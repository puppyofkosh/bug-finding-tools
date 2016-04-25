import json
from collections import namedtuple
import os

import commandio

import spectra_maker
import projects

_cache = {}

FeatureObj = namedtuple("FeatureObj", ["key_index", "feature_map"])

def make_feature_file(spectra_file, out_feature_file):
    commandio.get_output(["feature-extractor/feature-extractor", spectra_file,
                          out_feature_file,
                          "pairwise"])
    assert os.path.exists(out_feature_file)

def load(filename):
    if filename in _cache:
        return _cache[filename]

    features = {}
    with open(filename, "r") as fd:
        features = json.load(fd)

    
    key_index = features["key_index"]
    feature_map = features["feature_map"]
    
    feature_map = {int(failing_test):
                   {int(passing_test): vec
                    for passing_test, vec in passing_to_vec.items()}
                   for failing_test, passing_to_vec in feature_map.items()}

    fobj = FeatureObj(key_index, feature_map)
    _cache[filename] = fobj
    return fobj





FEATURE_DIR = "features"
def get_feature_file(project_name, version):
    fname = project_name + "-" + version + ".feat"
    fname = os.path.join(FEATURE_DIR, fname)
    return fname

def get_feature_vecs(project_name, version):
    return load(get_feature_file(project_name, version))

def compute_features(project_name):
    if not os.path.exists(FEATURE_DIR):
        os.mkdir(FEATURE_DIR)

    for version in projects.get_version_names(project_name):
        fname = get_feature_file(project_name, version)
        if os.path.exists(fname):
            print("V {0} Already exists, skipping".format(version))
            continue

        print("Computing version {0}".format(version))
        spectra_file = spectra_maker.get_spectra_file(project_name, version)
        make_feature_file(spectra_file, fname)
