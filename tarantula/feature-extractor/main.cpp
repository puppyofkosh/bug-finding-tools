#include <iostream>
#include <vector>
#include <cassert>
#include <string>

#include <cstdlib>
#include <iostream>
#include <ctime>
#include <fstream>
#include <map>

#include "json.hpp"

using json = nlohmann::json;
using std::vector;
using std::map;
using std::string;
using std::endl;

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

    vector<int> get_spectrum_vec() const {
        // This relies on the iteration order of std::map
        std::vector<int> vec;
        for (auto it : spectrum) {
            vec.push_back(it.second);
        }
        return vec;
    }
};

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


FeatureVec compute_features(const vector<int>& spectrum,
                                  const vector<vector<int> >& failing) {

    int max_common = -1;
    double max_over_failing = 0.0;
    double max_over_passing = 0.0;

    int min_common = -1;
    double min_over_passing = 0.0;
    double min_over_failing = 0.0;
    
    double avg_over_passing = 0;
    double avg_over_failing = 0;
    for (size_t i = 0; i < failing.size(); i++) {
        int nfailing_execd = 0;
        int npassing_execd = 0;
        int ncommon_execd = 0;

        assert(failing[i].size() == spectrum.size());
        
        auto f = failing[i];
        for (size_t j = 0; j < spectrum.size(); j++) {
            if (f[j] > 0)
                nfailing_execd++;
            if (spectrum[j] > 0)
                npassing_execd++;
            if (f[j] > 0 && spectrum[j] > 0)
                ncommon_execd++;
        }

        avg_over_failing += ncommon_execd / double(nfailing_execd);
        avg_over_passing += ncommon_execd / double(npassing_execd);

        if (ncommon_execd > max_common) {
            max_common = ncommon_execd;
            max_over_failing = ncommon_execd / double(nfailing_execd);
            max_over_passing = ncommon_execd / double(npassing_execd);
        }

        if (ncommon_execd < min_common || min_common == -1) {
            min_common = ncommon_execd;
            min_over_failing = ncommon_execd / double(nfailing_execd);
            min_over_passing = ncommon_execd / double(npassing_execd);
        }
    }

    avg_over_failing /= failing.size();
    avg_over_passing /= failing.size();

    assert(max_common >= 0);

    map<string, double> features = {
        {"avg_common_over_failing", avg_over_failing},
        {"min_common_over_failing", min_over_failing},
        {"max_common_over_failing", max_over_failing},
        {"avg_common_over_passing", avg_over_passing},
        {"min_common_over_passing", min_over_passing},
        {"max_common_over_passing", max_over_passing}
    };

    return FeatureVec(std::move(features));
}

map<int, FeatureVec> compute_passing_features(
    const map<int, RunResult >& test_to_res) {

    vector<vector<int> > passing, failing;
    for(auto it = test_to_res.begin(); it != test_to_res.end(); it++) {
        if (it->second.passed) {
            passing.push_back(it->second.get_spectrum_vec());
        } else {
            failing.push_back(it->second.get_spectrum_vec());
        }
    }

    map<int, FeatureVec> test_to_feature;
    for (auto& it : test_to_res) {
        if (!it.second.passed)
            continue;

        vector<int> spectrum = it.second.get_spectrum_vec();
        FeatureVec f = compute_features(spectrum, failing);
        test_to_feature.insert(std::make_pair(it.first, f));
    }
    return test_to_feature;
}

std::map<int, RunResult> load_spectra(const string& fname) {
    std::ifstream in(fname, std::ios::in);
    
    json j;
    in >> j;

    std::cout << "Size is " << j.size() << endl;

    std::map<int, RunResult> test_to_res;
    for (json::iterator it = j.begin(); it != j.end(); ++it) {
        int k = std::stoi(it.key());

        RunResult res(it.value());
        test_to_res.insert(std::make_pair(k, res));
    }

    return test_to_res;
}

void save_features(const map<int, FeatureVec>& feature_vecs,
                   const string& outfile) {
    // TODO: Find a better way of doing this?
    // need to overide operator<< probably

    map<int, map<string, double> > outvals;
    json j = json::object();
    for (auto& it : feature_vecs) {
        json vec(it.second.features);
        j[std::to_string(it.first)] = vec;
    }
    
    std::ofstream out(outfile, std::ios::out);
    out << j;
}

int main(int argc, char** argv) {
    if (argc < 3) {
        std::cout << "Usage is " << argv[0] << " input-spectra-file "
                  << "output-feature-file" << endl;
        return 0;
    }

    string spectra_file(argv[1]);
    string feature_file(argv[2]);

    std::cout << "Loading spectra from " << spectra_file << endl;
    std::map<int, RunResult> test_to_res = load_spectra(spectra_file);

    
    map<int, FeatureVec> feature_vecs = compute_passing_features(test_to_res);
    save_features(feature_vecs, feature_file);

    return 0;
}
