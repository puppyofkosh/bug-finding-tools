import os

class Project(object):
    def __init__(self, name,
                 test_file, input_dir,
                 working_src_dir,
                 buggy_src_dir,
                 src_files,
                 main_src_file):
        self.name = name
        self.test_file = test_file
        self.input_dir = input_dir
        self.working_src_dir = working_src_dir
        self.buggy_src_dir = buggy_src_dir
        self.src_files = src_files
        self.main_src_file = main_src_file

PROJECT_TO_FILENAME = {
    "replace": Project("replace",
                       os.path.join("testplans.alt", "universe"),
                       "inputs",
                       os.path.join("source.alt", "source.orig"),
                       os.path.join("versions.alt",
                                    "versions.orig", "v1"),
                       ["replace.c"],
                       "replace.c"),

    "schedule2": Project("schedule2",
                         os.path.join("testplans.alt", "universe"),
                         "inputs",
                         os.path.join("source.alt", "source.orig"),
                         os.path.join("versions.alt",
                                      "versions.orig", "v1"),
                         ["schedule2.c", "schedule2.h"],
                         "schedule2.c"),
}

def get_project(projectname):
    return PROJECT_TO_FILENAME.get(projectname, None)