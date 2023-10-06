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
  set(multiValueArgs SOURCES SPECS VFILE)
  cmake_parse_arguments(REGISTER_AND_BUILD_ONE_API_FPGA_OBJECT "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

  message(STATUS "[REGISTER_ONE_API_FPGA_OBJECT]: Inside register_one_api_fpga_object")
  message(STATUS "[REGISTER_ONE_API_FPGA_OBJECT]: ${ONE_API_FPGA_CROSSGEN} -v -fPIC ${REGISTER_AND_BUILD_ONE_API_FPGA_OBJECT_SPECS} --emulation_model 
      ${REGISTER_AND_BUILD_ONE_API_FPGA_OBJECT_SOURCES} --target sycl 
      -o ${REGISTER_AND_BUILD_ONE_API_FPGA_OBJECT_NAME}.o 
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}")
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
  message(STATUS "[REGISTER_ONE_API_FPGA_OBJECT]: register_one_api_fpga_object: ${ONE_API_FPGA_OBJECTS}")
  message(STATUS "[REGISTER_ONE_API_FPGA_OBJECT]: register_one_api_fpga_object targets: ${ONE_API_FPGA_OBJECTS_TARGETS}")
endfunction()


function(create_one_api_fpga_library)
  set(options)
  set(oneValueArgs NAME)
  set(multiValueArgs)
  cmake_parse_arguments(CREATE_ONE_API_FPGA_LIBRARY "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

  set(LIBRARY_ARCHIVE ${CMAKE_BINARY_DIR}/${CREATE_ONE_API_FPGA_LIBRARY_NAME}.a)

  message(STATUS "[CREATE_ONE_API_FPGA_LIBRARY]: custom target: CREATE_${CREATE_ONE_API_FPGA_LIBRARY_NAME}
    DEPENDS ${LIBRARY_ARCHIVE}")
  add_custom_target(CREATE_${CREATE_ONE_API_FPGA_LIBRARY_NAME}
    DEPENDS ${LIBRARY_ARCHIVE}
  )
  message(STATUS "[CREATE_ONE_API_FPGA_LIBRARY]: ${ONE_API_FPGA_LIBTOOL} -v ${ONE_API_FPGA_OBJECTS}
      --target sycl --create ${LIBRARY_ARCHIVE}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    DEPENDS ${ONE_API_FPGA_OBJECTS_TARGETS}")
  add_custom_command(
    OUTPUT ${LIBRARY_ARCHIVE}
    COMMAND 
      ${ONE_API_FPGA_LIBTOOL} ${ONE_API_FPGA_OBJECTS}
      --target sycl --create ${LIBRARY_ARCHIVE}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    DEPENDS ${ONE_API_FPGA_OBJECTS_TARGETS}
    COMMENT "Running fpga_libtool to build ${LIBRARY_ARCHIVE}"
  )

  message(STATUS "[CREATE_ONE_API_FPGA_LIBRARY]: Name: ${CREATE_ONE_API_FPGA_LIBRARY_NAME}. Targets: ${ONE_API_FPGA_OBJECTS_TARGETS}")
  add_library(${CREATE_ONE_API_FPGA_LIBRARY_NAME}  STATIC IMPORTED GLOBAL)
  add_dependencies(${CREATE_ONE_API_FPGA_LIBRARY_NAME} CREATE_${CREATE_ONE_API_FPGA_LIBRARY_NAME}) 
  set_target_properties(${CREATE_ONE_API_FPGA_LIBRARY_NAME} PROPERTIES IMPORTED_LOCATION ${LIBRARY_ARCHIVE})
endfunction()


#This macro must be called for every object file that should be compiled
register_one_api_fpga_object(
  NAME "rtl_lzc32"
  SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/src/lib_rtl_model_lzc32.cpp
  SPECS ${CMAKE_CURRENT_SOURCE_DIR}/specs/lib_rtl_spec_lzc32.xml
  VFILE ${CMAKE_CURRENT_SOURCE_DIR/specs/lib_rtl_lzc32.v}
)
message(STATUS "After call: ${ONE_API_FPGA_OBJECTS_TARGETS}")

create_one_api_fpga_library(NAME libtslOneAPIFPGA)

