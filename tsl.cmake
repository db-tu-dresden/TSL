cmake_minimum_required(VERSION 3.16)

find_package(Python3 REQUIRED)


function(create_tsl)
  set(options WORKAROUND_WARNINGS USE_CONCEPTS CREATE_TESTS)
  set(oneValueArgs TSLGENERATOR_DIRECTORY DESTINATION)
  set(multiValueArgs TARGETS_FLAGS APPEND_TARGETS_FLAGS PRIMITIVES_FILTER DATATYPES_FILTER LINK_OPTIONS GENERATOR_OPTIONS)
  cmake_parse_arguments(CREATE_TSL_ARGS "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})
  
  if(NOT DEFINED CREATE_TSL_ARGS_TSLGENERATOR_DIRECTORY)
    set(TSLGENERATOR_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}")
  else()
    set(TSLGENERATOR_DIRECTORY "${CREATE_TSL_ARGS_TSLGENERATOR_DIRECTORY}")
  endif()

  if (CREATE_TSL_ARGS_TARGETS_FLAGS STREQUAL "" OR NOT DEFINED CREATE_TSL_ARGS_TARGETS_FLAGS)
    set(TARGETS_FLAGS "" STRING "space separated lscpu flags for --targets, will attempt to call lscpu if empty")
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
  else()
    set(TARGETS_FLAGS "${CREATE_TSL_ARGS_TARGETS_FLAGS}")
  endif()


  string(REGEX REPLACE "[ \t]+" ";" TARGETS_FLAGS_LIST "${TARGETS_FLAGS}")
  list(APPEND TARGETS_FLAGS_LIST ${CREATE_TSL_ARGS_APPEND_TARGETS_FLAGS})
  set(TSL_TARGETS_SWITCH "--targets" ${TARGETS_FLAGS_LIST})

  if(NOT DEFINED CREATE_TSL_ARGS_PRIMITIVES_FILTER)
    # message(STATUS "No primitive filtering.")
    set(TSL_PRIMITIVE_SWITCH "")
  else()
    message(STATUS "relevant primitives: ${CREATE_TSL_ARGS_PRIMITIVES_FILTER}")
    string(REGEX MATCHALL "([a-zA-Z\_])+" PRIMITIVE_LIST "${CREATE_TSL_ARGS_PRIMITIVES_FILTER}")
    set(TSL_PRIMITIVE_SWITCH "--primitives" ${PRIMITIVE_LIST})
  endif()

  if(NOT DEFINED CREATE_TSL_ARGS_DATATYPES_FILTER)
    # message(STATUS "No primitive filtering.")
    set(TSL_TYPES_SWITCH "")
  else()
    message(STATUS "relevant data types: ${CREATE_TSL_ARGS_DATATYPES_FILTER}")
    string(REGEX MATCHALL "([a-zA-Z\_0-9])+" TYPE_LIST "${CREATE_TSL_ARGS_DATATYPES_FILTER}")
    set(TSL_TYPES_SWITCH "--types" ${TYPE_LIST})
  endif()

  if(NOT DEFINED CREATE_TSL_ARGS_LINK_OPTIONS)
    # message(STATUS "No additional link options.")
    unset(TSL_LINK_OPTIONS)
  else()
    # string(REPLACE ";" " " link_options_list "${CREATE_TSL_ARGS_LINK_OPTIONS}")
    set(TSL_LINK_OPTIONS ${CREATE_TSL_ARGS_LINK_OPTIONS} CACHE STRING "linker options")
  endif()

  if(CREATE_TSL_ARGS_DESTINATION STREQUAL "" OR NOT DEFINED CREATE_TSL_ARGS_DESTINATION)
    set(TSL_GENERATOR_DESTINATION "${CMAKE_CURRENT_BINARY_DIR}/generator_output")
  else()
    set(TSL_GENERATOR_DESTINATION ${CREATE_TSL_ARGS_DESTINATION})
  endif()

  file(GLOB_RECURSE TSL_GENERATOR_SOURCES CONFIGURE_DEPENDS
    "${TSLGENERATOR_DIRECTORY}/generator/config/*.template"
    "${TSLGENERATOR_DIRECTORY}/generator/config/*.yaml"
    "${TSLGENERATOR_DIRECTORY}/generator/static_files/*.yaml"
    "${TSLGENERATOR_DIRECTORY}/generator/core/*.py"
    "${TSLGENERATOR_DIRECTORY}/generator/expansions/*.py"
    "${TSLGENERATOR_DIRECTORY}/generator/utils/*.py"
    "${TSLGENERATOR_DIRECTORY}/primitive_data/extensions/*.yaml"
    "${TSLGENERATOR_DIRECTORY}/primitive_data/primitives/*.yaml"
  )
  set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS ${TSL_GENERATOR_SOURCES})

  if(NOT DEFINED CREATE_TSL_ARGS_GENERATOR_OPTIONS)
    set(CURRENT_GENERATOR_OPTIONS "")
  else()
    set(CURRENT_GENERATOR_OPTIONS "${CREATE_TSL_ARGS_GENERATOR_OPTIONS}")
  endif()
  if(CREATE_TSL_ARGS_WORKAROUND_WARNINGS)
    set(CURRENT_GENERATOR_OPTIONS "${CURRENT_GENERATOR_OPTIONS}" "--workaround-warnings")
  else()
    set(CURRENT_GENERATOR_OPTIONS "${CURRENT_GENERATOR_OPTIONS}" "--no-workaround-warnings")
  endif()

  if(CREATE_TSL_ARGS_CREATE_TESTS)
    set(CURRENT_GENERATOR_OPTIONS "${CURRENT_GENERATOR_OPTIONS}" "--testing")
  else() 
    set(CURRENT_GENERATOR_OPTIONS "${CURRENT_GENERATOR_OPTIONS}" "--no-testing")
  endif()

  if(CREATE_TSL_ARGS_USE_CONCEPTS)
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
  set(TSL_GENERATOR_OPTIONS ${CURRENT_GENERATOR_OPTIONS} STRING "additonal cli options for the generator, semicolon separated")
  
  message(STATUS "=== SUMMARY: TSL Generation ===")
  message(STATUS "Script path      : ${TSLGENERATOR_DIRECTORY}/main.py")
  message(STATUS "Generation path  : ${TSL_GENERATOR_DESTINATION}")
  message(STATUS "Switches         : ")
  if(TSL_TARGETS_SWITCH STREQUAL "")
    message(STATUS "   all targets")
  else()
    message(STATUS "   ${TSL_TARGETS_SWITCH}")
  endif()
  if(TSL_PRIMITIVE_SWITCH STREQUAL "")
    message(STATUS "   all primitives")
  else()
    message(STATUS "   ${TSL_PRIMITIVE_SWITCH}")
  endif()
  if(TSL_TYPES_SWITCH STREQUAL "")
    message(STATUS "   all types")
  else()
    message(STATUS "   ${TSL_TYPES_SWITCH}")
  endif()
  message(STATUS "Generator Options: ${TSL_GENERATOR_OPTIONS}")
  message(STATUS "Target Options   : ${TSL_LINK_OPTIONS}")
  message(STATUS "===============================")
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