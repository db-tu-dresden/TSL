cmake_minimum_required(VERSION 3.16)

find_program(ONE_API_FPGA_CROSSGEN fpga_crossgen)
find_program(ONE_API_FPGA_LIBTOOL fpga_libtool)

if(NOT ONE_API_FPGA_CROSSGEN)
  message(FATAL_ERROR "Required executables fpga_crossgen not found")
endif()
if(NOT ONE_API_FPGA_LIBTOOL)
  message(FATAL_ERROR "Required executables fpga_libtool not found")
endif()

set(ONE_API_FPGA_OBJECTS_TARGETS )
set(ONE_API_FPGA_OBJECTS )
set(ONE_API_FPGA_LIBRARY_TARGET "libtslOneAPIFPGA" PARENT_SCOPE)

# This is a CMake macro that creates a custom command and target for generating an FPGA object file
# using the `fpga_crossgen` tool. The macro takes in a `NAME` argument for the name of the object file
# to be generated, and `SOURCES` and `SPECS` arguments for the source and specification files needed
# by `fpga_crossgen`.
macro(register_one_api_fpga_object)
  set(options)
  set(oneValueArgs NAME)
  set(multiValueArgs SOURCES SPECS)
  cmake_parse_arguments(REGISTER_AND_BUILD_ONE_API_FPGA_OBJECT "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

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

  list(APPEND ONE_API_FPGA_OBJECTS ${REGISTER_AND_BUILD_ONE_API_FPGA_OBJECT_NAME}.o)
  list(APPEND ONE_API_FPGA_OBJECTS_TARGETS one_api_fpga_object_${REGISTER_AND_BUILD_ONE_API_FPGA_OBJECT_NAME})
endmacro()


macro(create_one_api_fpga_library)
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
  add_custom_target(${ONE_API_FPGA_LIBRARY_TARGET}
    DEPENDS ${CREATE_ONE_API_FPGA_LIBRARY_NAME}.a
  )
  add_dependencies(${ONE_API_FPGA_LIBRARY_TARGET} ${ONE_API_FPGA_OBJECTS_TARGETS})
endmacro()





