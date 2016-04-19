# This file contains the actual implementation of tarantula

import pandas as pd
import numpy as np

def convert_to_binary_vector_spectrum(spectrum, key_index):
    return np.array([1.0 if spectrum[k] > 0 else 0.0
                     for k in key_index])

def convert_spectra_to_binary(spectra, key_index):
    return [convert_to_binary_vector_spectrum(s, key_index) for s in spectra]


def divide_replace_nan(numerator, denominator, replacement):
    divided = None
    with np.errstate(divide='ignore', invalid='ignore'):
        # Replace any divisions by zero with just 0
        divided = np.true_divide(numerator, denominator)
        divided[ ~ np.isfinite(divided)] = replacement  # -inf inf NaN
    return divided


def compute_suspiciousness(passing_spectra, failing_spectra):
    assert len(passing_spectra) > 0
    assert len(failing_spectra) > 0
    key_index = np.array(sorted(passing_spectra[0].keys()))

    keys = set(key_index)
    assert all(set(p.keys()) == keys for p in passing_spectra)
    assert all(set(f.keys()) == keys for f in failing_spectra)

    passing_spectra = convert_spectra_to_binary(passing_spectra,
                                                key_index)
    failing_spectra = convert_spectra_to_binary(failing_spectra,
                                                key_index)

    passing_counts = sum(passing_spectra)
    failing_counts = sum(failing_spectra)

    total_failed = len(failing_spectra)
    total_passed = len(passing_spectra)

    assert total_failed > 0 and total_passed > 0

    # Now we get the suspiciousness of each line
    failing_counts /= float(total_failed)
    passing_counts /= float(total_passed)

    denom = failing_counts + passing_counts

    susp = divide_replace_nan(failing_counts, denom, 0)
    susp_dict = {line: susp[i] for i, line in enumerate(key_index)}

    return susp_dict


def get_statement_ranks(susp_dict):
    assert len(susp_dict) > 0
    
    # A lot of this stuff could be accomplished with pandas, and be more
    # readable, but the cost of creating pandas series is pretty heavy,
    # and since this function gets called a lot, it has to be as fast
    # as possible.
    
    line_susp_pairs = list(susp_dict.items())
    # Sort so that we have most suspicious lines first
    line_susp_pairs = sorted(line_susp_pairs,
                             key=lambda line_susp: line_susp[1],
                             reverse=True)

    susps = sorted(set(susp_dict.values()),reverse=True)
    
    line_to_rank = {}
    cur_rank = 1
    for line,susp in line_susp_pairs:
        if susps[cur_rank - 1] != susp:
            cur_rank += 1
            assert susp == susps[cur_rank - 1]
        
        line_to_rank[line] = cur_rank
    return line_to_rank


class TarantulaRanker(object):
    def get_suspicious_lines(self, passing_spectra, failing_spectra):
        assert len(passing_spectra) > 0
        assert len(failing_spectra) > 0
        suspiciousness = compute_suspiciousness(passing_spectra,
                                                failing_spectra)

        ranks = get_statement_ranks(suspiciousness)
        return ranks, suspiciousness


class OchaiaRanker(object):
    def get_suspicious_lines(self, passing_spectra, failing_spectra):
        assert len(passing_spectra) > 0
        assert len(failing_spectra) > 0
        key_index = np.array(sorted(passing_spectra[0].keys()))

        keys = set(key_index)
        assert all(set(p.keys()) == keys for p in passing_spectra)
        assert all(set(f.keys()) == keys for f in failing_spectra)

        passing_spectra = convert_spectra_to_binary(passing_spectra, key_index)
        failing_spectra = convert_spectra_to_binary(failing_spectra, key_index)

        passing_counts = sum(passing_spectra)
        failing_counts = sum(failing_spectra)

        total_failed = len(failing_spectra)
        total_passed = len(passing_spectra)

        assert total_failed > 0 and total_passed > 0

        # Ochaia formula is, for each statement:
        # (# times executed by failing test)
        # __________________________________
        # sqrt((# failing which executed + # of failing which didn't execute) *
        # (# times executed by failing + # times executed by passing))

        numerator = failing_counts
        total_failing = np.full(len(passing_spectra[0]), float(total_failed))
        
        denom = np.sqrt(total_failing * (failing_counts + passing_counts))

        susp = divide_replace_nan(numerator, denom, 0)
        susp_dict = {line: susp[i] for i, line in enumerate(key_index)}

        ranks = get_statement_ranks(susp_dict)
        return ranks, susp_dict
