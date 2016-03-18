# This file evaluates how good a ranking that's produced by tarantula
# is It takes in a dictionary of line num -> rank, as well as a set of
# lines which are known to have the bug (often, just one line num) and
# finds the "score"
# The score is the percent of the program (percent of executable lines we'll say)
# which you would NOT have to look at if you followed tarantula's output.
# This returns the best score of all the line numbers in the set


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

