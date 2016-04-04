#include <vector>

#include "spectra.h"

using std::vector;

Spectrum get_intersection_of_spectra(const vector<Spectrum>& spectra) {
    Spectrum intersection(spectra[0].size());
    for (const auto& s : spectra)
        intersection += s;

    for (size_t i = 0; i < intersection.size(); i++)
        if (intersection[i] < spectra.size())
            intersection[i] = 0;

    return intersection;
}

void get_common_execd(const Spectrum& a,
                      const Spectrum& b,
                      int* n_a_execd,
                      int* n_b_execd,
                      int* n_common_execd,
                      int* n_common_not_execd) {
    int na = 0;
    int nb = 0;
    int ncommon = 0;
    int n_notcommon = 0;

    assert(a.size() == b.size());
    for (size_t j = 0; j < a.size(); j++) {
        if (a[j] > 0)
            na++;
        if (b[j] > 0)
            nb++;
        if (a[j] > 0 && b[j] > 0)
            ncommon++;
        if (a[j] == 0 && b[j] == 0)
            n_notcommon++;
    }
    if (n_a_execd)
        *n_a_execd = na;
    if (n_b_execd)
        *n_b_execd = nb;
    if (n_common_execd)
        *n_common_execd = ncommon;
    if (n_common_not_execd)
        *n_common_not_execd = n_notcommon;
}
