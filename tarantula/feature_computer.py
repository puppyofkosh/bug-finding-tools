import pickle
from collections import namedtuple

import run_result



FeatureVec = namedtuple('FeatureVec', ['closest_common_executed',
                                       'furthest_common_executed',
                                       'avg_common_executed'])

def compute_features(test_to_passing_spectra, test_to_failing_spectra):
    feature_vecs = {}

    failing_spectra = test_to_failing_spectra.values()
    nfailing = len(failing_spectra)
    for test, p in test_to_passing_spectra.items():
        plen = float(len(p))

        # Number of positions where they both have a 1
        commonly_executed = [len(p[((p==other) & (p==1))])
                             for other in failing_spectra]
        
        closest_common_executed = max(commonly_executed) / plen
        furthest_common_executed = min(commonly_executed) / plen
        avg_common_executed = sum(commonly_executed) / nfailing / plen
        vec = FeatureVec(closest_common_executed,
                         furthest_common_executed,
                         avg_common_executed)
        feature_vecs[test] = vec
    
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
