import numpy as np

import run_result


# This is the file that determines which spectra to use, and which not to
# before we run tarantula.
class HeuristicFilter(object):
    def __init__(self, run_to_feature):
        self._run_to_feature = run_to_feature

    def filter_tests(self, run_to_result):
        passing_spectra, failing_spectra = run_result.\
                                           get_passing_failing(run_to_result)

        assert set(passing_spectra.keys()) <= set(self._run_to_feature.keys())

        passing_tests_to_keep = passing_spectra.keys()
        passing_tests_to_keep = [p for p in passing_spectra if
                                 #run_to_feature[p].min_common_over_failing <= 0.8 and
                                 self._run_to_feature[p].\
                                 intersection_over_passing < 1.0]

        passing_to_keep = [passing_spectra[test]
                           for test in passing_tests_to_keep]
        failing_to_keep = list(failing_spectra.values())
        return passing_to_keep, failing_to_keep


class TrivialFilter(object):
    def filter_tests(self, run_to_result):
        passing_spectra, failing_spectra = run_result.\
                                           get_passing_failing(run_to_result)

        return list(passing_spectra.values()), list(failing_spectra.values())

class DotProductFilter(object):
    def __init__(self, classify_vector, cutoff, run_to_feature):
        self._classify_vector = np.array(classify_vector)
        self._cutoff = cutoff
        self._run_to_feature = run_to_feature

    def filter_tests(self, run_to_result):
        passing_spectra, failing_spectra = run_result.\
                                           get_passing_failing(run_to_result)
        assert len(passing_spectra) > 0
        assert len(failing_spectra) > 0
        assert set(passing_spectra.keys()) == set(self._run_to_feature.keys())
        
        first_res = next(iter(self._run_to_feature.values()))
        key_index = sorted(first_res.keys())
        passing_to_keep = []
        for passing_test, spectrum in passing_spectra.items():
            feature_dict = self._run_to_feature[passing_test]
            feature_vec = np.array([feature_dict[k] for k in key_index])
            score = np.dot(self._classify_vector, feature_vec)
            if score >= self._cutoff:
                passing_to_keep.append(spectrum)
            
        return passing_to_keep, list(failing_spectra.values())
