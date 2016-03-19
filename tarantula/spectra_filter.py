import pandas as pd

def _spectra_difference(a, b):
    a = pd.Series(a)
    b = pd.Series(b)

    diff = a.add(-1 * b, fill_value=0)
    return diff.abs().sum()

def get_failing_test(run_to_result):
    failing = [test
               for test, run_res in run_to_result.iteritems()
               if not run_res.passed]
    assert len(failing) > 0
    return failing[0]

# This is the file that determines which spectra to use, and which not to
# before we run tarantula.
def filter_spectra(run_to_result):
    # Find the average distance between spectra
    failing_test = get_failing_test(run_to_result)
    passing, failing_spectrum = run_to_result[failing_test]
    assert not passing
    total_difference = 0
    total_compared = 0
    test_to_diff = {}
    for test, run_res in run_to_result.iteritems():
        if not run_res.passed:
            continue
        
        total_compared += 1
        diff = _spectra_difference(failing_spectrum, run_res.spectrum)
        total_difference += diff

        test_to_diff[test] = diff

    
    avg_difference = float(total_difference)/total_compared
    print "Avg distance is {0}".format(avg_difference)

    # spectra_to_keep = {test:val for test,val in run_to_result.iteritems()
    #                    if test in test_to_diff and
    #                    test_to_diff[test] <= avg_difference}
    # spectra_to_keep[failing_test] = run_to_result[failing_test]

    return run_to_result
