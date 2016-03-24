import run_result

def _spectra_difference(a, b):
    diff = a.add(-1 * b, fill_value=0)
    return diff.abs().sum()

def dist_from_furthest(spectrum, spectra):
    """Return spectrum's distance from the furthest element of spectra"""
    return max(_spectra_difference(spectrum, f) for f in spectra)

def dist_from_closest(spectrum, spectra):
    return min(_spectra_difference(spectrum, f) for f in spectra)

def avg_distance(spectrum, spectra):
    total_dist = sum(_spectra_difference(s, spectrum) for s in spectra)
    return float(total_dist) / len(spectra)


# This is the file that determines which spectra to use, and which not to
# before we run tarantula.
def filter_spectra(run_to_result, run_to_feature):
    passing_spectra, failing_spectra = run_result.\
                                       get_passing_failing(run_to_result)

    assert set(passing_spectra.keys()) <= set(run_to_feature.keys())

    passing_tests_to_keep = passing_spectra.keys()
    passing_tests_to_keep = [p for p in passing_spectra if
                             run_to_feature[p].avg_common_executed > 0.5]

    passing_to_keep = [passing_spectra[test] for test in passing_tests_to_keep]
    failing_to_keep = failing_spectra.values()
    return passing_to_keep, failing_to_keep

def trivial_filter(run_to_result, _):
    passing_spectra, failing_spectra = run_result.\
                                       get_passing_failing(run_to_result)

    return passing_spectra.values(), failing_spectra.values()
