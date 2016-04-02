#include <map>

using std::map;

class FeatureVec;
class RunResult;

map<int, FeatureVec> compute_passing_features(
    const map<int, RunResult >& test_to_res);
