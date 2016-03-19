# This module will take in a project (which is a bunch of info about
# where code is stored) and produce spectra for each run of the buggy
# program on each test, as well as which tests passed/failed
#


import os
import subprocess
import shutil

import spectra
import gcov_helper
from commandio import get_output
from run_result import RunResult

BUGGY_DIR = "buggy-version"
WORKING_DIR = "working-version"

WORKING_RUNNABLE = "working.out"
BUGGY_RUNNABLE = "buggy.out"

GCC_ARGS = ["-std=c99"]
GCC_INSTRUMENTATION_ARGS = ["-fprofile-arcs", "-ftest-coverage"]

# A TestRunner will run the correct program on all the test inputs and
# store the results. Then, you can request to run it on a buggy
# program to get which tests fail
class TestRunner(object):
    def __init__(self, project):
        self._project = project
        self._correct_outputs = None
        

    def load_correct_outputs(self):
        assert self._correct_outputs is None

        # Copy the buggy source into our current dir. We need to be in the same dir
        # as we compiled to run gcov, and if we try to keep the buggy version in
        # its own directory, we'll have to call chdir() over and over
        working_runnable = compile_working_version(self._project)
        
        # FIXME: make get_tests lazily get the tests
        test_lines = get_tests(self._project.test_file)
        self._correct_outputs = []
        for i, test in enumerate(test_lines):
            if i % 500 == 0:
                print "Running correct version on test {0}".format(i)

            expected_output = get_output(working_runnable + " " +  test, True)
            self._correct_outputs.append(expected_output)

    def set_project(self, project):
        """Switch project so we can run a different buggy version"""
        assert project.name == self._project.name
        self._project = project

    def get_buggy_version_results(self):
        buggy_program = compile_buggy_version(self._project)

        test_lines = get_tests(self._project.test_file)

        passcount = 0
        run_to_result = {}
        for i, test in enumerate(test_lines):
            if i % 500 == 0:
                print "Running buggy version test {0}".format(i)

            prog_output = get_output(buggy_program + " " + test, True)

            passed = prog_output == self._correct_outputs[i]
            if passed:
                passcount += 1

            trace = gcov_helper.get_trace(self._project.main_src_file)
            gcov_helper.reset_gcov_counts(self._project.main_src_file)

            spectrum = spectra.make_spectrum_from_trace(trace)

            run_to_result[i] = RunResult(passed=passed, spectrum=spectrum)

        print "Passed {0}/{1}".format(passcount, len(test_lines))
        return run_to_result
    

def check_current_directory(project):
    for e in project.get_all_files():
        if not os.path.exists(e):
            raise RuntimeError("{0} doesn't exist".format(e))

def initialize_directory(project):
    # Make sure correct dirs are there
    check_current_directory(project)

    if not os.path.exists(BUGGY_DIR):
        os.makedirs(BUGGY_DIR)
    if not os.path.exists(WORKING_DIR):
        os.makedirs(WORKING_DIR)

    # Create a symlink to each of the subfolders in test/ in the current dir
    for d in os.listdir(project.input_dir):
        target_name = os.path.join(project.input_dir, d)
        link_name = os.path.basename(os.path.normpath(d))

        if not os.path.exists(link_name):
            os.symlink(target_name, link_name)


def run_gcc(args, end_args, infile, outfile):
    extra_args = [infile, "-o", outfile]
    retcode = subprocess.call(["gcc"] + args + extra_args + end_args,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    return retcode


def compile_working_version(project):
    for f in project.src_files:
        shutil.copy(os.path.join(project.working_src_dir, f),
                    os.path.join(WORKING_DIR, f))
    os.chdir(WORKING_DIR)
    retcode = run_gcc(GCC_ARGS, project.additional_gcc_flags,
                      project.main_src_file,
                      WORKING_RUNNABLE)

    if retcode != 0:
        os.chdir("..")
        raise RuntimeError("Could not compile working version")

    os.chdir("..")
    return os.path.join(WORKING_DIR, WORKING_RUNNABLE)
    

def compile_buggy_version(project):
    # Compile the incorrect one, this time with coverage
    for f in project.src_files:
        shutil.copy(os.path.join(project.buggy_src_dir, f), f)

    retcode = run_gcc(GCC_ARGS + GCC_INSTRUMENTATION_ARGS,
                      project.additional_gcc_flags,
                      project.main_src_file, BUGGY_RUNNABLE)

    if retcode != 0:
        raise RuntimeError("Error compiling buggy version")

    return os.path.join(".", BUGGY_RUNNABLE)


def get_tests(testfile):
    test_lines = []
    with open(testfile, 'r') as fd:
        test_lines += fd.readlines()

    test_lines = [l.strip() for l in test_lines]
    return test_lines
