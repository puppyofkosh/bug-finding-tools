#ifndef PAIRWISE_FEATURE_COMPUTER
#define PAIRWISE_FEATURE_COMPUTER

#include <vector>
#include <string>
#include <map>
#include <cassert>
#include <json.hpp>

#include "spectra.h"
#include "run_result.h"

using json = nlohmann::json;

namespace PairWiseFeatureComputer {

    typedef std::map<int, std::map<int, std::vector<double> > > FeatureMap;

    json feature_map_to_json(const FeatureMap& fmap) {
        json j = json::object();
        for (auto& failing_it : fmap) {
            string fail_test = std::to_string(failing_it.first);
            j[fail_test] = json::object();
            for (auto &passing_it : failing_it.second) {
                json fvec(passing_it.second);
                j[fail_test][std::to_string(passing_it.first)] = fvec;
            }
        }
        return j;
    }

    const std::vector<std::string> KEY_INDEX = {"normalized_hamming",
                                                "common_execd_over_total",
                                                "common_execd_over_failing",
                                                "common_execd_over_passing"};


    std::vector<double> get_features(const Spectrum& failing, const Spectrum& passing) {
        assert(failing.size() == passing.size());

        int num_different = 0;
        int num_common_execd = 0;
        int num_failing_execd = 0;
        int num_passing_execd = 0;
        for (auto i = 0; i < failing.size(); i++) {
            bool f = failing[i] > 0;
            bool p = passing[i] > 0;
            if (f != p)
                num_different++;
            if (f)
                num_failing_execd++;
            if (p)
                num_passing_execd++;
            if (f == p && p)
                num_common_execd++;
        }

        const double vecsize = failing.size();
        double hamming = num_different / vecsize;
        double common_execd_over_total = num_common_execd / vecsize;
        double common_execd_over_failing = num_common_execd /
            double(num_failing_execd);
        double common_execd_over_passing = num_common_execd /
            double(num_passing_execd);

        vector<double> res = {hamming,
                              common_execd_over_total,
                              common_execd_over_failing,
                              common_execd_over_passing};

        assert(res.size() == KEY_INDEX.size());
        return res;
    }


    std::map<int, std::map<int, std::vector<double> > >
        compute_differences(const std::map<int, RunResult>& test_to_res) {
        std::map<int, std::map<int, std::vector<double> > > failing_to_passing_dists;

        std::vector<std::pair<int, Spectrum> > passing, failing;
        for(auto it = test_to_res.begin(); it != test_to_res.end(); it++) {
            std::pair<int, Spectrum> p (it->first,
                                        it->second.get_spectrum_vec());

            if (it->second.passed) {
                passing.push_back(p);
            } else {
                failing.push_back(p);
            }
        }

        for (const auto& fail : failing) {
            std::map<int, std::vector<double> > passing_to_feat;
            for (const auto& pass : passing) {
                std::vector<double> feats = get_features(fail.second, pass.second);
                passing_to_feat.insert({pass.first, feats});
            }
            failing_to_passing_dists.insert({fail.first, passing_to_feat});
        }

        return failing_to_passing_dists;
    }

};

#endif
