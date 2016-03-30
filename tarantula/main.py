#! /bin/python

import os
import sys
import pandas as pd
from collections import defaultdict

import projects
import test_runner
import tarantula
import evaluator
import spectra_filter
import run_result
import feature_computer
import tarantula_runner
import optimizer

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


def get_tarantula_results(project_name, version, filter_obj):
    run_to_result = run_result.load(get_spectra_file(project_name, version))

    buggy_lines = projects.get_known_buggy_lines(project_name,
                                                 version)
    if buggy_lines is None:
        print("Buggy lines aren't known for version {0}".format(version))
        return None, None, None, None

    return tarantula_runner.get_tarantula_results(run_to_result,
                                                  filter_obj, buggy_lines)


def get_tarantula_output(project_name, version, use_filter):

    filter_obj = spectra_filter.TrivialFilter()
    if use_filter:
        feature_file = get_feature_file(project_name, version)
        features = feature_computer.load(feature_file)
        #filter_obj = spectra_filter.HeuristicFilter(features)
        v = [0.1, 0.1, 0.1,
             0.1, 0.1, 0.1,
             0.1]
        
        v = [-59.07164369,  81.16767812, -32.15659794,
             5.06205734,
             83.42100009, -32.84513908, -63.71071346]
        cutoff = 0.46388956
        filter_obj = spectra_filter.DotProductFilter(v, cutoff, features)

    return get_tarantula_results(project_name, version, filter_obj)


def print_tarantula_result(project_name, version, use_filter):
    (ranks, suspiciousness, line, score) = get_tarantula_output(project_name,
                                                                version,
                                                                use_filter)
    results = pd.DataFrame(data={'rank': ranks, 'susp': suspiciousness})
    results.sort_values('rank', inplace=True)
    print(results.head(100))
    print("line {0}: score {1}".format(line, score))
    print("susp: {0}".format(suspiciousness[line]))
    print("rank: {0}".format(ranks[line]))


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

def get_all_results():
    res_ser = pd.Series()
    for proj in projects.get_siemens_projects():
        ver_to_score = get_total_scores(proj, False)
        ver_to_score.rename(lambda n: proj + "-" + n, inplace=True)

        res_ser = res_ser.append(ver_to_score)

    print(res_ser)

    BINS = [(0, 0.1), (0.1, 0.2), (0.2, 0.3),
            (0.3, 0.4), (0.4, 0.5), (0.5, 0.6),
            (0.6, 0.7), (0.7, 0.8), (0.8, 0.9),
            (0.9, 0.99), (0.99, 1.0)]
    bin_to_count = defaultdict(int)
    for score in res_ser:
        for b in BINS:
            if score >= b[0] and score < b[1]:
                bin_to_count[b] += 1
                break

    bin_to_count_ser = pd.Series(bin_to_count)
    assert bin_to_count_ser.sum() == len(res_ser)
    # Give percentages of how many fall into each bin
    bin_to_count_ser /= len(res_ser)

    print(bin_to_count_ser)

    return res_ser


def main():
    if len(sys.argv) < 3:
        print("usage: {0} projectname command ...".format(sys.argv[0]))
        print("Valid projects are: {0}".format({}))

    project_name = sys.argv[1]
    command = sys.argv[2]
    args = sys.argv[3:]

    if project_name == "all":
        if command == "evaluate-all":
            get_all_results()
            return
        elif command == "compute-features":
            for p in projects.get_siemens_projects():
                compute_features(p)
        return


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
    elif command == "optimize":
        optimizer.optimize_classifier(project_name)
    else:
        print("invalid command")
        return


if __name__ == "__main__":
    main()
