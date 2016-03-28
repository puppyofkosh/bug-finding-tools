# This file contains the actual implementation of tarantula

import pandas as pd
import numpy as np

def convert_to_binary_vector_spectrum(spectrum, key_index):
    return np.array([1.0 if spectrum[k] > 0 else 0.0
                     for k in key_index])

def _compute_suspiciousness(passing_spectra, failing_spectra):
    # Must be binary spectra
    assert len(passing_spectra) > 0
    assert len(failing_spectra) > 0
    key_index = np.array(sorted(passing_spectra[0].keys()))

    keys = set(key_index)
    assert all(set(p.keys()) == keys for p in passing_spectra)
    assert all(set(f.keys()) == keys for f in failing_spectra)

    passing_spectra = [convert_to_binary_vector_spectrum(p, key_index)
                       for p in passing_spectra]
    failing_spectra = [convert_to_binary_vector_spectrum(f, key_index)
                       for f in failing_spectra]

    assert all(max(p) == 1 for p in passing_spectra)
    assert all(max(f) == 1 for f in failing_spectra)

    passing_counts = sum(passing_spectra)
    failing_counts = sum(failing_spectra)

    total_failed = len(failing_spectra)
    total_passed = len(passing_spectra)

    assert total_failed > 0 and total_passed > 0

    # Now we get the suspiciousness of each line
    failing_counts /= float(total_failed)
    passing_counts /= float(total_passed)

    denom = failing_counts + passing_counts

    susp = None
    with np.errstate(divide='ignore', invalid='ignore'):
        # Replace any divisions by zero with just 0
        susp = np.true_divide(failing_counts, denom)
        susp[ ~ np.isfinite(susp)] = 0  # -inf inf NaN

    susp_dict = {line: susp[i] for i, line in enumerate(key_index)}

    suspiciousness = pd.Series(susp_dict)
    assert not suspiciousness.isnull().values.any()
    suspiciousness.sort_values(inplace=True, ascending=False)
    return suspiciousness


def _get_statement_ranks(suspiciousness):
    assert len(suspiciousness) > 0
    assert suspiciousness.max() <= 1.0 and suspiciousness.min() >= 0
    suspiciousness.sort_values(inplace=True, ascending=False)

    #
    # We rank statements by how many statements we'd have to look
    # at until we got to this one (starting from 1), going from
    # high to low suspiciousness.
    # If two statements have the same suspiciousness, then we give all the
    # statements the rank, assuming we look at it last. In other words,
    # all of the statements with the same suspiciousness get the same rank.
    # Example: Suspiciousnesses are: 0.8 0.5 0.5 0.3
    # Ranks are:                      1   3   3   4
    # We assume we'd look at the 0.5 statements last, so they each get rank 3.
    #
    
    df = pd.DataFrame(suspiciousness, columns=['susp'])
    # maps suspiciousness -> all indices with that suspiciousness
    gb = df.groupby('susp')
    
    ordered_suspiciousness_scores = sorted(set(suspiciousness.values),
                                           reverse=True)
    
    line_to_rank = {}
    cur_rank = 1
    for s in ordered_suspiciousness_scores:
        group = gb.get_group(s)
        lines = group.index
        for l in lines:
            line_to_rank[l] = cur_rank

        cur_rank += 1

    assert len(line_to_rank) == len(suspiciousness)
    line_to_rank_ser = pd.Series(line_to_rank)
    line_to_rank_ser.sort_values(inplace=True)
    return line_to_rank_ser


def get_suspicious_lines(passing_res, failing_res):
    assert len(passing_res) > 0
    assert len(failing_res) > 0
    suspiciousness = _compute_suspiciousness(passing_res,
                                             failing_res)

    ranks = _get_statement_ranks(suspiciousness)
    return ranks, suspiciousness
