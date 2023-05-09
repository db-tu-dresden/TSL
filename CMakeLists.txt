cmake_minimum_required(VERSION 3.19)
project(tsl)

find_package(Python3 REQUIRED)

# gather lscpu flags
set(TSL_LSCPU_FLAGS "" CACHE STRING "space separated lscpu flags for --targets, will attempt to call lscpu if empty")
if(TSL_LSCPU_FLAGS STREQUAL "")
    execute_process(
        COMMAND "${Python3_EXECUTABLE}" -c "import cpuinfo; print(*cpuinfo.get_cpu_info()['flags'])"
        OUTPUT_STRIP_TRAILING_WHITESPACE OUTPUT_VARIABLE TSL_LSCPU_FLAGS
    )
endif()
if(TSL_LSCPU_FLAGS STREQUAL "")
	execute_process(
		COMMAND bash -c "LANG=en;lscpu|grep -i flags | tr ' ' '\n' | egrep -v '^Flags:|^$' | sort -d | tr '\n' ' '"
		OUTPUT_VARIABLE TSL_LSCPU_FLAGS
		RESULT_VARIABLE TSLHardwareReturnValue
	)
	if(NOT TSLHardwareReturnValue EQUAL 0)
		message(FATAL_ERROR "Could not determine hardware flags. Please specify them manually.")
	endif()
endif()
message(STATUS "lscpu flags: ${TSL_LSCPU_FLAGS}")
string(REGEX REPLACE "[ \t]+" ";" LSCPU_FLAGS_LIST "${TSL_LSCPU_FLAGS}")

set(TSL_FILTER_FOR_PRIMITIVES "" CACHE STRING "space separated list of primitives to generate")
if(TSL_FILTER_FOR_PRIMITIVES STREQUAL "")
	message(STATUS "No primitive filtering.")
	set( TSL_PRIMITIVE_SWITCH "" )
else()
	message(STATUS "relevant primitives: ${TSL_FILTER_FOR_PRIMITIVES}")
	string(REGEX MATCHALL "([a-zA-Z\_])+" PRIMITIVE_LIST "${TSL_FILTER_FOR_PRIMITIVES}")
	set( TSL_PRIMITIVE_SWITCH --primitives ${PRIMITIVE_LIST} )
endif()

# trigger reconfiguration if the source files of the generator changed
file(GLOB_RECURSE TSL_GENERATOR_SOURCES CONFIGURE_DEPENDS
    "generator/config/*.template"
    "generator/config/*.yaml"
    "generator/static_files/*.yaml"
    "generator/core/*.py"
    "generator/expansions/*.py"
    "generator/utils/*.py"
    "primitive_data/extensions/*.yaml"
    "primitive_data/primitives/*.yaml"
)
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS ${TSL_GENERATOR_SOURCES})

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

set(TSL_GENERATOR_OPTS ${DEFAULT_GENERATOR_OPTS} CACHE STRING "additonal cli options for the generator, semicolon separated")

# run the generator
set(GENERATOR_OUTPUT_PATH "${CMAKE_CURRENT_BINARY_DIR}/generator_output")
message(STATUS "Running TSL Generator...")
execute_process(
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/main.py" ${TSL_GENERATOR_OPTS} -o "${GENERATOR_OUTPUT_PATH}" --targets ${LSCPU_FLAGS_LIST} ${TSL_PRIMITIVE_SWITCH}
    COMMAND_ERROR_IS_FATAL ANY
)

# run the CMakeLists.txt created by the generator
add_subdirectory("${GENERATOR_OUTPUT_PATH}")
