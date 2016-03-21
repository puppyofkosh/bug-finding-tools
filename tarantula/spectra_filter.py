import run_result

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
def filter_spectra(run_to_result):
    passing_spectra, failing_spectra = run_result.\
                                       get_passing_failing(run_to_result)

    passing_to_keep = [p for p in passing_spectra
                       if dist_from_closest(p, failing_spectra) > 20]

    failing_to_keep = failing_spectra
    return passing_to_keep, failing_to_keep

def trivial_filter(run_to_result):
    passing_spectra, failing_spectra = run_result.\
                                       get_passing_failing(run_to_result)

    return passing_spectra, failing_spectra
