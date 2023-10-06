# CMakeFile for building the example(s).
# The following parameters can be passed to cmake:
# BOARD: name of fpga board [intel_s10sx_pac:pac_s10_usm]

cmake_minimum_required(VERSION 3.13)
project(oneAPIfpgaExamples)


set(TSLROOT ${CMAKE_SOURCE_DIR}/../..)

set(CMAKE_VERBOSE_MAKEFILE ON)

set(project_cxx_standard 20)
set(release_cxx_flag "-O2")

set(warnings "-Wall;-Wextra;-Wpedantic")
set(release_warnings "-Winline")

if (DEFINED BOARD)
  set(fpga_board ${BOARD})
else()
  set(fpga_board "intel_s10sx_pac:pac_s10_usm")
endif()

set(fpga_link_options -qactypes -fsycl -fintelfpga)

# generate the TSL (with SSE, AVX, AVX512, ONEAPIfpga) assuming Intel Xeon Gold Cascade Lake (e.g., Xeon Gold 6238R)
include(${TSLROOT}/tsl.cmake)
create_tsl(
  TSLGENERATOR_DIRECTORY "${TSLROOT}"
  DESTINATION "${CMAKE_BINARY_DIR}/tsl"
	TARGETS_FLAGS "sse;sse2;ssse3;sse4_1;sse4_2;avx;avx2;avx512f;avx512dq;avx512cd;avx512bw;avx512vl;avx512_vnni;bmi1;bmi2;oneAPIfpgaDev"
  USE_CONCEPTS
	LINK_OPTIONS ${fpga_link_options}
)
#create_tsl(
#  TSLGENERATOR_DIRECTORY "${TSLROOT}"
#  DESTINATION "${CMAKE_BINARY_DIR}/tsl"
#	TARGETS_FLAGS "oneAPIfpgaDev"
#  USE_CONCEPTS
#	LINK_OPTIONS ${fpga_link_options}
#)
message(STATUS "TSL Include Directory: ${TSL_INCLUDE_DIRECTORY}")


########################################################
## Build emulator 
########################################################
function(create_fpga_emulator_target targetName mainFile)
  set(exec_target_name ${targetName}.fpga.emu)
  add_executable(${exec_target_name} ${mainFile})
  target_include_directories(${exec_target_name} PRIVATE ${TSL_INCLUDE_DIRECTORY})
  target_link_libraries(${exec_target_name} PRIVATE tsl)
  set_target_properties(${exec_target_name} PROPERTIES CXX_STANDARD ${project_cxx_standard})
  target_compile_options(${exec_target_name} PRIVATE -fsycl ${release_cxx_flag} ${warnings} ${release_warnings} -fintelfpga -qactypes)
  target_link_options(${exec_target_name} PRIVATE ${fpga_link_options})
endfunction()

########################################################
## Build hardware
########################################################
function(create_fpga_target targetName mainFile)
  set(exec_target_name ${targetName}.fpga)
  add_executable(${exec_target_name} ${mainFile})
  target_include_directories(${exec_target_name} PRIVATE ${TSL_INCLUDE_DIRECTORY})
  target_link_libraries(${exec_target_name} tsl)
  target_link_libraries(${exec_target_name} libtslOneAPIFPGA)
  set_target_properties(${exec_target_name} PROPERTIES CXX_STANDARD ${project_cxx_standard})
  target_compile_definitions(${exec_target_name} PRIVATE ONEAPI_FPGA_HARDWARE)
  target_compile_options(${exec_target_name} PRIVATE -fsycl ${release_cxx_flag} ${warnings} ${release_warnings} -fintelfpga -Xsoutput-report-folder=${targetName}.prj -qactypes)
  target_link_options(${exec_target_name} PRIVATE -qactypes -fsycl -fintelfpga -Xshardware -Xsboard=${fpga_board} -reuse-exe=${CMAKE_CURRENT_BINARY_DIR}/${exec_target_name}) 
endfunction()

if(NOT DEFINED ${TARGET})
  message(STATUS "No target specified. Assuming emulator")
  set(TARGET EMULATOR)
endif()
if(${TARGET} STREQUAL "EMULATOR")
  create_fpga_emulator_target(clz_rtl clz_rtl_example.cpp)
elif(${TARGET} STREQUAL "FPGA_HARDWARE")
  create_fpga_target(clz_rtl clz_rtl_example.cpp)
endif()
