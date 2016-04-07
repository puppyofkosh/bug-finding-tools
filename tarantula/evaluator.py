from collections import namedtuple

import spectra_maker
import projects
import tarantula
import spectra_filter
import run_result
import feature_computer

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
        others = line_to_rank_ser[line_to_rank_ser > rank]
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
    if ranker_type == "normal":
        return tarantula.TarantulaRanker()
    elif ranker_type == "intersection":
        return tarantula.IntersectionTarantulaRanker()
    elif ranker_type == "ochaia":
        return tarantula.OchaiaRanker()
    raise RuntimeError("Unkown ranker {0}".format(ranker_type))

def get_filter(project_name, version, filter_type):
    if filter_type == "none":
        return spectra_filter.TrivialFilter()

    feature_file = feature_computer.get_feature_file(project_name, version)
    features = feature_computer.load(feature_file)
    if filter_type == "heuristic":
        return spectra_filter.HeuristicFilter(features)
    elif filter_type == "learned":
        v = [-62.3405955 ,  13.86391412,  11.2309994 ,  -4.03151566,
       -90.7341109 ,   8.03077839, -50.52596326, -36.57490774,
        73.2524005 ,  78.83498064,  12.20039375,  78.07912836,
        82.40447128, -63.78238101, -57.65408425]
        return spectra_filter.DotProductFilter(v, features)

    raise RuntimeError("Unkown filter {0}".format(filter_type))

def get_ranker_results(project_name, version, ranker_type, filter_type):
    ranker_obj = get_ranker(project_name, version, ranker_type)
    filter_obj = get_filter(project_name, version, filter_type)

    spectra_file = spectra_maker.get_spectra_file(project_name, version)
    run_to_result = run_result.load(spectra_file)

    buggy_lines = projects.get_known_buggy_lines(project_name,
                                                 version)
    if buggy_lines is None:
        print("Buggy lines aren't known for version {0}".format(version))
        return None

    return compute_results(run_to_result,
                              ranker_obj,
                              filter_obj,
                              buggy_lines)
