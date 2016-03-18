# This file contains the actual implementation of tarantula

import pandas as pd


def _sum_spectra(spectr):
    total = pd.Series()
    for spectrum in spectr:
        ser = pd.Series(spectrum)
        total = total.add(ser, fill_value=0)
    return total


def _compute_suspiciousness(passing_spectra, failing_spectra):
    failing_counts = _sum_spectra(failing_spectra)
    passing_counts = _sum_spectra(passing_spectra)

    total_failed = len(failing_spectra)    
    total_passed = len(passing_spectra)

    assert total_failed > 0 and total_passed > 0
    assert not passing_counts.isnull().values.any()
    assert not failing_counts.isnull().values.any()

    # Now we get the suspiciousness of each line
    failing_counts /= float(total_failed)
    passing_counts /= float(total_passed)

    denom = failing_counts.add(passing_counts, fill_value=0)
    suspiciousness = failing_counts.mul(1.0 / denom, fill_value=0)
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
    line_to_rank = {}
    cur_rank = 1
    cur_susp = suspiciousness[suspiciousness.index[0]]
    lines_with_cur_rank = set()
    for line, susp in suspiciousness.iteritems():
        if cur_susp != susp:
            assert len(lines_with_cur_rank) > 0
            for l in lines_with_cur_rank:
                line_to_rank[l] = cur_rank

            cur_rank += 1
            cur_susp = susp
            lines_with_cur_rank.clear()

        # No matter what, add this line
        lines_with_cur_rank.add(line)

    # Add lines with the last rank that didn't get added in the loop
    for l in lines_with_cur_rank:
        line_to_rank[l] = cur_rank

    assert len(line_to_rank) == len(suspiciousness)
    line_to_rank_ser = pd.Series(line_to_rank)
    line_to_rank_ser.sort_values(inplace=True)
    return line_to_rank_ser


def get_suspicious_lines(run_to_result):
    passing_spectra = []
    failing_spectra = []
    for passing, spectrum in run_to_result.values():
        if passing:
            passing_spectra.append(spectrum)
        else:
            failing_spectra.append(spectrum)

    assert len(passing_spectra) > 0
    assert len(failing_spectra) > 0
    suspiciousness = _compute_suspiciousness(passing_spectra,
                                             failing_spectra)
    ranks = _get_statement_ranks(suspiciousness)

    return ranks, suspiciousness
