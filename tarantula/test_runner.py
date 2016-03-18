# This module will take in a project (which is a bunch of info about
# where code is stored) and produce spectra for each run of the buggy
# program on each test, as well as which tests passed/failed
#


import os
import sys
import subprocess
import shutil
import pickle
import pandas as pd
import argparse

import spectra
import gcov_helper
from commandio import get_output

import projects

BUGGY_DIR = "buggy-version"
WORKING_DIR = "working-version"

WORKING_RUNNABLE = "working.out"
BUGGY_RUNNABLE = "buggy.out"

GCC_ARGS = ["-std=c99"]
GCC_INSTRUMENTATION_ARGS = ["-fprofile-arcs", "-ftest-coverage"]

RUN_RESULT_FILE = "runs.pickle"

def check_current_directory(project):
    for e in project.get_all_files():
        if not os.path.exists(e):
            return "{0} doesn't exist".format(e)
    return None


def initialize_directory(project):
    # Make sure correct dirs are there
    err = check_current_directory(project)
    if err is not None:
        return err

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

    return None


def run_gcc(args, infile, outfile):
    extra_args = [infile, "-o", outfile]
    retcode = subprocess.call(["gcc"] + args + extra_args,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    return retcode


def compile_working_version(working_src_dir, main_src_file, src_files):
    for f in src_files:
        shutil.copy(os.path.join(working_src_dir, f),
                    os.path.join(WORKING_DIR, f))
    os.chdir(WORKING_DIR)
    retcode = run_gcc(GCC_ARGS, main_src_file, WORKING_RUNNABLE)

    if retcode != 0:
        os.chdir("..")
        raise RuntimeError("Could not compile working version")

    os.chdir("..")
    return True
    

def compile_buggy_version(buggy_src_dir, main_src_file, src_files):
    # Compile the incorrect one, this time with coverage
    for f in src_files:
        shutil.copy(os.path.join(buggy_src_dir, f),
                    f)

    retcode = run_gcc(GCC_ARGS + GCC_INSTRUMENTATION_ARGS,
                      main_src_file, BUGGY_RUNNABLE)
    if retcode != 0:
        print "Error compiling buggy version"
        return False

    return True


def get_tests(testfile):
    test_lines = []
    with open(testfile, 'r') as fd:
        test_lines += fd.readlines()

    test_lines = [l.strip() for l in test_lines]
    return test_lines


def get_spectra(src_filename,
                buggy_program, correct_program,
                testfile):
    test_lines = get_tests(testfile)

    passcount = 0
    run_to_result = {}
    for i, test in enumerate(test_lines):
        if i % 100 == 0:
            print "Running test {0}".format(i)

        prog_output = get_output(buggy_program + " " + test, True)
        expected_output = get_output(correct_program + " " +  test, True)

        passed = prog_output == expected_output
        if not passed:
            print "Failed following test({0}): {1}".format(i, test)
        else:
            passcount += 1

        trace = gcov_helper.get_trace(src_filename)
        gcov_helper.reset_gcov_counts(src_filename)

        spectrum = spectra.make_spectrum_from_trace(trace)

        run_to_result[i] = (passed, spectrum)

    print "Passed {0}/{1}".format(passcount, len(test_lines))
    return run_to_result


def get_test_results(projectdir, project):
    original_dir = os.getcwd()

    os.chdir(projectdir)
    err = initialize_directory(project)
    if err is not None:
        print err
        return

    # Copy the buggy source into our current dir. We need to be in the same dir
    # as we compiled to run gcov, and if we try to keep the buggy version in
    # its own directory, we'll have to call chdir() over and over
    compile_working_version(project.working_src_dir, project.main_src_file,
                            project.src_files)

    compile_buggy_version(project.buggy_src_dir, project.main_src_file,
                          project.src_files)

    run_to_result = get_spectra(project.main_src_file,
                                os.path.join(".", BUGGY_RUNNABLE),
                                os.path.join(WORKING_DIR, WORKING_RUNNABLE),
                                project.test_file)

    # Write the information about the runs to the file
    # This consists of 1) did the case pass, and 2) which lines executed
    os.chdir(original_dir)

    return run_to_result
    #with open(RUN_RESULT_FILE, "w") as fd:
    #pickle.dump(run_to_result, fd)

