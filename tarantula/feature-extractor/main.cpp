#include <iostream>
#include <vector>
#include <cassert>
#include <string>

#include <cstdlib>
#include <iostream>
#include <ctime>
#include <fstream>
#include <map>
#include <json.hpp>

#include "run_result.h"
#include "feature_vec.h"
#include "feature_computer.h"
#include "pairwise_feature_computer.h"


using json = nlohmann::json;
using std::vector;
using std::map;
using std::string;
using std::endl;



std::map<int, RunResult> load_spectra(const string& fname) {
    std::ifstream in(fname, std::ios::in);
    
    json j;
    in >> j;

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

    json j = json::object();
    for (auto& it : feature_vecs) {
        json vec(it.second.features);
        j[std::to_string(it.first)] = vec;
    }
    
    std::ofstream out(outfile, std::ios::out);
    out << j;
}

void save_single_line_features(
    const PairWiseFeatureComputer::FeatureMap& featuremap,
    const string& outfile) {
    json j = json::object();

    json keyind(PairWiseFeatureComputer::KEY_INDEX);
    j["key_index"] = keyind;
    std::cout << "here\n\n\n";
    j["feature_map"] = PairWiseFeatureComputer::
        feature_map_to_json(featuremap);

    std::ofstream out(outfile, std::ios::out);
    out << j;
}
    
                               

int main(int argc, char** argv) {
    if (argc < 4) {
        std::cout << "Usage is " << argv[0] << " input-spectra-file "
                  << "output-feature-file " << "pairwise|normal" << endl;
        return 0;
    }

    string spectra_file(argv[1]);
    string feature_file(argv[2]);
    string is_pairwise(argv[3]);

    std::cout << "Loading spectra from " << spectra_file << endl;
    std::map<int, RunResult> test_to_res = load_spectra(spectra_file);

    
    if (is_pairwise == "normal") {
        map<int, FeatureVec> feature_vecs = compute_passing_features(test_to_res);
        save_features(feature_vecs, feature_file);
    } else if (is_pairwise == "pairwise") {
        auto fmap = PairWiseFeatureComputer::compute_differences(test_to_res);
        save_single_line_features(fmap, feature_file);
    } else {
        assert(0 && "wrong arg");
    }

    return 0;
}
