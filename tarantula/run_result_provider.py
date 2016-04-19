# Provides an extra layer of abstraction for getting each run result
# If we want to evaluate tarantula using all the available failing test
# cases just use the TrivialProvider
# If we want to evaluate tarantula giving it only one failing test
# at a time, we use the SingleFailingProvider



class TrivialProvider(object):
    def get_run_results(self, run_to_result):
        return [("all", run_to_result)]


class SingleFailingProvider(object):
    def get_run_results(self, run_to_result):
        failing_tests = [run for run,res in run_to_result.items() if 
                         not res.passed]

        for failing_run in failing_tests:
            # All passing tests, and this one failing test, but no others.
            new_run_res = {run: res for run,res in run_to_result.items()
                           if res.passed or run == failing_run}
            yield (failing_run, new_run_res)
