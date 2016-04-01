import json
from collections import namedtuple
import os

import commandio

import spectra_maker
import projects

FeatureVec = namedtuple(
    'FeatureVec',
    ["avg_common_over_failing",
     "min_common_over_failing",
     "max_common_over_failing",
     "avg_common_over_passing",
     "min_common_over_passing",
     "max_common_over_passing",

     "passing_over_intersection",
])

_cache = {}

def make_feature_file(spectra_file, out_feature_file):
    commandio.get_output(["feature-extractor/feature-extractor", spectra_file,
                          out_feature_file])
    assert os.path.exists(out_feature_file)

def load(filename):
    if filename in _cache:
        return _cache[filename]

    features = {}
    with open(filename, "r") as fd:
        features = json.load(fd)

    features = {int(test): v for test,v in features.items()}
    _cache[filename] = features
    return features



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
