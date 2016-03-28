import pandas as pd
import json
from collections import namedtuple

RunResult = namedtuple('RunResult', ['passed', 'spectrum'])


# So we don't have to keep loading from disk
_cache = {}

# Save and load dictionary of test number -> result
def save(fname, run_to_result):
    run_to_result_dict = {test: dict(res._asdict()) for test, res in
                          run_to_result.items()}

    jsonstring = json.dumps(run_to_result_dict)
    with open(fname, "w") as fd:
        fd.write(jsonstring)
                          

def load(fname):
    if fname in _cache:
        return _cache[fname]

    run_to_result = {}
    jsonobj = None
    print(fname)
    with open(fname, "r") as fd:
        jsonobj = json.load(fd)
    
    # Convert dictionary representations of RunResults back to RunResults
    run_to_result = {int(test): RunResult(**run_res_dict)
                     for test, run_res_dict
                     in jsonobj.items()}
    
    for test, run_res in run_to_result.items():
        # Convert all spectra to pandas series once
        # Convert to binary spectra
        spectrum = {int(line): 1 if val > 0 else 0
                    for line,val in run_res.spectrum.items()}
        spectrum_ser = pd.Series(spectrum).sort_values(ascending=False)
        run_to_result[test] = run_res._replace(spectrum=spectrum_ser)

    _cache[fname] = run_to_result
    return run_to_result

def get_passing_failing(run_to_result):
    passing_spectra = {}
    failing_spectra = {}
    for run, res in run_to_result.items():
        if res.passed:
            passing_spectra[run] = res.spectrum
        else:
            failing_spectra[run] = res.spectrum
    return passing_spectra, failing_spectra
