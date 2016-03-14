import os
import sys
import subprocess
import shutil

import spectra
from commandio import get_output

def run_gcov(filename):
    retcode = subprocess.call(["gcov", filename])
    return retcode == 0

def reset_gcov_counts(filepath):
    filename, extension = os.path.splitext(filepath)
    assert extension == ".c"

    # Remove the data file 
    os.remove(filename + ".gcda")


def parse_gcov_output():
    pass

def get_execution_counts(filename):
    pass
