#! /bin/python

import sys
from collections import defaultdict
import pandas as pd

import projects
import spectra_maker
import evaluator
import feature_computer
import optimizer
import pd_helper


def print_tarantula_result(project_name, version, ranker_type, filter_type):
    failing_to_rankres = evaluator.get_ranker_results(project_name,
                                                      version,
                                                      ranker_type,
                                                      filter_type)

    assert len(failing_to_rankres) == 1
    ranker_res = next(iter(failing_to_rankres.values()))

    ranks = ranker_res.ranks
    suspiciousness = ranker_res.suspiciousness
    line = ranker_res.line

    results = pd.DataFrame(data={'rank': ranks, 'susp': suspiciousness})
    results.sort_values('rank', inplace=True)
    print(results.head(100))
    print("line {0}: score {1}".format(line, ranker_res.score))
    print("susp: {0}".format(suspiciousness[line]))
    print("rank: {0}".format(ranks[line]))


def get_total_scores(project_name, ranker_type, filter_type):
    version_to_rankres = {}
    for version in projects.get_version_names(project_name):
        failing_to_rankres = evaluator.get_ranker_results(project_name,
                                                          version,
                                                          ranker_type,
                                                          filter_type,
                                                          single_line=True)
        version_to_rankres.update(failing_to_rankres)
    

    version_to_score = {ver: rank_res.score for ver, rank_res in
                        version_to_rankres.items()}
    version_to_score = pd.Series(version_to_score)
    version_to_score.sort_values(inplace=True, ascending=False)
    return version_to_score

def print_total_scores(project_name, ranker_type, filter_type):
    version_to_score = get_total_scores(project_name, ranker_type, filter_type)
    print("Average score is {0}".format(version_to_score.mean()))
    print(version_to_score)

def compare_filter(project_name, ranker_type, filter_type):
    print("Computing with filter")
    filter_scores = get_total_scores(project_name, ranker_type, filter_type)
    print("Computing without filter")
    nofilter_scores = get_total_scores(project_name, "normal", "none")

    results = pd.DataFrame({'nofilter': nofilter_scores,
                            'filter': filter_scores,
                            'diff': filter_scores - nofilter_scores})
    results.sort_values('diff', inplace=True)

    pd_helper.print_df(results)


def get_all_results(ranker_type, filter_type):
    res_ser = pd.Series()
    for proj in projects.get_siemens_projects():
        ver_to_score = get_total_scores(proj, ranker_type, filter_type)
        ver_to_score.rename(lambda n: proj + "-" + n, inplace=True)

        res_ser = res_ser.append(ver_to_score)

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

    return res_ser, bin_to_count_ser

def print_all_results(ranker_type, filter_type):
    res_ser, bin_to_count_ser = get_all_results(ranker_type, filter_type)
    print(res_ser)
    print(bin_to_count_ser)
    
def compare_all_results(ranker_type, filter_type):
    a_scores, a_bin_to_count = get_all_results("normal", "none")
    b_scores, b_bin_to_count = get_all_results(ranker_type, filter_type)
    
    scores = pd.DataFrame({'normal': a_scores,
                           'modified': b_scores,
                           'diff': b_scores - a_scores})
    scores.sort_values('diff', inplace=True)

    bins = pd.DataFrame({'normal': a_bin_to_count,
                         'modified': b_bin_to_count,
                         'diff': b_bin_to_count - a_bin_to_count})
    print(scores)
    print(bins)
    print("average difference is {0}".format(scores['diff'].mean()))

    diff = scores['diff']
    diff_of_lower = diff[a_scores < 0.9] 
    print("Average difference for things that were previously under 0.9 {0}"\
          .format(diff_of_lower.mean()))

def main():
    if len(sys.argv) < 3:
        print("usage: {0} projectname command ...".format(sys.argv[0]))
        print("Valid projects are: {0}".format({}))

    project_name = sys.argv[1]
    command = sys.argv[2]

    if project_name == "all":
        args = sys.argv[3:]
        if command == "compare-filter":
            ranker_type = args[0]
            filter_type = args[1]
            compare_all_results(ranker_type, filter_type)
        if command == "evaluate-all":
            ranker_type = args[0]
            filter_type = args[1]
            print_all_results(ranker_type, filter_type)
            return
        elif command == "compute-features":
            for p in projects.get_siemens_projects():
                feature_computer.compute_features(p)
        return

    args = sys.argv[3:]
    if command == "make-all-spectra":
        if len(args) < 1:
            print("Usage: make-all-spectra project-dir")
            return

        project_dir = args[0]
        spectra_maker.make_spectra(project_name, project_dir,
                     projects.get_version_names(project_name), False)
    elif command == "make-spectra":
        if len(args) < 2:
            print("Usage: make-spectra project-dir version")
            return

        project_dir = args[0]
        version = args[1]
        spectra_maker.make_spectra(project_name,
                                   project_dir, [version], True)
    elif command == "find-bugs":
        if len(args) < 3:
            print("Usage: find-bugs version ranker-type filter-type")
            return
        version = args[0]
        ranker_type = args[1]
        filter_type = args[2]

        print_tarantula_result(project_name, version,
                               ranker_type, filter_type)
    elif command == "evaluate-all":
        if len(args) < 1:
            print("Usage evaluate-all ranker-type filter-type")
            return
        ranker_type = args[0]
        filter_type = args[1]
        print_total_scores(project_name, ranker_type, filter_type)
    elif command == "compare-filter":
        ranker_type = args[0]
        filter_type = args[1]
        compare_filter(project_name, ranker_type, filter_type)
    elif command == "compute-features":
        feature_computer.compute_features(project_name)
    elif command == "optimize":
        optimizer.optimize_classifier(project_name)
    else:
        print("invalid command")
        return


if __name__ == "__main__":
    main()
