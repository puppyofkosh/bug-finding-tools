#ifndef ULAM_H
#define ULAM_H

#include <assert.h>
#include <algorithm>
#include <vector>
#include <iostream>

template<class T>
int longest_common_subsequence(const std::vector<T>& a,
                               const std::vector<T>& b) {
    assert(a.size() == b.size());

    std::vector<int> prevRow(a.size() + 1, 0);
    std::vector<int> curRow(a.size() + 1, 0);

    for (size_t row = 0; row <= a.size(); row++) {
        std::swap(prevRow, curRow);
        for (size_t col = 0; col <= a.size(); col++) {
            if (row == 0 || col == 0)
                curRow[col] = 0;
            else if (a[col - 1] == b[row - 1])
                curRow[col] = prevRow[col - 1] + 1;
            else
                curRow[col] = std::max(curRow[col - 1], prevRow[col]);
        }
    }

    int ret = (int)curRow[curRow.size() - 1];
    return ret;
}


int ulam_distance(const std::vector<T>& a, const std::vector<T>& b) {
    assert(a.size() == b.size());

    return a.size() - longest_common_subsequence(a, b);
}

void test_ulam();

#endif
