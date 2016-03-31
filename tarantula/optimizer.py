import scipy.optimize

import projects
import feature_computer
import tarantula
import evaluator
import spectra_filter


def evaluation_fn(project_name, initial_scores,
                  classify_vector, cutoff):
    print("Evaluating with cutoff {0} classify {1}".format(cutoff,
                                                           classify_vector))
    scoresum = 0
    ver = None
    for version in projects.get_version_names(project_name):
        feature_file = feature_computer.get_feature_file(project_name,
                                                         version)
        features = feature_computer.load(feature_file)

        filter_obj = spectra_filter.DotProductFilter(classify_vector,
                                                     cutoff,
                                                     features)

        ranker_obj = tarantula.IntersectionTarantulaRanker()
        rank_res = evaluator.get_ranker_results(project_name,
                                                version,
                                                ranker_obj,
                                                filter_obj)
        if rank_res is None:
            continue

        score = rank_res.score
        scorediff = score - initial_scores[version]
        if score > 0.8:
            ver = version
            scoresum = max(scoresum, scorediff)

    print("Score is {0} for version: {1}".format(scoresum, ver))
    return scoresum


def optimize_classifier(project_name):
    initial_scores = {}
    for version in projects.get_version_names(project_name):
        filter_obj = spectra_filter.TrivialFilter()
        rank_res = evaluator.get_ranker_results(project_name,
                                                version,
                                                filter_obj)
        initial_scores[version] = rank_res.score

    def to_optimize(classify_vector_with_cutoff):
        cutoff = classify_vector_with_cutoff[-1]
        classify_vector = classify_vector_with_cutoff[:-1]

        score = evaluation_fn(project_name, initial_scores,
                              classify_vector, cutoff)
        # minimize negative
        return -1 * score

    vecsize = 7 + 1
    lower = [-1.0 for i in range(vecsize)]
    upper = [1.0 for i in range(vecsize)]
    x0 = [0.1 for i in range(vecsize)]

    res = scipy.optimize.anneal(to_optimize, x0,
                                maxiter=1,
                                maxeval=1,
                                dwell=1,
                                full_output=True)
    print(res)
