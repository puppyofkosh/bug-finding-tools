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


def get_tarantula_output(project_name, version):
    run_to_result = {}
    with open(get_spectra_file(project_name, version), "r") as fd:
        run_to_result = pickle.load(fd)

    ranks, suspiciousness = tarantula.get_suspicious_lines(run_to_result)

    buggy_lines = projects.get_known_buggy_lines(project_name,
                                                 version)
    if buggy_lines is None:
        print "Buggy lines aren't known for version {0}".format(version)
        return ranks, suspiciousness, None, None

    line, score = evaluator.get_score(ranks, buggy_lines)

    return (ranks, suspiciousness, line, score)


def print_tarantula_result(project_name, version):
    (ranks, suspiciousness, line, score) = get_tarantula_output(project_name,
                                                              version)
    results = pd.DataFrame(data={'rank': ranks, 'susp': suspiciousness})
    results.sort_values('rank', inplace=True)
    print results
    print "line {0}: score {1}".format(line, score)


def get_total_scores(project_name):
    version_to_score = {}
    for version in projects.get_version_names(project_name):
        _, __, ___, score = get_tarantula_output(project_name, version)
        version_to_score[version] = score
    
    version_to_score = pd.Series(version_to_score)
    version_to_score.sort_values(inplace=True, ascending=False)
    print "Average score is {0}".format(version_to_score.mean())
    print version_to_score
    

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
            print "Generating spectra for version {0}".format(v)
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
        print_tarantula_result(project_name, version)
    elif command == "evaluate-all":
        get_total_scores(project_name)
    else:
        print "invalid command"
        return


if __name__ == "__main__":
    main()
