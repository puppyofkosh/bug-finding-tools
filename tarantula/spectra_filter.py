import run_result

# This is the file that determines which spectra to use, and which not to
# before we run tarantula.
def filter_spectra(run_to_result, run_to_feature):
    passing_spectra, failing_spectra = run_result.\
                                       get_passing_failing(run_to_result)

    assert set(passing_spectra.keys()) <= set(run_to_feature.keys())

    passing_tests_to_keep = passing_spectra.keys()
    passing_tests_to_keep = [p for p in passing_spectra if
                             #run_to_feature[p].min_common_over_failing <= 0.8 and
                             run_to_feature[p].intersection_over_passing < 1.0]

    passing_to_keep = [passing_spectra[test] for test in passing_tests_to_keep]
    failing_to_keep = list(failing_spectra.values())
    return passing_to_keep, failing_to_keep

def trivial_filter(run_to_result, _):
    passing_spectra, failing_spectra = run_result.\
                                       get_passing_failing(run_to_result)

    return list(passing_spectra.values()), list(failing_spectra.values())
