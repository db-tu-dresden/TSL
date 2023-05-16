find_package(Python3 REQUIRED)

function(create_tsl)
  set(options WORKAROUND_WARNINGS USE_CONCEPTS)
  set(oneValueArgs TSLGENERATOR_DIRECTORY DESTINATION)
  set(multiValueArgs TARGETS_FLAGS PRIMITIVES_FILTER DATATYPES_FILTER LINK_OPTIONS GENERATOR_OPTIONS)
  cmake_parse_arguments(TSLGEN_CREATE "${options}" "${oneValueArgs}" "{multiValueArgs}" ${ARGN})
  
  
  if (TARGET_FLAGS STREQUAL "" OR NOT DEFINED TARGETS_FLAGS)
    set(TARGETS_FLAGS "" CACHE STRING "space separated lscpu flags for --targets, will attempt to call lscpu if empty")
    if(LSCPU_FLAGS STREQUAL "")
        execute_process(
            COMMAND "${Python3_EXECUTABLE}" -c "import cpuinfo; print(*cpuinfo.get_cpu_info()['flags'])"
            OUTPUT_STRIP_TRAILING_WHITESPACE OUTPUT_VARIABLE TARGETS_FLAGS
        )
    endif()
    if(TARGETS_FLAGS STREQUAL "")
      execute_process(
        COMMAND bash -c "LANG=en;lscpu|grep -i flags | tr ' ' '\n' | egrep -v '^Flags:|^$' | sort -d | tr '\n' ' '"
        OUTPUT_VARIABLE TARGETS_FLAGS
        RESULT_VARIABLE TSLHardwareReturnValue
      )
      if(NOT TSLHardwareReturnValue EQUAL 0)
        message(FATAL_ERROR "Could not determine hardware flags. Please specify them manually.")
      endif()
    endif()
    message(STATUS "lscpu flags: ${TARGETS_FLAGS}")
  endif()

  string(REGEX REPLACE "[ \t]+" ";" TARGETS_FLAGS_LIST "${TARGETS_FLAGS}")
  set(TSL_TARGETS_SWITCH "--targets" ${TARGETS_FLAGS_LIST})

  if(PRIMITIVES_FILTER STREQUAL "" OR NOT DEFINED PRIMITIVES_FILTER)
    message(STATUS "No primitive filtering.")
    set(TSL_PRIMITIVE_SWITCH "")
  else()
    message(STATUS "relevant primitives: ${PRIMITIVES_FILTER}")
    string(REGEX MATCHALL "([a-zA-Z\_])+" PRIMITIVE_LIST "${PRIMITIVES_FILTER}")
    set(TSL_PRIMITIVE_SWITCH "--primitives" ${PRIMITIVE_LIST})
  endif()

  if(DATATYPES_FILTER STREQUAL "" OR NOT DEFINED DATATYPES_FILTER)
    message(STATUS "No primitive filtering.")
    set(TSL_TYPES_SWITCH "")
  else()
    message(STATUS "relevant data types: ${DATATYPES_FILTER}")
    string(REGEX MATCHALL "([a-zA-Z\_0-9])+" TYPE_LIST "${DATATYPES_FILTER}")
    set(TSL_TYPES_SWITCH "--types" ${TYPE_LIST})
  endif()

  if(LINK_OPTIONS STREQUAL "" OR NOT DEFINED LINK_OPTIONS)
    message(STATUS "No additional link options.")
    unset(TSL_LINK_OPTIONS)
  else()
    set(TSL_LINK_OPTIONS ${LINK_OPTIONS} CACHE STRING "linker options")
  endif()

  if(DESTINATION STREQUAL "" OR NOT DEFINED DESTINATION)
    set(TSL_GENERATOR_DESTINATION "${CMAKE_CURRENT_BINARY_DIR}/generator_output")
  else()
    set(TSL_GENERATOR_DESTINATION ${DESTINATION})
  endif()

  file(GLOB_RECURSE TSL_GENERATOR_SOURCES CONFIGURE_DEPENDS
    "${TSL_ROOT}/generator/config/*.template"
    "${TSL_ROOT}/generator/config/*.yaml"
    "${TSL_ROOT}/generator/static_files/*.yaml"
    "${TSL_ROOT}/generator/core/*.py"
    "${TSL_ROOT}/generator/expansions/*.py"
    "${TSL_ROOT}/generator/utils/*.py"
    "${TSL_ROOT}/primitive_data/extensions/*.yaml"
    "${TSL_ROOT}/primitive_data/primitives/*.yaml"
  )
  set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS ${TSL_GENERATOR_SOURCES})

  if(WORKAROUND_WARNINGS)
    set(CURRENT_GENERATOR_OPTIONS "${GENERATOR_OPTIONS}" "--workaround-warnings")
  else()
    set(CURRENT_GENERATOR_OPTIONS "${GENERATOR_OPTIONS}" "--no-workaround-warnings")
  endif()

  if(USE_CONCEPTS)
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
        set(CURRENT_GENERATOR_OPTIONS ${CURRENT_GENERATOR_OPTIONS} "--no-concepts")
      endif()
    else()
      message(STATUS "Compiler does not support C++20.")
      set(CURRENT_GENERATOR_OPTIONS ${CURRENT_GENERATOR_OPTIONS} "--no-concepts")
    endif()
  else()
    set(CURRENT_GENERATOR_OPTIONS ${CURRENT_GENERATOR_OPTIONS} "--no-concepts")
  endif()


  set(TSL_GENERATOR_OPTIONS ${CURRENT_GENERATOR_OPTIONS} CACHE STRING "additonal cli options for the generator, semicolon separated")
  message(STATUS "Running TSL Generator...")
  execute_process(
      COMMAND "${Python3_EXECUTABLE}" "${TSLGENERATOR_DIRECTORY}/main.py" 
      ${TSL_GENERATOR_OPTIONS} -o "${TSL_GENERATOR_DESTINATION}"
      ${TSL_TARGETS_SWITCH} ${TSL_PRIMITIVE_SWITCH} ${TSL_TYPES_SWITCH}
      ANY
  )

  set(TSL_INCLUDE_DIRECTORY "${TSL_GENERATOR_DESTINATION}/include" CACHE STRING "include path of TSL")
  
  add_subdirectory("${TSL_GENERATOR_DESTINATION}" "${TSL_GENERATOR_DESTINATION}/build")
endfunction()