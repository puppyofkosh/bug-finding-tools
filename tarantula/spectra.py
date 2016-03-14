import os
import sys
import subprocess
import shutil

from commandio import get_output

class RunResult(object):
    def __init__(self, passed, spectrum):
        self.passed = passed
        self.spectrum = spectrum

