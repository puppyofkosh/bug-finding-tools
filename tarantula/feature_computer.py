import pickle
from collections import namedtuple

import run_result



FeatureVec = namedtuple('FeatureVec',
                        ['lowest_ratio_failing_both_exec',
                         'highest_ratio_failing_both_exec',
                         'avg_ratio_failing_both_exec',
                         #^ ratio of num statements both executed / num stmts
                         # failed test executed

                         #v ratio of num statements both executed / num stmts
                         # passing test executed
                         'lowest_ratio_passing_both_exec',
                         'highest_ratio_passing_both_exec',
                         'avg_ratio_passing_both_exec',
                     ])

def _make_feature_vec(passing_spectrum,
                      failing_spectra):
    p = passing_spectrum

    common_over_failing = []
    common_over_passing = []
    for failing in failing_spectra:
        failing_did_execute = (failing == 1)
        passing_did_execute = (p == 1)
        both_executed = len(failing[failing_did_execute & passing_did_execute])
        
        npassing_execd = float(len(p[passing_did_execute]))
        nfailing_execd = float(len(failing[failing_did_execute]))

        common_over_passing.append(both_executed / npassing_execd)
        common_over_failing.append(both_executed / nfailing_execd)

    vec = FeatureVec(min(common_over_failing),
                     max(common_over_failing),
                     sum(common_over_failing) / len(common_over_failing),
                     min(common_over_passing),
                     max(common_over_passing),
                     sum(common_over_passing) / len(common_over_passing))
    return vec

def compute_features(test_to_passing_spectra, test_to_failing_spectra):
    feature_vecs = {}

    failing_spectra = list(test_to_failing_spectra.values())
    nfailing = len(failing_spectra)
    for test, p in test_to_passing_spectra.items():
        feature_vecs[test] = _make_feature_vec(p, failing_spectra)
    
    return feature_vecs

def save_features(filename, run_to_result):
    passing_spectra, failing_spectra = run_result.\
                                       get_passing_failing(run_to_result)
    
    features = compute_features(passing_spectra, failing_spectra)

    with open(filename, "wb") as fd:
        pickle.dump(features, fd)

def load(filename):
    features = {}
    with open(filename, "rb") as fd:
        features = pickle.load(fd)
    return features
