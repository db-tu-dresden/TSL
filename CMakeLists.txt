cmake_minimum_required(VERSION 3.13)
project(tvl)

find_package(Python3 REQUIRED)

# gather lscpu flags
set(TVL_LSCPU_FLAGS "" CACHE STRING "space separated lscpu flags for --targets, will attempt to call lscpu if empty")
if(TVL_LSCPU_FLAGS STREQUAL "")
    execute_process(
        COMMAND "${Python3_EXECUTABLE}" -c "import cpuinfo; print(*cpuinfo.get_cpu_info()['flags'])"
        OUTPUT_STRIP_TRAILING_WHITESPACE OUTPUT_VARIABLE TVL_LSCPU_FLAGS
    )
endif()
if(TVL_LSCPU_FLAGS STREQUAL "")
    message(FATAL_ERROR "failed to deduce TVL_LSCPU_FLAGS, please specify manually")
endif()
message(STATUS "lscpu flags: ${TVL_LSCPU_FLAGS}")
string(REGEX REPLACE "[ \t]+" ";" LSCPU_FLAGS_LIST "${TVL_LSCPU_FLAGS}")

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

set(DEFAULT_GENERATOR_OPTS --no-workaround-warnings)

# check for C++20 Concepts features
if("cxx_std_20" IN_LIST CMAKE_CXX_COMPILE_FEATURES)
	set(CMAKE_CXX_STANDARD 20)
	#set(CMAKE_REQUIRED_FLAGS "${CMAKE_REQUIRED_FLAGS} -std=c++20")
	INCLUDE(CheckCXXSourceCompiles)
		CHECK_CXX_SOURCE_COMPILES(
		[[
		#include <concepts>
		struct test_struct {};
		template<std::copyable T>
		void test_concepts(T) {};
		int main(void) {
			test_concepts(test_struct{});
			return 0;
		}
		]] SUPPORTS_CONCEPTS)
	if(SUPPORTS_CONCEPTS)
		message(STATUS "Compiler does support C++20 and concepts.")
	else()
		message(STATUS "Compiler does support C++20 but not concepts.")
		set(DEFAULT_GENERATOR_OPTS ${DEFAULT_GENERATOR_OPTS} "--no-concepts")
	endif()
else()
	message(STATUS "Compiler does not support C++20.")
	set(DEFAULT_GENERATOR_OPTS ${DEFAULT_GENERATOR_OPTS} "--no-concepts")
endif()

set(TVL_GENERATOR_OPTS ${DEFAULT_GENERATOR_OPTS} CACHE STRING "additonal cli options for the generator, semicolon separated")

# run the generator
set(GENERATOR_OUTPUT_PATH "${CMAKE_CURRENT_BINARY_DIR}/generator_output")
message(STATUS "Running TVL Generator...")
execute_process(
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/main.py" ${TVL_GENERATOR_OPTS} -o "${GENERATOR_OUTPUT_PATH}" --targets ${LSCPU_FLAGS_LIST}
    COMMAND_ERROR_IS_FATAL ANY
)

# run the CMakeLists.txt created by the generator
add_subdirectory("${GENERATOR_OUTPUT_PATH}")
