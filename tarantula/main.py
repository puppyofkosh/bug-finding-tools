#! /bin/python

import os
import sys
import pandas as pd
import pickle

import projects
import test_runner
import tarantula
import evaluator

SPECTRA_DIR = "spectra"


def get_spectra_file(project_name, version):
    return os.path.join(SPECTRA_DIR,
                        project_name + "-" + version + ".res")


def make_spectra(project, projectdir):
    run_to_result = test_runner.get_test_results(projectdir, project)

    if not os.path.exists(SPECTRA_DIR):
        os.mkdir(SPECTRA_DIR)

    outfile = get_spectra_file(project.name, project.version)
    print "Saving results to {0}".format(outfile)
    with open(outfile, "w") as fd:
        pickle.dump(run_to_result, fd)


def find_bugs(project_name, version):
    run_to_result = {}
    with open(get_spectra_file(project_name, version), "r") as fd:
        run_to_result = pickle.load(fd)

    ranks, suspiciousness = tarantula.get_suspicious_lines(run_to_result)
    results = pd.DataFrame(data={'rank': ranks, 'susp': suspiciousness})
    results.sort_values('rank', inplace=True)
    print results

    interesting_keys = projects.get_known_buggy_lines(project_name,
                                                      version)
    if interesting_keys is None:
        interesting_keys = [134, 135, 136]

    line, score = evaluator.get_score(ranks, interesting_keys)
    print "line {0}: score {1}".format(line, score)
    for k in interesting_keys:
        print "line {0}: susp {1}".format(k, suspiciousness.get(k, None))


def main():
    if len(sys.argv) < 3:
        print "usage: {0} projectname command ...".format(sys.argv[0])
        print "Valid projects are: {0}".format({})

    project_name = sys.argv[1]
    command = sys.argv[2]
    args = sys.argv[3:]
    if command == "make-all-spectra":
        if len(args) < 1:
            print "Usage: make-all-spectra project-dir"
            return

        project_dir = args[0]
        for v in projects.get_version_names(project_name):
            project = projects.get_project(project_name, v)
            make_spectra(project, project_dir)
    elif command == "make-spectra":
        if len(args) < 2:
            print "Usage: make-spectra project-dir version"
            return

        project_dir = args[0]
        version = args[1]

        project = projects.get_project(project_name, version)
        if project is None:
            print "Unkown project {0}".format(project_name)
            return
        make_spectra(project, project_dir)
    elif command == "find-bugs":
        if len(args) < 1:
            print "Usage: find-bugs version"
            return
        version = args[0]
        find_bugs(project_name, version)
    else:
        print "invalid command"
        return


if __name__ == "__main__":
    main()
