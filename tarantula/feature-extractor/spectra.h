#ifndef SPECTRA_H
#define SPECTRA_H

#include <vector>
#include <Eigen/Dense>



typedef Eigen::VectorXi Spectrum;
//typedef Eigen::VectorXd DSpectrum;


Spectrum get_intersection_of_spectra(const std::vector<Spectrum>& spectra);

void get_common_execd(const Spectrum& a,
                      const Spectrum& b,
                      int* n_a_execd,
                      int* n_b_execd,
                      int* n_common_execd,
                      int* n_common_not_execd);

#endif
