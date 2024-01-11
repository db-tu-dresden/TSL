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
  
   uint32_t mask = 1 << 31;  
   uint32_t lzc = 0;

   if (a == 0)
      lzc = 32;	   
   else
      while ((mask & a) == 0)  {
         mask = mask >> 1;
         lzc = lzc +1;
      }  
  
   return lzc; 
}
