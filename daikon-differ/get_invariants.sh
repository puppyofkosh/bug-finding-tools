#! /bin/bash

cd $1
javac -g Main.java
if [ $? -ne 0 ]; then
    exit 1
fi



main_class=Main
command="java daikon.Chicory --daikon-args='--no_text_output --config=../config.txt' --daikon $main_class"
print_invariants="java daikon.PrintInvariants --format java $main_class.inv.gz"
# First run the program with just passing test cases (pass in "pass")
# nohierarchy means to process calls who get entered, but not exited (maybe due to an exception)
eval $command pass
eval $print_invariants > pass_invariants

# Now run the program with both passing and testing cases (pass in "fail")
eval $command both
eval $print_invariants > fail_invariants
