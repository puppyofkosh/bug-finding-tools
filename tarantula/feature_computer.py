import json
from collections import namedtuple
import os

import commandio


FeatureVec = namedtuple(
    'FeatureVec',
    ["avg_common_over_failing",
     "min_common_over_failing",
     "max_common_over_failing",
     "avg_common_over_passing",
     "min_common_over_passing",
     "max_common_over_passing",
])

def make_feature_file(spectra_file, out_feature_file):
    commandio.get_output(["feature-extractor/feature-extractor", spectra_file,
                          out_feature_file])
    assert os.path.exists(out_feature_file)

def load(filename):
    features = {}
    with open(filename, "r") as fd:
        features = json.load(fd)

    features = {int(test): FeatureVec(**v) for test,v in features.items()}
    return features
