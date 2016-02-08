#! /bin/bash

javac -g *.java
# nohierarchy means to process calls who get entered, but not exited (maybe due to an exception)
java daikon.Chicory --daikon-args='--no_text_output --config=../config.txt' --daikon $1
java daikon.PrintInvariants $1.inv.gz > $2
