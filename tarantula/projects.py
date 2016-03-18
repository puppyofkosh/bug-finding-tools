import os
import copy


class Project(object):

    def set_bug_version(self, version):
        self.version = version
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
                 main_src_file,
                 additional_gcc_flags=None):
        self.version = None
        self.name = name
        self.test_file = test_file
        self.input_dir = input_dir
        self.working_src_dir = working_src_dir
        self.buggy_src_dir = buggy_src_dir
        self.src_files = src_files
        assert main_src_file in src_files
        self.main_src_file = main_src_file
        if additional_gcc_flags is None:
            additional_gcc_flags = []
        self.additional_gcc_flags = additional_gcc_flags

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
                       os.path.join("versions.alt", "versions.orig"),
                       ["replace.c"],
                       "replace.c"),

    "schedule2": Project("schedule2",
                         os.path.join("testplans.alt", "universe"),
                         "inputs",
                         os.path.join("source.alt", "source.orig"),
                         os.path.join("versions.alt", "versions.orig"),
                         ["schedule2.c", "schedule2.h"],
                         "schedule2.c"),

    "totinfo": Project("totinfo",
                       os.path.join("testplans.alt", "universe"),
                       "inputs",
                       os.path.join("source.alt", "source.orig"),
                       os.path.join("versions.alt", "versions.orig"),
                       ["tot_info.c", "std.h", "gamma.h", "chisq.h"],
                       "tot_info.c",
                       # Must link with math library to use sin/cos/log functions
                       ["-lm"])

}

PROJECT_TO_BUGGY_LINES = {
    "paper-example-mid": {
        "v1": {10}
    },

    # If the bug is missing code, then we say the lines with the bugs are either
    # the line before or the line after, as long as they're in the same basic block
    # (guaranteed to execute iff the correct version without missing code is also
    # guaranteed to execute)
    "schedule2": {
        "v1": {134, 135, 136},
        # Line 297 is iffy as to whether it should get counted
        # FIXME: Ask about best way of evaluating how well tarantula does when
        # there is missing code
        "v2": {294, 295, 296} | {297},
        "v3": {291, 292, 293} | {297},
        "v4": {92, 93},
        "v5": {111} | {112},
        "v6": {77},
        "v7": {292},

        # v8 segfaults, so we don't include it
        #"v8": {277, 278},

        # v9 doesn't fail any tests, so we don't include it
        #"v9": {187},

        "v10": {28, 29}
    },

    "totinfo": {
        "v1": {342},
    },
}


def get_known_buggy_lines(project_name, version):
    if project_name in PROJECT_TO_BUGGY_LINES:
        known_buggy_lines = PROJECT_TO_BUGGY_LINES[project_name]
        if version in known_buggy_lines:
            return known_buggy_lines[version]
    return None


def get_project(projectname, version):
    project = PROJECT_TO_FILENAME.get(projectname, None)
    
    # We return a copied object because we don't want to change the fields
    # (like version and stuff) of the global one
    project = copy.deepcopy(project)
    project.set_bug_version(version)
    return project


def get_projects():
    return PROJECT_TO_FILENAME.keys()


def get_version_names(projectname):
    return PROJECT_TO_BUGGY_LINES[projectname].keys()
