#include <vector>
#include <map>

#include "feature_vec.h"
#include "run_result.h"
#include "spectra.h"

using json = nlohmann::json;
using std::vector;
using std::map;
using std::string;
using std::endl;


void add_min_max_features(const Spectrum& spectrum,
                          const vector<Spectrum>& failing,
                          map<string, double>& features) {
    int max_common = -1;
    double max_common_over_failing = 0.0;
    double max_common_over_passing = 0.0;

    int min_common = -1;
    double min_common_over_passing = 0.0;
    double min_common_over_failing = 0.0;
    
    double avg_common_over_passing = 0;
    double avg_common_over_failing = 0;

    // ne = note executed
    int max_common_ne = -1;
    int min_common_ne = -1;
    double max_common_ne_over_failing = 0.0;
    double max_common_ne_over_passing = 0.0;
    double min_common_ne_over_failing = 0.0;
    double min_common_ne_over_passing = 0.0;
    double avg_common_ne_over_passing = 0.0;
    double avg_common_ne_over_failing = 0.0;
        

    for (size_t i = 0; i < failing.size(); i++) {
        int nfailing_execd_i = 0;
        int npassing_execd_i = 0;
        int ncommon_execd = 0;
        int ncommon_not_execd = 0;
        assert(failing[i].size() == spectrum.size());

        get_common_execd(spectrum, failing[i],
                         &npassing_execd_i, &nfailing_execd_i,
                         &ncommon_execd, &ncommon_not_execd);
        
        const double nfailing_execd = double(nfailing_execd_i);
        const double npassing_execd = double(npassing_execd_i);

        avg_common_over_failing += ncommon_execd / nfailing_execd;
        avg_common_over_passing += ncommon_execd / npassing_execd;


        if (ncommon_execd > max_common) {
            max_common = ncommon_execd;
            max_common_over_failing = ncommon_execd / nfailing_execd;
            max_common_over_passing = ncommon_execd / npassing_execd;
        }

        if (ncommon_execd < min_common || min_common == -1) {
            min_common = ncommon_execd;
            min_common_over_failing = ncommon_execd / nfailing_execd;
            min_common_over_passing = ncommon_execd / npassing_execd;
        }

        avg_common_ne_over_failing += ncommon_not_execd / nfailing_execd;
        avg_common_ne_over_passing += ncommon_not_execd / npassing_execd;

        if (ncommon_not_execd > max_common_ne) {
            max_common_ne = ncommon_not_execd;
            max_common_ne_over_passing = max_common_ne / npassing_execd;
            max_common_ne_over_failing = max_common_ne / nfailing_execd;
        }

        if (ncommon_not_execd < min_common_ne || min_common_ne == -1) {
            min_common_ne = ncommon_not_execd;
            min_common_ne_over_passing = min_common_ne / npassing_execd;
            min_common_ne_over_failing = min_common_ne / nfailing_execd;
        }
    }

    assert(max_common >= 0);
    avg_common_over_failing /= failing.size();
    avg_common_over_passing /= failing.size();

    features.insert({"avg_common_over_failing", avg_common_over_failing});
    features.insert({"min_common_over_failing", min_common_over_failing});
    features.insert({"max_common_over_failing", max_common_over_failing});
    features.insert({"avg_common_over_passing", avg_common_over_passing});
    features.insert({"min_common_over_passing", min_common_over_passing});
    features.insert({"max_common_over_passing", max_common_over_passing});

    avg_common_ne_over_passing /= failing.size();
    avg_common_ne_over_failing /= failing.size();

    features.insert({"avg_common_ne_over_failing", avg_common_ne_over_failing});
    features.insert({"min_common_ne_over_failing", min_common_ne_over_failing});
    features.insert({"max_common_ne_over_failing", max_common_ne_over_failing});
    features.insert({"avg_common_ne_over_passing", avg_common_ne_over_passing});
    features.insert({"min_common_ne_over_passing", min_common_ne_over_passing});
    features.insert({"max_common_ne_over_passing", max_common_ne_over_passing});
}

void add_intersection_features(const Spectrum& spectrum,
                               const Spectrum& failing_intersection,
                               map<string, double>& features) {
    // Get the percent of "intersection" statements this passing
    // tests executed
    int nfailing_intersection = 0;
    int ncommon_with_intersection = 0;
    int ncommon_not_execd_with_intersection = 0;
    get_common_execd(spectrum, failing_intersection,
                     nullptr,
                     &nfailing_intersection,
                     &ncommon_with_intersection,
                     &ncommon_not_execd_with_intersection);

    double passing_over_intersection =
        double(ncommon_with_intersection) / nfailing_intersection;
    double passing_not_execd_over_intersection =
        double(ncommon_not_execd_with_intersection) / nfailing_intersection;

    // How big intersection of failing tests is relative to total number
    // of executable statements
    double intersection_size = double(nfailing_intersection) / spectrum.size();

    features.insert({"common_over_intersection", passing_over_intersection});
    features.insert({"common_ne_over_intersection",
                passing_not_execd_over_intersection});
}

map<int, FeatureVec> compute_passing_features(
    const map<int, RunResult >& test_to_res) {

    vector<Spectrum> passing, failing;
    for(auto it = test_to_res.begin(); it != test_to_res.end(); it++) {
        if (it->second.passed) {
            passing.push_back(it->second.get_spectrum_vec());
        } else {
            failing.push_back(it->second.get_spectrum_vec());
        }
    }

    // Lines which are executed by every failing test case
    Spectrum failing_intersection = get_intersection_of_spectra(failing);

    map<int, FeatureVec> test_to_feature;
    for (auto& it : test_to_res) {
        if (!it.second.passed)
            continue;

        Spectrum spectrum = it.second.get_spectrum_vec();

        map<string, double> features;
        add_min_max_features(spectrum, failing, features);
        add_intersection_features(spectrum, failing_intersection,
                                  features);

        FeatureVec f(std::move(features));
        test_to_feature.insert(std::make_pair(it.first, f));
    }
    return test_to_feature;
}
