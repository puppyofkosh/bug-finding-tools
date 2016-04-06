#include <assert.h>
#include <vector>
#include <iostream>

using std::vector;



void test_ulam() {
    vector<int> v = {1,2,3,4,5};
    vector<int> v2 = {5,2,1,4,3};

    assert(longest_common_subsequence(v,v2) == 2);
    
    vector<int> v3 = {'X', 'M', 'J', 'Y', 'A', 'U', 'Z'};
    vector<int> v4 = {'M', 'Z', 'J', 'A', 'W', 'X', 'U'};

    // From wikipedia
    assert(longest_common_subsequence(v3, v4) == 4);

    // From some bullshit website
    vector<int> v5 = {'A', 'B', 'C', 'D', 'G', 'H'};
    vector<int> v6 = {'A', 'E', 'D', 'F', 'H', 'R'};
    assert(longest_common_subsequence(v5, v6) == 3);

    vector<int> v7;
    vector<int> v8;
    assert(longest_common_subsequence(v7, v8) == 0);
}

