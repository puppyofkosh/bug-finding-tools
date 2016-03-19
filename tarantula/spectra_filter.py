def _spectra_difference(a, b):
    diff = a.add(-1 * b, fill_value=0)
    return diff.abs().sum()

def get_nearest_passing_spectrum(spectrum, run_to_result):
    # TODO: Write this with argmin instead
    best_ind = None
    best_diff = None
    for test, run_res in run_to_result.items():
        if not run_res.passed:
            continue

        diff = _spectra_difference(spectrum, run_res.spectrum)
        if best_diff is None or best_diff > diff:
            if run_res.spectrum.equals(spectrum):
                continue

            best_ind = test
            best_diff = diff

    assert best_ind is not None
    return best_ind

def get_failing_test(run_to_result):
    failing = [test
               for test, run_res in run_to_result.items()
               if not run_res.passed]
    assert len(failing) > 0
    return failing[0]

# This is the file that determines which spectra to use, and which not to
# before we run tarantula.
def filter_spectra(run_to_result):
    failing_tests = [t for t, run_res in run_to_result.items()
                     if not run_res.passed]

    # Keep the failing tests and their "nearest neighbors"
    tests_to_keep = [get_nearest_passing_spectrum(run_to_result[t].spectrum,
                                                    run_to_result)
                       for t in failing_tests]
    tests_to_keep += failing_tests
    
    return {test: run_to_result[test] for test in tests_to_keep}

def get_avg(run_to_result):
    # Find the average distance between spectra
    failing_test = get_failing_test(run_to_result)
    passing, failing_spectrum = run_to_result[failing_test]
    assert not passing
    total_difference = 0
    total_compared = 0
    test_to_diff = {}
    for test, run_res in run_to_result.items():
        if not run_res.passed:
            continue
        
        total_compared += 1
        diff = _spectra_difference(failing_spectrum, run_res.spectrum)
        total_difference += diff

        test_to_diff[test] = diff

    
    avg_difference = float(total_difference)/total_compared
    print("Avg distance is {0}".format(avg_difference))
    return run_to_result
