# This file contains the actual implementation of tarantula

import pandas as pd

def _sum_spectra(spectr):
    df = pd.DataFrame({i: spec for i,spec in enumerate(spectr)})
    # Sum all columns of dataframe
    total = df.sum(axis=1)
    return total.sort_values(ascending=False)


def _compute_suspiciousness(passing_spectra, failing_spectra):
    assert all(p.max() == 1 for p in passing_spectra)
    assert all(f.max() == 1 for f in failing_spectra)

    failing_counts = _sum_spectra(failing_spectra)
    passing_counts = _sum_spectra(passing_spectra)

    total_failed = len(failing_spectra)
    total_passed = len(passing_spectra)

    assert total_failed > 0 and total_passed > 0

    # Now we get the suspiciousness of each line
    failing_counts /= float(total_failed)
    passing_counts /= float(total_passed)

    assert not passing_counts.isnull().values.any()
    assert not failing_counts.isnull().values.any()

    denom = failing_counts.add(passing_counts, fill_value=0)
    suspiciousness = failing_counts.mul(1.0 / denom, fill_value=0)
    # In case we just divided by 0 (a line is executable, but never executed)
    # give it suspiciousness of 0
    suspiciousness.fillna(0, inplace=True)
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
