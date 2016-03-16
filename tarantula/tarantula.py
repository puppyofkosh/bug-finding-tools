#! /bin/python

import os
import sys
import subprocess
import shutil
import pickle
import pandas as pd

import spectra
import gcov_helper
from commandio import get_output

from projects import get_project

BUGGY_DIR = "buggy-version"
WORKING_DIR = "working-version"

WORKING_RUNNABLE = "working.out"
BUGGY_RUNNABLE = "buggy.out"

PROJECT_TO_FILENAME = {
    "replace": "replace.c"
}

GCC_ARGS = ["-std=c99"]
GCC_INSTRUMENTATION_ARGS = ["-fprofile-arcs", "-ftest-coverage"]

RUN_RESULT_FILE = "runs.pickle"

def check_current_directory():
    expected_dirs = ["versions.alt",
                     "source.alt",
                     os.path.join("source.alt", "source.orig"),
                     "testplans.alt"]

    for e in expected_dirs:
        if not os.path.exists(e):
            return "{0} doesn't exist".format(e)
    return None


def initialize_directory(project):
    # Make sure correct dirs are there
    err = check_current_directory()
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


def get_spectra(src_filename, buggy_program, correct_program, testfile):
    test_lines = get_tests(testfile)

    passcount = 0
    run_to_result = {}
    test_lines = test_lines[:15]
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


def get_traces(projectdir, project):
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
    with open(RUN_RESULT_FILE, "w") as fd:
        pickle.dump(run_to_result, fd)


def analyze_runs():
    run_to_result = {}
    with open(RUN_RESULT_FILE, "r") as fd:
        run_to_result = pickle.load(fd)
    
    # Count how many times each line was executed in a failing or
    # successful test
    failing_counts = pd.Series()
    passing_counts = pd.Series()
    
    total_passed = 0
    total_failed = 0

    for passing, spectrum in run_to_result.values():
        ser = pd.Series(spectrum)
        assert not ser.isnull().values.any()
        if passing:
            total_passed += 1
            passing_counts = passing_counts.add(ser, fill_value=0)
        else:
            total_failed += 1
            failing_counts = failing_counts.add(ser, fill_value=0)

    assert total_failed > 0 and total_passed > 0
    assert not passing_counts.isnull().values.any()
    assert not failing_counts.isnull().values.any()

    # Now we get the suspiciousness of each line
    failing_counts /= float(total_failed)
    passing_counts /= float(total_passed)

    denom = failing_counts.add(passing_counts, fill_value=0)
    suspiciousness = failing_counts.mul(1.0 / denom, fill_value=0)
    suspiciousness.sort_values(inplace=True)
    return suspiciousness

def main():
    if len(sys.argv) < 2:
        print "usage: {0} program-directory project".format(sys.argv[0])
        print "Valid projects are: {0}".format(PROJECT_TO_FILENAME.keys())
        return

    projectdir = sys.argv[1]
    project_name = sys.argv[2]

    project = get_project(project_name)
    if project is None:
        print "Unkown project {0}".format(project_name)
        return

    if "make-spectra" in sys.argv:
        print projectdir
        get_traces(projectdir, project)
    elif "analyze-spectra" in sys.argv:
        suspiciousness = analyze_runs()
        print suspiciousness

        if 111 in suspiciousness:
            print suspiciousness[111]

        if 105 in suspiciousness:
            print suspiciousness[105]
            

if __name__ == "__main__":
    main()
