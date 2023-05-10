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

SYCL_EXTERNAL extern "C" unsigned Lzc32Uint(unsigned int a) {
  return a+1; 
}
