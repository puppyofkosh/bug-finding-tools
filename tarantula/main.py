#! /bin/python

import os
import sys
import pandas as pd

import projects
import test_runner
import tarantula
import evaluator
import spectra_filter
import run_result

SPECTRA_DIR = "spectra"
def get_spectra_file(project_name, version):
    return os.path.join(SPECTRA_DIR,
                        project_name + "-" + version + ".res")


def make_spectra(project_name, projectdir, versions):
    versions = list(versions)
    assert len(versions) > 0
    original_dir = os.getcwd()

    os.chdir(projectdir)
    project = projects.get_project(project_name, versions[0])
    test_runner.initialize_directory(project)
    runner = test_runner.TestRunner(project)

    runner.load_correct_outputs()

    for v in versions:
        print("Running version {0}".format(v))
        project = projects.get_project(project_name, v)
        runner.set_project(project)

        run_to_result = runner.get_buggy_version_results()
        os.chdir(original_dir)

        if not os.path.exists(SPECTRA_DIR):
            os.mkdir(SPECTRA_DIR)

        outfile = get_spectra_file(project.name, project.version)
        print("Saving results to {0}".format(outfile))
        run_result.save(outfile, run_to_result)
        os.chdir(projectdir)


def get_tarantula_output(project_name, version, use_filter):
    run_to_result = run_result.load(get_spectra_file(project_name, version))

    filter_fn = spectra_filter.filter_spectra
    if not use_filter:
        filter_fn = spectra_filter.trivial_filter

    passing_spectra, failing_spectra = filter_fn(run_to_result)

    ranks, suspiciousness = tarantula.get_suspicious_lines(passing_spectra,
                                                           failing_spectra)

    buggy_lines = projects.get_known_buggy_lines(project_name,
                                                 version)
    if buggy_lines is None:
        print("Buggy lines aren't known for version {0}".format(version))
        return ranks, suspiciousness, None, None

    line, score = evaluator.get_score(ranks, buggy_lines)

    return (ranks, suspiciousness, line, score)


def print_tarantula_result(project_name, version, use_filter):
    (ranks, suspiciousness, line, score) = get_tarantula_output(project_name,
                                                                version,
                                                                use_filter)
    results = pd.DataFrame(data={'rank': ranks, 'susp': suspiciousness})
    results.sort_values('rank', inplace=True)
    print(results)
    print("line {0}: score {1}".format(line, score))


def get_total_scores(project_name, use_filter):
    version_to_score = {}
    for version in projects.get_version_names(project_name):
        _, __, ___, score = get_tarantula_output(project_name, version, use_filter)
        version_to_score[version] = score
    
    version_to_score = pd.Series(version_to_score)
    version_to_score.sort_values(inplace=True, ascending=False)
    print("Average score is {0}".format(version_to_score.mean()))
    print(version_to_score)
    

def main():
    if len(sys.argv) < 3:
        print("usage: {0} projectname command ...".format(sys.argv[0]))
        print("Valid projects are: {0}".format({}))

    project_name = sys.argv[1]
    command = sys.argv[2]
    args = sys.argv[3:]
    if command == "make-all-spectra":
        if len(args) < 1:
            print("Usage: make-all-spectra project-dir")
            return

        project_dir = args[0]
        make_spectra(project_name, project_dir,
                     projects.get_version_names(project_name))
    elif command == "make-spectra":
        if len(args) < 2:
            print("Usage: make-spectra project-dir version")
            return

        project_dir = args[0]
        version = args[1]
        make_spectra(project_name, project_dir, [version])
    elif command == "find-bugs":
        if len(args) < 2:
            print("Usage: find-bugs version filter|nofilter")
            return
        version = args[0]
        use_filter = args[1] == "filter"

        print_tarantula_result(project_name, version, use_filter)
    elif command == "evaluate-all":
        if len(args) < 1:
            print("Usage evaluate-all filter|nofilter")
            return
        use_filter = args[0] == "filter"
        get_total_scores(project_name, use_filter)
    else:
        print("invalid command")
        return


if __name__ == "__main__":
    main()
