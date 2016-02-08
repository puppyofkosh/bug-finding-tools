#! /bin/bash

javac -g src/*.java
java -cp "../../../daikon.jar:." daikon.Chicory --daikon src.StackArTester

