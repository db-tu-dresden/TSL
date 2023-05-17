cmake_minimum_required(VERSION 3.16)
project(OneAPIFPGAtoCpp)

include(one_api_lib_create.cmake)

#This macro must be called for every object file that should be compiled
register_one_api_fpga_object(
  NAME "rtl_lzc32"
  SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/src/lib_rtl_model_lzc32.cpp
  SPECS ${CMAKE_CURRENT_SOURCE_DIR}/specs/lib_rtl_spec_lzc32.xml
)

#This macro must be called only once to create the library
create_one_api_fpga_library(
  NAME libtslOneAPIFPGA
)

add_dependencies(${CMAKE_PROJECT_NAME} ${ONE_API_FPGA_LIBRARY_TARGET})