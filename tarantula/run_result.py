import pandas as pd
import pickle
from collections import namedtuple

RunResult = namedtuple('RunResult', ['passed', 'spectrum'])


# Save and load dictionary of test number -> result
def save(fname, run_to_result):
    with open(fname, "wb") as fd:
        pickle.dump(run_to_result, fd)

def load(fname):
    run_to_result = {} # type: Dict[int, RunResult]
    with open(fname, "rb") as fd:
        run_to_result = pickle.load(fd)
    
    for test, run_res in run_to_result.items():
        # Convert all spectra to pandas series once
        spectrum_ser = pd.Series(run_res.spectrum).sort_values(ascending=False)
        run_to_result[test] = run_res._replace(spectrum=spectrum_ser)
    return run_to_result

def get_passing_failing(run_to_result):
    passing_spectra = []
    failing_spectra = []
    for run_res in run_to_result.values():
        if run_res.passed:
            passing_spectra.append(run_res.spectrum)
        else:
            failing_spectra.append(run_res.spectrum)
    return passing_spectra, failing_spectra
