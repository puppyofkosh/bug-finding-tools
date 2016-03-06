#! /bin/python

import os
import sys
from subprocess import call

PASS_ARG = "pass"
FAIL_ARG = "both"

# Don't generate invaraints about stuff we don't care about
CLASSES_TO_OMIT = ["^org.junit\\.",
                   "^junit\\.",
                   "^com.sun.proxy\\."]


PROJECTS = {
    "lang": {
        "classpath": "target/tests:target/classes:" +
        "$CLASSPATH:/usr/share/java/hamcrest-core.jar",
        "classes_to_include": []
    },

    "closure": {
        "classpath": "build/test:build/classes:build/lib/*:lib/*:$CLASSPATH",
        "classes_to_include": ["__Invariant$", ]
    }

}

LANG_CLASSPATH = "target/tests:target/classes:$CLASSPATH:" +\
                 "/usr/share/java/hamcrest-core.jar"


CLOSURE_CLASSPATH = "build/test:build/classes:build/lib/*:lib/*:$CLASSPATH"
CLOSURE_CLASSES_TO_INCLUDE = ["__Invariant$", ]


def get_omit_args(to_omit):
    s = ""
    for o in to_omit:
        s += "--ppt-omit-pattern='{0}' ".format(o)
    return s


def get_include_args(to_include):
    s = ""
    for o in to_include:
        s += "--ppt-select-pattern='{0}' ".format(o)
    return s


def get_project(projectname):
    name = projectname.split("_")[0].lower()

    if name not in PROJECTS:
        print "{0} doesn't start with one of {1}".format(name,
                                                         PROJECTS.keys())
        raise RuntimeError("Unkown project")

    return PROJECTS[name]


def main():
    if len(sys.argv) < 3:
        print "usage: {0} directoryname fullclasspathtorun [nodaikon]"\
            .format(sys.argv[0])
        print "[nodaikon]: if you just want to run the class without daikon"
        return

    project_name = sys.argv[1]
    full_classname = sys.argv[2]
    file_name = full_classname.split('.')[-1]
    nodaikon = "nodaikon" in sys.argv

    project_obj = get_project(project_name)

    os.chdir(project_name)
    return_code = call("defects4j compile", shell=True)
    if return_code != 0:
        print "couldn't compile"
        return

    if nodaikon:
        command = "java -cp {0} {1} {2}".format(project_obj["classpath"],
                                                full_classname, FAIL_ARG)
        call(command, shell=True)
        return

    daikon_args = "--no_text_output --config=../config.txt"

    # Omit invariants about junit internal stuff,
    # As well as invariants about the test cases (we want invariants about the
    # actual program)
    to_omit = CLASSES_TO_OMIT + [full_classname]
    to_include = project_obj["classes_to_include"]
    chicory_args = get_omit_args(to_omit) + " " + get_include_args(to_include)
    command = "java -cp {0} daikon.Chicory {1} --daikon-args='{2}' --daikon {3}"\
        .format(project_obj["classpath"],
                chicory_args, daikon_args, full_classname)

    print_invariants = "java daikon.PrintInvariants --format java {0}.inv.gz".\
                       format(file_name)

    if "failonly" not in sys.argv:
        print command
        if 0 != call(command + " " + PASS_ARG, shell=True):
            print "Couldn't run passing version"
            return

        call(print_invariants + " > pass_invariants", shell=True)

    if "passonly" not in sys.argv:
        if 0 != call(command + " " + FAIL_ARG, shell=True):
            print "Failing version crashed"
            return
        call(print_invariants + " > fail_invariants", shell=True)


if __name__ == "__main__":
    main()
