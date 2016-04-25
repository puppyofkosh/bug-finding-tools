from collections import namedtuple

import spectra_maker
import projects
import tarantula
import spectra_filter
import run_result
import feature_computer
import run_result_provider

# This file evaluates how good a ranking that's produced by tarantula
# is It takes in a dictionary of line num -> rank, as well as a set of
# lines which are known to have the bug (often, just one line num) and
# finds the "score"
# The score is the percent of the program (percent of executable lines we'll say)
# which you would NOT have to look at if you followed tarantula's output.
# This returns the best score of all the line numbers in the set


def get_score(line_to_rank_ser, buggy_line_nums):
    best_line = None
    best_score = None
    for l in buggy_line_nums:
        if l not in line_to_rank_ser:
            continue
        
        rank = line_to_rank_ser[l]
        others = [l for l,r in line_to_rank_ser.items() if r > rank]
        #others = line_to_rank_ser[line_to_rank_ser > rank]
        score = len(others) / float(len(line_to_rank_ser))
        if best_line is None or score > best_score:
            best_line = l
            best_score = score

    # They should pass in at least one valid line
    assert best_line is not None
    return best_line, best_score


RankerResult = namedtuple(
    'RankerResult',
    ['ranks',
     'suspiciousness',
     'line',
     'score']
)

def compute_results(run_to_result, ranker_obj,
                    filter_obj,
                    buggy_lines):
    passing_spectra, failing_spectra = filter_obj.filter_tests(run_to_result)

    if len(passing_spectra) == 0 or len(failing_spectra) == 0:
        return None

    ranks, suspiciousness = ranker_obj.get_suspicious_lines(passing_spectra,
                                                            failing_spectra)

    line, score = get_score(ranks, buggy_lines)

    return RankerResult(ranks, suspiciousness, line, score)

def get_ranker(project_name, version, ranker_type):
    if ranker_type == "tarantula":
        return tarantula.TarantulaRanker()
    elif ranker_type == "ochaia":
        return tarantula.OchaiaRanker()
    raise RuntimeError("Unkown ranker {0}".format(ranker_type))

def get_run_res_provider(t):
    if t == "normal":
        return run_result_provider.TrivialProvider()
    elif t == "singlefailing":
        return run_result_provider.SingleFailingProvider()
    raise RuntimeError("Unkown run res provider {0}".format(t))

def get_filter(project_name, version, filter_type):
    if filter_type == "none":
        return spectra_filter.TrivialFilter()

    feature_obj = feature_computer.get_feature_vecs(project_name,
                                                    version)
    if filter_type == "heuristic":
        return spectra_filter.HeuristicFilter(feature_obj)
    elif filter_type == "direct_cutoff":
        return spectra_filter.SingleFailingDistanceFilter(
            feature_obj,
            'inv_common_execd_over_passing',
            0.15)
    elif filter_type == "topn":
        return spectra_filter.SingleFailingDistanceFilterTopNPercent(
            feature_obj,
            'normalized_hamming',
            0.3)

    raise RuntimeError("Unkown filter {0}".format(filter_type))

def get_ranker_results_with_objs(project_name, version, ranker_obj, filter_obj,
                                 provider):
    spectra_file = spectra_maker.get_spectra_file(project_name, version)
    run_to_result = run_result.load(spectra_file)

    buggy_lines = projects.get_known_buggy_lines(project_name,
                                                 version)
    if buggy_lines is None:
        print("Buggy lines aren't known for version {0}".format(version))
        return None



    failing_to_rankres = {}
    for failing_test_num, run_res in provider.get_run_results(run_to_result):
        failing_to_rankres[failing_test_num] = compute_results(run_res,
                                                               ranker_obj,
                                                               filter_obj,
                                                               buggy_lines)

    ret = {}
    for failing,rank_res in failing_to_rankres.items():
        key = "{0}-{1}-{2}".format(project_name, version, failing)
        ret[key] = rank_res
    return ret


def get_ranker_results(project_name, version,
                       ranker_type, filter_type,
                       run_res_prov_type):
    ranker_obj = get_ranker(project_name, version, ranker_type)
    filter_obj = get_filter(project_name, version, filter_type)
    provider = get_run_res_provider(run_res_prov_type)
    return get_ranker_results_with_objs(project_name, version, ranker_obj,
                                        filter_obj, provider)
