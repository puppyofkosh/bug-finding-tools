#! /bin/bash

javac -g *.java
# nohierarchy means to process calls who get entered, but not exited (maybe due to an exception)
java daikon.Chicory --daikon-args='--nohierarchy --no_text_output' --daikon $1
java daikon.PrintInvariants $1.inv.gz > $2
