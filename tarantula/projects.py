import os

class Project(object):
    def set_bug_version(self, version):
        self.buggy_src_dir = os.path.join(self.buggy_src_dir, version)

    def get_all_files(self):
        files = [self.test_file, self.input_dir,
                self.working_src_dir, self.buggy_src_dir]

        for s in list(self.src_files) + [self.main_src_file]:
            files.append(os.path.join(self.working_src_dir, s))
            files.append(os.path.join(self.buggy_src_dir, s))
        return files

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
    "paper-example-mid": Project("paper-example-mid",
                                 "test.txt",
                                 "inputs",
                                 "working", "buggy",
                                 ["mid.c"],
                                 "mid.c"),
    "replace": Project("replace",
                       os.path.join("testplans.alt", "universe"),
                       "inputs",
                       os.path.join("source.alt", "source.orig"),
                       os.path.join("versions.alt",
                                    "versions.orig"),
                       ["replace.c"],
                       "replace.c"),

    "schedule2": Project("schedule2",
                         os.path.join("testplans.alt", "universe"),
                         "inputs",
                         os.path.join("source.alt", "source.orig"),
                         os.path.join("versions.alt",
                                      "versions.orig"),
                         ["schedule2.c", "schedule2.h"],
                         "schedule2.c"),
}

def get_project(projectname, version):
    project = PROJECT_TO_FILENAME.get(projectname, None)
    project.set_bug_version(version)
    return project
