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



using json = nlohmann::json;
using std::vector;
using std::map;
using std::string;
using std::endl;



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
