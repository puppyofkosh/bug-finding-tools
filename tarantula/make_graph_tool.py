import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import evaluator
import tarantula
import feature_computer
import run_result_provider
import spectra_filter
import pd_helper

INTERESTING_KEYS = [
    "totinfo-v13-947",
    "totinfo-v13-928",
    "totinfo-v13-134",
    "totinfo-v13-997"
]





def get_score_mat():
    project_name = "totinfo"
    version = "v13"
    feature_obj = feature_computer.get_feature_vecs(project_name,
                                                    version)
    score_mat = pd.DataFrame()
    x_axis = list(np.arange(1.0, 0.0, -0.05))
    for cutoff in x_axis:
        ranker_obj = tarantula.TarantulaRanker()
        filter_obj = spectra_filter.SingleFailingDistanceFilter(
            feature_obj,
            "inv_common_execd_over_passing",
            cutoff)
        provider = run_result_provider.SingleFailingProvider()

        results = evaluator.get_ranker_results_with_objs(project_name,
                                                         version,
                                                         ranker_obj,
                                                         filter_obj,
                                                         provider)

        scores = pd.Series({ver:rank_res.score if rank_res else 0.0
                            for ver,rank_res
                            in results.items()})
        assert scores.max() <= 1.0
        score_mat[cutoff] = scores

    return score_mat.transpose()


def main():
    score_mat = get_score_mat()
    pd_helper.print_df(score_mat)
    
    x_axis = list(score_mat.index)
    average_values = np.zeros(len(x_axis))
    for k in score_mat.columns:
        y_axis = score_mat[k].values
        average_values += y_axis
        plt.plot(x_axis, y_axis, '-')
    average_values /= len(score_mat.columns)

    plt.title("Distance cutoff v performance")
    plt.xlabel("Distance cutoff")
    plt.ylabel("ratio of program not looked at")
    plt.ylim((0.0,1.0))
    plt.show()

    # Plot the average performance
    print("Avg values {0}".format(average_values))
    plt.plot(x_axis, average_values, '-')
    plt.title("Distance cutoff v avg performance")
    plt.xlabel("Distance cutoff")
    plt.ylabel("ratio of program not looked at")
    plt.ylim((0.0,1.0))
    plt.show()

    # Plot median performance
    median = score_mat.median(axis=1)
    plt.plot(x_axis, median, '-')
    plt.title("Distance cutoff v median performance")
    plt.xlabel("Distance cutoff")
    plt.ylabel("ratio of program not looked at")
    plt.ylim((0.0,1.0))
    plt.show()

    

if __name__ == "__main__":
    main()
