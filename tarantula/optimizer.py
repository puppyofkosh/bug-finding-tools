import scipy.optimize
import main
import projects
import feature_computer
import spectra_filter


def evaluation_fn(project_name, classify_vector, cutoff):
    print("Evaluating with cutoff {0} classify {1}".format(cutoff,
                                                           classify_vector))
    scoresum = 0
    for version in projects.get_version_names(project_name):
        feature_file = main.get_feature_file(project_name, version)
        features = feature_computer.load(feature_file)

        filter_obj = spectra_filter.DotProductFilter(classify_vector,
                                                     cutoff,
                                                     features)
        (ranks,
         suspiciousness,
         line,
         score) = main.get_tarantula_results(project_name, version,
                                             filter_obj)
        if score is None:
            continue
        if score >= 0.8:
            scoresum += 1

    print("Score is {0}".format(scoresum))
    return scoresum

    


def optimize_classifier(project_name):
    def to_optimize(classify_vector_with_cutoff):
        cutoff = classify_vector_with_cutoff[-1]
        classify_vector = classify_vector_with_cutoff[:-1]
        
        score = evaluation_fn(project_name, classify_vector, cutoff) 
        # minimize negative
        return -1 * score
    
    vecsize = 7 + 1
    lower = [-1.0 for i in range(vecsize)]
    upper = [1.0 for i in range(vecsize)]
    x0 = [0.1 for i in range(vecsize)]

    res = scipy.optimize.anneal(to_optimize, x0,
                                maxiter=1,
                                maxeval=2,
                                dwell=2,
                                full_output=True)
    print(res)
