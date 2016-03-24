import pickle
from collections import namedtuple

import run_result



FeatureVec = namedtuple('FeatureVec', ['dist_from_closest_failing',
                                       'dist_from_furthest_failing',
                                       'avg_dist_from_failing'])


def _spectra_difference(a, b):
    diff = a.add(-1 * b)
    return diff.abs().sum()

def compute_features(passing_spectra, failing_spectra):
    feature_vecs = {}
    for test, p in passing_spectra.items():
        
        

        failing_spectra_diffs = [_spectra_difference(p, other)
                                 for other in failing_spectra.values()]
        dist_from_closest = min(failing_spectra_diffs) / float(len(p))
        dist_from_furthest = max(failing_spectra_diffs) / float(len(p))
        avg_distance = sum(d for d in failing_spectra_diffs) / float(len(p))
        vec = FeatureVec(dist_from_closest,
                         dist_from_furthest,
                         avg_distance)
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
