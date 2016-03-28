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
import feature_computer

SPECTRA_DIR = "spectra"
def get_spectra_file(project_name, version):
    return os.path.join(SPECTRA_DIR,
                        project_name + "-" + version + ".res")

FEATURE_DIR = "features"
def get_feature_file(project_name, version):
    fname = project_name + "-" + version + ".feat"
    fname = os.path.join(FEATURE_DIR, fname)
    return fname


def make_spectra(project_name, projectdir, versions, remake):
    versions = list(versions)
    assert len(versions) > 0
    original_dir = os.getcwd()

    os.chdir(projectdir)
    project = projects.get_project(project_name, versions[0])
    test_runner.initialize_directory(project)
    runner = test_runner.TestRunner(project)

    runner.load_correct_outputs()
    os.chdir(original_dir)
    
    for v in versions:
        project = projects.get_project(project_name, v)
        outfile = get_spectra_file(project.name, project.version)

        exists = os.path.exists(outfile)
        if exists and not remake:
            print("Spectra already exists for {0}. Skipping".format(v))
            continue

        os.chdir(projectdir)
        print("Running version {0}".format(v))
        runner.set_project(project)

        run_to_result = runner.get_buggy_version_results()
        os.chdir(original_dir)

        if not os.path.exists(SPECTRA_DIR):
            os.mkdir(SPECTRA_DIR)

        outfile = get_spectra_file(project.name, project.version)
        print("Saving results to {0}".format(outfile))
        run_result.save(outfile, run_to_result)


def get_tarantula_output(project_name, version, use_filter):
    run_to_result = run_result.load(get_spectra_file(project_name, version))

    filter_fn = spectra_filter.trivial_filter
    features = None
    if use_filter:
        filter_fn = spectra_filter.filter_spectra
        feature_file = get_feature_file(project_name, version)
        features = feature_computer.load(feature_file)

    passing_spectra, failing_spectra = filter_fn(run_to_result, features)

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
        _, __, ___, score = get_tarantula_output(project_name,
                                                 version, use_filter)
        version_to_score[version] = score
    
    version_to_score = pd.Series(version_to_score)
    version_to_score.sort_values(inplace=True, ascending=False)
    return version_to_score

def print_total_scores(project_name, use_filter):
    version_to_score = get_total_scores(project_name, use_filter)
    print("Average score is {0}".format(version_to_score.mean()))
    print(version_to_score)

def compare_filter(project_name):
    nofilter_scores = get_total_scores(project_name, False)
    filter_scores = get_total_scores(project_name, True)

    results = pd.DataFrame({'nofilter': nofilter_scores,
                            'filter': filter_scores,
                            'diff': filter_scores - nofilter_scores})
    results.sort_values('diff', inplace=True)
    print(results)

def compute_features(project_name):
    if not os.path.exists(FEATURE_DIR):
        os.mkdir(FEATURE_DIR)

    for version in projects.get_version_names(project_name):
        fname = get_feature_file(project_name, version)
        if os.path.exists(fname):
            print("V {0} Already exists, skipping".format(version))
            continue

        print("Computing version {0}".format(version))
        spectra_file = get_spectra_file(project_name, version)
        feature_computer.make_feature_file(spectra_file, fname)

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
                     projects.get_version_names(project_name), False)
    elif command == "make-spectra":
        if len(args) < 2:
            print("Usage: make-spectra project-dir version")
            return

        project_dir = args[0]
        version = args[1]
        make_spectra(project_name, project_dir, [version], True)
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
        print_total_scores(project_name, use_filter)
    elif command == "compare-filter":
        compare_filter(project_name)
    elif command == "compute-features":
        compute_features(project_name)
    else:
        print("invalid command")
        return


if __name__ == "__main__":
    main()
