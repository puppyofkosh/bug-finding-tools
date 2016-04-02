#ifndef FEATURE_VEC_H
#define FEATURE_VEC_H

#include <map>
#include <string>

#include <json.hpp>

using json = nlohmann::json;
using std::map;
using std::string;

struct FeatureVec {
    map<string, double> features;

    FeatureVec(map<string, double>&& f)
        :features(std::move(f)) {
    }

    FeatureVec(FeatureVec&& f) noexcept {
        features = std::move(f.features);
    }

    FeatureVec(const FeatureVec& f) {
        features = f.features;
    }

    json to_json() {
        json j(features);
        return j;
    }
};

#endif
