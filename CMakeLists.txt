cmake_minimum_required(VERSION 3.16)
project(tslgen)

include(tsl.cmake)

create_tsl(
	CREATE_TESTS TRUE
	TSLGENERATOR_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
	DESTINATION ${GENERATOR_OUTPUT_PATH}	
)
message(STATUS "TSL Include Directory: ${TSL_INCLUDE_DIRECTORY}")