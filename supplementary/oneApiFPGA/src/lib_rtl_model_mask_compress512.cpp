//==============================================================
// Copyright Intel Corporation
//
// SPDX-License-Identifier: MIT
// =============================================================

/*
###############################
## Created: Intel Corporation 
##	Piotr Ratuszniak	
##      January  2023
###############################
*/

#include <CL/sycl.hpp>
#include <array>

SYCL_EXTERNAL extern "C" std::array<uint64_t,8>  MaskCompress512(std::array<uint64_t,8> datain_src, std::array<uint64_t,8> datain_a, uint8_t maskin) {
  return datain_a; 
}
