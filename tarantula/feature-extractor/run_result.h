#ifndef RUN_RESULT_H
#define RUN_RESULT_H

#include <map>
#include <vector>

#include <json.hpp>

using std::vector;
using json = nlohmann::json;

//typedef vector<int> Spectrum;

#include <Eigen/Dense>
typedef Eigen::VectorXd Spectrum;

struct RunResult {
    std::map<int, int> spectrum;
    bool passed;

    RunResult(const json& j) {
        passed = j["passed"];
        json s = j["spectrum"];

        for (json::const_iterator it = s.begin(); it != s.end(); ++it) {
            int line = std::stoi(it.key());
            int executed = it.value().get<int>();
            spectrum.insert(std::make_pair(line, executed));
        }
    }

    Spectrum get_spectrum_vec() const {
        // This relies on the iteration order of std::map
        Spectrum vec(spectrum.size());

        size_t i = 0;
        for (auto it : spectrum) {
            vec[i++] = it.second;
        }
        return vec;
    }

    vector<int> get_key_vec() const {
        std::vector<int> vec;
        for (auto it: spectrum) {
            vec.push_back(it.first);
        }
        return vec;
    }
};

#endif
