import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import evaluator
import tarantula
import feature_computer
import run_result_provider
import spectra_filter

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


    x_axis = list(np.arange(1.0, 0.0, -0.1))
    for cutoff in x_axis:
        ranker_obj = tarantula.TarantulaRanker()
        filter_obj = spectra_filter.SingleFailingDistanceFilter(feature_obj,
                                                                'normalized_hamming',
                                                                cutoff)
        provider = run_result_provider.SingleFailingProvider([947, 928, 134, 997])

        results = evaluator.get_ranker_results_with_objs(project_name,
                                                         version,
                                                         ranker_obj,
                                                         filter_obj,
                                                         provider)

        scores = pd.Series({ver:rank_res.score if rank_res else 0.0
                            for ver,rank_res
                            in results.items()})
        score_mat[cutoff] = scores

    return score_mat


def main():
    score_mat = get_score_mat()
    print(score_mat)
    
    x_axis = list(score_mat.columns)
    print(x_axis)
    for k in INTERESTING_KEYS:
        y_axis = score_mat.loc[k].values
        print(y_axis)
        plt.plot(x_axis, y_axis, 'ro')
        plt.title(k)
        plt.xlabel("Distance cutoff")
        plt.ylabel("ratio of program not looked at")
        plt.show()


    

if __name__ == "__main__":
    main()
