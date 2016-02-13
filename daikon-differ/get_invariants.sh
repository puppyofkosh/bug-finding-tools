#! /bin/bash

cd $1
javac -g *.java

main_class=Main
command="java daikon.Chicory --daikon-args='--no_text_output --config=../config.txt' --daikon $main_class"
print_invariants="java daikon.PrintInvariants $main_class.inv.gz"
# First run the program with just passing test cases (pass in "pass")
# nohierarchy means to process calls who get entered, but not exited (maybe due to an exception)
eval $command pass
eval $print_invariants > pass_invariants

# Now run the program with both passing and testing cases (pass in "fail")
eval $command both
eval $print_invariants > fail_invariants
