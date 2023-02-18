cmake_minimum_required(VERSION 3.13)
project(tvl)

# gather lscpu flags
set(TVL_LSCPU_FLAGS "" CACHE STRING "space separated lscpu flags for --targets, will attempt to call lscpu if empty")
if(TVL_LSCPU_FLAGS STREQUAL "")
    execute_process(
        COMMAND "sh" "-c" "lscpu | sed -n 's/Flags:\\s*\\(.*\\)/\\1/p'"
        OUTPUT_STRIP_TRAILING_WHITESPACE OUTPUT_VARIABLE TVL_LSCPU_FLAGS
    )
endif()
if(TVL_LSCPU_FLAGS STREQUAL "")
    message(FATAL_ERROR "failed to deduce TVL_LSCPU_FLAGS, please specify manually")
endif()
string(REGEX REPLACE "[ \t]+" ";" LSCPU_FLAGS_LIST "${TVL_LSCPU_FLAGS}")
message(STATUS "lscpu flags: ${LSCPU_FLAGS_LIST}")

# trigger reconfiguration if the source files of the generator changed
file(GLOB_RECURSE TVL_GENERATOR_SOURCES CONFIGURE_DEPENDS
    "config/*.template"
    "config/*.yaml"
    "static_files/*.yaml"
    "core/*.py"
    "expansions/*.py"
    "utils/*.py"
    "primitive_data/extensions/*.yaml"
    "primitive_data/primitives/*.yaml"
)
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS ${TVL_GENERATOR_SOURCES})

# run the generator
set(GENERATOR_OUTPUT_PATH "${CMAKE_CURRENT_BINARY_DIR}/generator_output")
find_package(Python3 REQUIRED)

message(STATUS "Running TVL Generator...")
execute_process(
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/main.py" --no-workaround-warnings --no-concepts -o "${GENERATOR_OUTPUT_PATH}" --targets ${LSCPU_FLAGS_LIST}
    COMMAND_ERROR_IS_FATAL ANY
)

# run the CMakeLists.txt created by the generator
add_subdirectory("${GENERATOR_OUTPUT_PATH}")

# disable -W-attributes
include(CheckCXXCompilerFlag)
check_cxx_compiler_flag(-Wno-attributes HAVE_W_NO_ATTRIBUTES)
if (HAVE_W_NO_ATTRIBUTES)
    target_compile_options(tvl INTERFACE -Wno-attributes)
endif()
