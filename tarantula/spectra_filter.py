import numpy as np

import run_result



class SingleFailingDistanceFilterTopNPercent(object):
    def __init__(self, feature_obj, feature_name, n_percent_to_keep):
        self._key_index = feature_obj.key_index
        self._feature_index = self._key_index.index(feature_name)
        self._feature_map = feature_obj.feature_map
        self._feature_name = feature_name
        self._n_percent = n_percent_to_keep


    def filter_tests(self, run_to_result):
        passing_spectra, failing_spectra = run_result.\
                                           get_passing_failing(run_to_result)
        assert len(failing_spectra) == 1
        failing_test = next(iter(failing_spectra.keys()))

        def get_distance(passing):
            vec = self._feature_map[failing_test][passing]
            return vec[self._feature_index]
        ordered_passing = sorted(passing_spectra.keys(),
                                 key=get_distance)

        # Find the top n percent, but keep at least 1 test
        n_to_keep = int(max(float(len(ordered_passing)) * self._n_percent,
                        1))
        
        passing_to_keep = [passing_spectra[test]
                           for test in ordered_passing[0:n_to_keep]]
        failing_to_keep = list(failing_spectra.values())
        return passing_to_keep, failing_to_keep


class SingleFailingDistanceFilter(object):
    def __init__(self, feature_obj, feature_name, distance_cutoff):
        self._key_index = feature_obj.key_index
        self._feature_index = self._key_index.index(feature_name)
        self._feature_map = feature_obj.feature_map
        self._feature_name = feature_name
        self._distance_cutoff = distance_cutoff


    def filter_tests(self, run_to_result):
        passing_spectra, failing_spectra = run_result.\
                                           get_passing_failing(run_to_result)
        assert len(failing_spectra) == 1
        failing_test = next(iter(failing_spectra.keys()))

        passing_tests_to_keep = []

        for p in passing_spectra:
            vec = self._feature_map[failing_test][p]

            if vec[self._feature_index] <= self._distance_cutoff:
                passing_tests_to_keep.append(p)

        passing_to_keep = [passing_spectra[test]
                           for test in passing_tests_to_keep]
        failing_to_keep = list(failing_spectra.values())
        return passing_to_keep, failing_to_keep
        

# This is the file that determines which spectra to use, and which not to
# before we run tarantula.
class HeuristicFilter(object):
    def __init__(self, run_to_feature):
        self._run_to_feature = run_to_feature

    def filter_tests(self, run_to_result):
        passing_spectra, failing_spectra = run_result.\
                                           get_passing_failing(run_to_result)

        assert set(passing_spectra.keys()) <= set(self._run_to_feature.keys())


        passing_tests_to_keep = []
        run_to_feature = self._run_to_feature
        for p in passing_spectra:
            intersection = run_to_feature[p]['common_over_intersection']

            if intersection < 0.8:
                passing_tests_to_keep.append(p)

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
