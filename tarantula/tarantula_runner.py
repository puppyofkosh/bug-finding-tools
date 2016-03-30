import tarantula
import evaluator

def get_tarantula_results(run_to_result, filter_obj, buggy_lines):
    passing_spectra, failing_spectra = filter_obj.filter_tests(run_to_result)

    if len(passing_spectra) == 0 or len(failing_spectra) == 0:
        return None, None, None, None

    ranks, suspiciousness = tarantula.get_suspicious_lines(passing_spectra,
                                                           failing_spectra)

    line, score = evaluator.get_score(ranks, buggy_lines)

    return (ranks, suspiciousness, line, score)
