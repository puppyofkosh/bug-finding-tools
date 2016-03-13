#! /bin/python

import os
import sys
import subprocess
import shutil


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


def get_output(command):
    proc = subprocess.Popen(command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True)
    stdout, stderr = proc.communicate()

    if len(stderr) > 0:
        print "{0}".format(command)
        print stderr
        raise RuntimeError("Why did it write to stderr?")
    return stdout


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
    return None


def run_gcc(args, infile, outfile):
    extra_args = [infile, "-o {0}".format(outfile)]
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

    # They both been compiled now.

    return None


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

    return

    test_file = TEST_FILE

    lines = []
    with open(test_file, 'r') as fd:
        lines += fd.readlines()

    lines = [l.strip() for l in lines]

    passcount = 0
    for i, test in enumerate(lines):
        prog_output = get_output(program + " " + test)
        expected_output = get_output(correct_program + " " + test)

        if prog_output != expected_output:
            print "Failed following test({0}): {1}".format(i, test)
        else:
            passcount += 1

    print "Passed {0}/{1}".format(passcount, len(lines))

if __name__ == "__main__":
    main()
