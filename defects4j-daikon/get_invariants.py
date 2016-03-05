#! /bin/python

import os
import sys
from subprocess import call


def main():
    if len(sys.argv) != 3:
        print "usage: {0} directoryname fullclasspathtorun".format(sys.argv[0])
        return

    project = sys.argv[1]
    full_classname = sys.argv[2]
    file_name = full_classname.split('.')[-1]

    os.chdir(project)
    return_code = call("defects4j compile", shell=True)
    if return_code != 0:
        print "couldn't compile"
        return

    classpath = "target/tests:target/classes:$CLASSPATH:/usr/share/java/hamcrest-core.jar"

    daikon_args = "--no_text_output --config=../config.txt"
    command = "java -cp {0} daikon.Chicory --daikon-args='{1}' --daikon {2}"\
        .format(classpath, daikon_args, full_classname)
    
    print_invariants = "java daikon.PrintInvariants --format java {0}.inv.gz".format(file_name)

    print command
    if 0 != call(command + " pass", shell=True):
        return

    call(print_invariants + " > pass_invariants", shell=True)
    # First run the program with just passing test cases (pass in "pass")
#eval $command both
#eval $print_invariants > fail_invariants



if __name__ == "__main__":
    main()
