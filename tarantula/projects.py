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
                       ["-lm"]),
    "tcas": Project("tcas",
                    os.path.join("testplans.alt", "universe"),
                    "inputs",
                    os.path.join("source.alt", "source.orig"),
                    os.path.join("versions.alt", "versions.orig"),
                    ["tcas.c"],
                    "tcas.c",
                    []),

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
        "v2": {294, 295, 296},
        "v3": {291, 292, 293},
        "v4": {92, 93},

        # Manually changed this one to put buggy statement on a separate line
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
        "v2": {85},
        "v3": {75},
        "v4": {233},
        "v5": {105},
        # V6's bug is strange. It is the incorrect value of of a #define
        # We're saying the buggy lines are the lines which use that macro.
        "v6": {55},

        "v7": {378},
        "v8": {201},
        "v9": {106},

        # V10's bug is also strange. It's change the type of something
        # from double to float.
        # We're defining the buggy lines to be the lines which use this
        # variable
        "v10": {330, 349, 352, 372},
        "v11": {198},
        "v12": {177},
        "v13": {394},
        "v14": {75},
        "v15": {200},
        "v16": {99},
        "v17": {223},
        "v18": {308},

        # v19 is the same bug as v6
        "v19": {55},

        "v20": {308},
        
        # v21 is similar bug to v19 and v6
        # Anywhere which uses this macro is considered buggy
        "v21": {75},
        "v22": {352},
        "v23": {215},
    },

    "replace": {
        "v1": {107},

        # This contains missing code, so we say the buggy
        # line is the one right before/after the missing line
        "v2": {105, 108},
        "v3": {494},
        "v4": {494},
        "v5": {118},
        "v6": {315, 318, 319},
        "v7": {176},
        "v8": {176},

        # This version contains a weird bug which I believe causes integer
        # overflow, so gcov reports that the file is corrupted
        #"v9": {115},
        "v10": {115},
        "v11": {116},
        "v12": {142, 145, 147, 148, 167, 206, 208, 210,
                226, 228, 234, 272, 275, 282},

        "v13": {500, 501, 502, 503},
        "v14": {370},
        "v15": {241},
        "v16": {176},
        "v17": {75},
        "v18": {372},

        # # This one has some weird differences
        # It relies on unitialized memory (line 515)
        # It also changes a constant (calls fgets with a different argument)
        "v19": {515, 44},

        "v20": {75},

        # # This one has multiple bugs
        # "v21": {44, 209, 55,
                
        #         # Any line which includes "MAXPAT" (a macro changed)
        #         # is considered buggy
        #     }
        
        # # This one has a strange difference as well
        # "v22": {140, 141, 144},
        # "v23": {74},
        # "v24": {362},
        # "v25": {362},
        # "v26": {370},
        
        ## Fails from segfault, apparently
        ## "v27": {182},
        # "v28": {176},
        # "v29": {176},
        # "v30": {176},
        # "v31": {370},

        ## Fails from segfault, apparently
        ## "v32": {115}
    },

    "tcas": {
        "v1": {75},
        "v2": {63},
        "v3": {120},
        "v4": {79},
        "v5": {118},
        "v6": {104},
        "v7": {51},
        "v8": {53},
        "v9": {89},
        "v10": {105, 111},
        "v11": {106, 113, 140, 136},
        "v12": {118},
        
        # Bug is a macro was changed, so buggy line is everywhere
        # the macro is used
        "v13": {118},
        "v14": {118},
    }
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

def get_siemens_projects():
    return ["schedule2", "totinfo", "replace", "tcas"]

def get_version_names(projectname):
    return sorted(PROJECT_TO_BUGGY_LINES[projectname].keys())
