cmake_minimum_required(VERSION 3.13)
project(tvl)

# gather lscpu flags
set(TVL_LSCPU_FLAGS "" CACHE STRING "lscpu flags for --targets, will attempt to call lscpu if empty")
if(TVL_LSCPU_FLAGS STREQUAL "")
    execute_process(
        COMMAND "sh" "-c" "lscpu | sed -n 's/Flags:\\s*\\(.*\\)/\\1/p' | tr ' ' ';'"
        OUTPUT_STRIP_TRAILING_WHITESPACE OUTPUT_VARIABLE TVL_LSCPU_FLAGS
    )
endif()
if(TVL_LSCPU_FLAGS STREQUAL "")
    message(FATAL_ERROR "failed to deduce TVL_LSCPU_FLAGS, please specify manually")
endif()

# run generator, this could be made 'lazy' using the strategy from tslgen.cmake
set(GENERATOR_OUTPUT_PATH "${CMAKE_CURRENT_BINARY_DIR}/generator_output")
message(STATUS "lscpu flags: ${TVL_LSCPU_FLAGS}")
message(STATUS "running generator...")
execute_process(
    COMMAND python3 "${CMAKE_CURRENT_SOURCE_DIR}/main.py" --no-workaround-warnings --no-concepts -o "${GENERATOR_OUTPUT_PATH}" --targets ${TVL_LSCPU_FLAGS}
    COMMAND_ERROR_IS_FATAL ANY
)

add_subdirectory("${GENERATOR_OUTPUT_PATH}")

# disable -W-attributes
include(CheckCXXCompilerFlag)
check_cxx_compiler_flag(-Wno-attributes HAVE_W_NO_ATTRIBUTES)
if (HAVE_W_NO_ATTRIBUTES)
    target_compile_options(tvl INTERFACE -Wno-attributes)
endif()
