cmake_minimum_required(VERSION 3.16)

find_program(ONE_API_FPGA_CROSSGEN fpga_crossgen)
find_program(ONE_API_FPGA_LIBTOOL fpga_libtool)

if(NOT ONE_API_FPGA_CROSSGEN)
  message(FATAL_ERROR "Required executables fpga_crossgen not found")
endif()
if(NOT ONE_API_FPGA_LIBTOOL)
  message(FATAL_ERROR "Required executables fpga_libtool not found")
endif()

set(ONE_API_FPGA_OBJECTS_TARGETS PARENT_SCOPE)
set(ONE_API_FPGA_OBJECTS PARENT_SCOPE)

# This is a CMake macro that creates a custom command and target for generating an FPGA object file
# using the `fpga_crossgen` tool. The macro takes in a `NAME` argument for the name of the object file
# to be generated, and `SOURCES` and `SPECS` arguments for the source and specification files needed
# by `fpga_crossgen`.
function(register_one_api_fpga_object)
  set(options)
  set(oneValueArgs NAME)
  set(multiValueArgs SOURCES SPECS)
  cmake_parse_arguments(REGISTER_AND_BUILD_ONE_API_FPGA_OBJECT "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

  message(STATUS "Inside register_one_api_fpga_object")
  add_custom_command(
    OUTPUT ${REGISTER_AND_BUILD_ONE_API_FPGA_OBJECT_NAME}.o
    COMMAND 
      ${ONE_API_FPGA_CROSSGEN} -v -fPIC ${REGISTER_AND_BUILD_ONE_API_FPGA_OBJECT_SPECS} --emulation_model 
      ${REGISTER_AND_BUILD_ONE_API_FPGA_OBJECT_SOURCES} --target sycl 
      -o ${REGISTER_AND_BUILD_ONE_API_FPGA_OBJECT_NAME}.o
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Running fpga_crossgen for ${REGISTER_AND_BUILD_ONE_API_FPGA_OBJECT_NAME}"
  )

  add_custom_target(one_api_fpga_object_${REGISTER_AND_BUILD_ONE_API_FPGA_OBJECT_NAME}
    DEPENDS ${REGISTER_AND_BUILD_ONE_API_FPGA_OBJECT_NAME}.o
  )

  list(APPEND ONE_API_FPGA_OBJECTS "${REGISTER_AND_BUILD_ONE_API_FPGA_OBJECT_NAME}.o")
  list(APPEND ONE_API_FPGA_OBJECTS_TARGETS "one_api_fpga_object_${REGISTER_AND_BUILD_ONE_API_FPGA_OBJECT_NAME}")
  set(ONE_API_FPGA_OBJECTS ${ONE_API_FPGA_OBJECTS} PARENT_SCOPE)
  set(ONE_API_FPGA_OBJECTS_TARGETS ${ONE_API_FPGA_OBJECTS_TARGETS} PARENT_SCOPE)
  message(STATUS "register_one_api_fpga_object targets: ${ONE_API_FPGA_OBJECTS_TARGETS}")
endfunction()


function(create_one_api_fpga_library)
  set(options)
  set(oneValueArgs NAME)
  set(multiValueArgs)
  cmake_parse_arguments(CREATE_ONE_API_FPGA_LIBRARY "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

  add_custom_command(
    OUTPUT ${CREATE_ONE_API_FPGA_LIBRARY_NAME}.a
    COMMAND 
      ${ONE_API_FPGA_LIBTOOL} -v ${ONE_API_FPGA_OBJECTS}
      --target sycl --create ${CREATE_ONE_API_FPGA_LIBRARY_NAME}.a
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Running fpga_libtool to build ${CREATE_ONE_API_FPGA_LIBRARY_NAME}.a"
  )
  add_custom_target(${CREATE_ONE_API_FPGA_LIBRARY_NAME}
    DEPENDS ${CREATE_ONE_API_FPGA_LIBRARY_NAME}.a
  )
  message(STATUS "Name: ${CREATE_ONE_API_FPGA_LIBRARY_NAME}. Targets: ${ONE_API_FPGA_OBJECTS_TARGETS}")
  add_dependencies(${CREATE_ONE_API_FPGA_LIBRARY_NAME} ${ONE_API_FPGA_OBJECTS_TARGETS})
endfunction()


#This macro must be called for every object file that should be compiled
register_one_api_fpga_object(
  NAME "rtl_lzc32"
  SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/src/lib_rtl_model_lzc32.cpp
  SPECS ${CMAKE_CURRENT_SOURCE_DIR}/specs/lib_rtl_spec_lzc32.xml
)
message(STATUS "After call: ${ONE_API_FPGA_OBJECTS_TARGETS}")

create_one_api_fpga_library(NAME libtslOneAPIFPGA)
