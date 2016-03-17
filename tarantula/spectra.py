import pandas as pd

def _sum_spectra(spectra):
    total = pd.Series()
    for spectrum in spectra:
        ser = pd.Series(spectrum)
        total = total.add(ser, fill_value=0)
    return total

def compute_suspiciousness(passing_spectra, failing_spectra):
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


# Makes a binary spectrum
def make_spectrum_from_trace(trace):
    spectrum = {line: 1 if count > 0 else 0
                for line, count in trace.iteritems()}
    return spectrum

def get_statement_ranks(suspiciousness):
    assert len(suspiciousness) > 0
    assert suspiciousness.max() < 1.0 and suspiciousness.min() >= 0
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


# Return the BEST score tarantula got of any of the buggy line nums
# Score is defined as amount of program we wouldn't have to look at
# This is the number of lines with rank higher than this line / total linecount
def get_score(line_to_rank_ser, buggy_line_nums):
    
    best_line = None
    best_score = None
    for l in buggy_line_nums:
        if l not in line_to_rank_ser:
            continue
        
        rank = line_to_rank_ser[l]
        others = line_to_rank_ser[line_to_rank_ser > rank]
        score = len(others) / float(len(line_to_rank_ser))
        if best_line is None or score > best_score:
            best_line = l
            best_score = score

    # They should pass in at least one valid line
    assert best_line is not None
    return best_line, best_score
