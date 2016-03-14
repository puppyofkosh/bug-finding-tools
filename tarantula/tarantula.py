#! /bin/python

import os
import sys
import subprocess
import shutil

import spectra
from commandio import get_output

BUGGY_DIR = "buggy-version"
WORKING_DIR = "working-version"

WORKING_SOURCE_DIR = os.path.join("source.alt", "source.orig")
BUGGY_SOURCE_DIR = os.path.join("versions.alt", "versions.orig", "v1")

WORKING_RUNNABLE = "working.out"
BUGGY_RUNNABLE = "buggy.out"

PROJECT_TO_FILENAME = {
    "replace": "replace.c"
}

GCC_ARGS = ["-std=c99"]
GCC_INSTRUMENTATION_ARGS = ["-fprofile-arcs", "-ftest-coverage"]

TEST_FILE = os.path.join("testplans.alt", "universe")
INPUT_DIR = "inputs"

def check_current_directory():
    expected_dirs = ["versions.alt",
                     "versions",
                     "source.alt",
                     os.path.join("source.alt", "source.orig"),
                     "testplans.alt"]

    for e in expected_dirs:
        if not os.path.exists(e):
            return "{0} doesn't exist".format(e)
    return None


def initialize_directory():
    # Make sure correct dirs are there
    err = check_current_directory()
    if err is not None:
        return err

    if not os.path.exists(BUGGY_DIR):
        os.makedirs(BUGGY_DIR)
    if not os.path.exists(WORKING_DIR):
        os.makedirs(WORKING_DIR)

    # Create a symlink to each of the subfolders in test/ in the current dir
    for d in os.listdir(INPUT_DIR):
        target_name = os.path.join(INPUT_DIR, d)
        link_name = os.path.basename(os.path.normpath(d))
        os.symlink(target_name, link_name)

    return None


def run_gcc(args, infile, outfile):
    extra_args = [infile, "-o", outfile]
    retcode = subprocess.call(["gcc"] + args + extra_args,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    return retcode


def compile_versions(filename, working_src_dir, buggy_src_dir):
    shutil.copy(os.path.join(working_src_dir, filename),
                os.path.join(WORKING_DIR, filename))
    os.chdir(WORKING_DIR)
    retcode = run_gcc(GCC_ARGS, filename, WORKING_RUNNABLE)

    if retcode != 0:
        print "Error compiling working version"
        return False

    os.chdir("..")

    # Compile the incorrect one, this time with coverage
    shutil.copy(os.path.join(buggy_src_dir, filename),
                os.path.join(BUGGY_DIR, filename))
    os.chdir(BUGGY_DIR)
    retcode = run_gcc(GCC_ARGS + GCC_INSTRUMENTATION_ARGS,
                      filename, BUGGY_RUNNABLE)
    if retcode != 0:
        print "Error compiling buggy version"
        return False

    os.chdir("..")
    # They both been compiled now.

    return None


def get_tests(testfile):
    test_lines = []
    with open(testfile, 'r') as fd:
        test_lines += fd.readlines()

    test_lines = [l.strip() for l in test_lines]
    return test_lines


def get_spectra(buggy_program, correct_program, testfile):
    test_lines = get_tests(testfile)

    passcount = 0
    run_to_result = {}
    for i, test in enumerate(test_lines):
        prog_output = get_output(buggy_program + " " + test)
        expected_output = get_output(correct_program + " " + test)

        passed = prog_output == expected_output
        if not passed:
            print "Failed following test({0}): {1}".format(i, test)
        else:
            passcount += 1

        run_to_result[i] = passed

    print "Passed {0}/{1}".format(passcount, len(test_lines))
    return run_to_result


def main():
    if len(sys.argv) < 2:
        print "usage: {0} program-directory project".format(sys.argv[0])
        print "Valid projects are: {0}".format(PROJECT_TO_FILENAME.keys())
        return

    projectdir = sys.argv[1]
    project_name = sys.argv[2]

    if project_name not in PROJECT_TO_FILENAME:
        print "Unkown project {0}".format(project_name)
        return

    os.chdir(projectdir)
    err = initialize_directory()
    if err is not None:
        print err
        return

    compile_versions(PROJECT_TO_FILENAME[project_name],
                     WORKING_SOURCE_DIR,
                     BUGGY_SOURCE_DIR)

    run_to_result = get_spectra(os.path.join(BUGGY_DIR, BUGGY_RUNNABLE),
                                os.path.join(WORKING_DIR, WORKING_RUNNABLE),
                                TEST_FILE)

    print "{0}".format({k: v for k, v in
                        run_to_result.iteritems() if v == False})

    return

if __name__ == "__main__":
    main()
