import os

from commandio import get_output

def _run_gcov(filename):
    _ = get_output(["gcov", filename])

def reset_gcov_counts(filepath):
    filename, extension = os.path.splitext(filepath)
    assert extension == ".c"

    # Remove the data file 
    os.remove(filename + ".gcda")


def _parse_gcov_output(filename):
    line_to_exec_count = {}
    with open(filename) as f:
        for line in f:
            line_split = line.strip().split(":")

            # exec count: line num: source code (which may contain :)
            assert len(line_split) >= 3
            

            line_num = int(line_split[1].strip())
            if line_num == 0:
                # Line 0 contains special data output by gcov
                # which we don't care about
                continue

            exec_count_str = line_split[0].strip()
            if exec_count_str in ["-", "===="]:
                continue

            assert line_num not in line_to_exec_count            
            if exec_count_str == "#####":
                # Special value which indicates it is an executable line
                # but is never reached
                line_to_exec_count[line_num] = 0
                continue

            line_to_exec_count[line_num] = int(exec_count_str)
    return line_to_exec_count


# Run gcov to get execution trace of the program when it ran
def get_trace(filename):
    _run_gcov(filename)
    return _parse_gcov_output(filename + ".gcov")
