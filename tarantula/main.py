#! /bin/python

from collections import defaultdict
import pandas as pd
import argparse

import projects
import evaluator
import optimizer
import pd_helper


def print_tarantula_result(project_name, version, ranker_type, filter_type):
    failing_to_rankres = evaluator.get_ranker_results(project_name,
                                                      version,
                                                      ranker_type,
                                                      filter_type,
                                                      "normal")

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


def get_total_scores(project_name, ranker_type, filter_type, provider_type,
                     versions=None):
    version_to_rankres = {}
    if versions is None:
        versions = projects.get_version_names(project_name)

    for version in versions:
        failing_to_rankres = evaluator.get_ranker_results(project_name,
                                                          version,
                                                          ranker_type,
                                                          filter_type,
                                                          provider_type)
        version_to_rankres.update(failing_to_rankres)
    

    version_to_score = {ver: rank_res.score for ver, rank_res in
                        version_to_rankres.items()}
    version_to_score = pd.Series(version_to_score)
    version_to_score.sort_values(inplace=True, ascending=False)
    return version_to_score

def print_total_scores(project_name, ranker_type, filter_type, provider_type,
                       versions=None):
    version_to_score = get_total_scores(project_name, ranker_type, filter_type,
                                        provider_type, versions=versions)
    print("Average score is {0}".format(version_to_score.mean()))
    pd_helper.print_df(version_to_score)

def compare_filter(project_name, ranker_type, filter_type, provider_type):
    print("Computing with filter")
    filter_scores = get_total_scores(project_name, ranker_type, filter_type,
                                     provider_type)
    print("Computing without filter")
    nofilter_scores = get_total_scores(project_name, "tarantula", "none",
                                       provider_type)

    results = pd.DataFrame({'nofilter': nofilter_scores,
                            'filter': filter_scores,
                            'diff': filter_scores - nofilter_scores})
    results.sort_values('diff', inplace=True)

    pd_helper.print_df(results)

    filter_bins = get_bin_to_count(filter_scores)
    nofilter_bins = get_bin_to_count(nofilter_scores)
    bins = pd.DataFrame({'filter': filter_bins,
                         'nofilter': nofilter_bins,
                         'diff': filter_bins - nofilter_bins})
    pd_helper.print_df(bins)


def get_bin_to_count(res_ser):
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
    return bin_to_count_ser

def get_all_results(ranker_type, filter_type, provider_type):
    res_ser = pd.Series()
    for proj in projects.get_siemens_projects():
        ver_to_score = get_total_scores(proj, ranker_type, filter_type,
                                        provider_type)
        ver_to_score.rename(lambda n: proj + "-" + n, inplace=True)

        res_ser = res_ser.append(ver_to_score)

    bin_to_count_ser = get_bin_to_count(res_ser)
    return res_ser, bin_to_count_ser

def print_all_results(ranker_type, filter_type, provider_type):
    res_ser, bin_to_count_ser = get_all_results(ranker_type, filter_type,
                                                provider_type)
    print(res_ser)
    print(bin_to_count_ser)
    
def compare_all_results(ranker_type, filter_type, provider_type):
    a_scores, a_bin_to_count = get_all_results("normal", "none", provider_type)
    b_scores, b_bin_to_count = get_all_results(ranker_type, filter_type,
                                               provider_type)
    
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
    parser = argparse.ArgumentParser()
    parser.add_argument("project_name", help="Name of project")
    parser.add_argument("command", help="A command")
    parser.add_argument("ranker_type",
                        help="ranker type, either normal or ochaia")
    parser.add_argument("filter_type", help="filter type")
    parser.add_argument("run_result_provider_type",
                        help="either normal, or singlefailing")
    parser.add_argument("--bugversion", help="The version of bug to use")
    args = parser.parse_args()

    project_name = args.project_name
    command = args.command

    ranker_type = args.ranker_type
    filter_type = args.filter_type
    provider_type = args.run_result_provider_type
    
    if project_name == "all":
        if command == "compare-filter":
            compare_all_results(ranker_type, filter_type, provider_type)
        if command == "evaluate-all":
            print_all_results(ranker_type, filter_type, provider_type)
        return

    if command == "find-bugs":
        version = args.bugversion
        assert version
        print_tarantula_result(project_name, version,
                               ranker_type, filter_type)
    elif command == "evaluate":
        version = args.bugversion
        assert version
        print_total_scores(project_name, ranker_type, filter_type,
                           provider_type, versions=[version])
    elif command == "evaluate-all":
        print_total_scores(project_name, ranker_type, filter_type,
                           provider_type)
    elif command == "compare-filter":
        compare_filter(project_name, ranker_type, filter_type, provider_type)
    elif command == "optimize":
        optimizer.optimize_classifier(project_name)
    else:
        print("invalid command")
        return


if __name__ == "__main__":
    main()
