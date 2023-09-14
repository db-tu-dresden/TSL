cmake_minimum_required(VERSION 3.14)
include(FetchContent)

project(Example)

# Choose the branch of TSL to use
set(TSL_BRANCH "main")

# Fetch TSL
FetchContent_Declare(
  tsl
  GIT_REPOSITORY https://github.com/db-tu-dresden/TSL.git
  GIT_TAG        ${TSL_BRANCH}
)
# Make TSL available to the project (triggers the generation of TSL)
FetchContent_MakeAvailable(tsl)

# Create your executable
add_executable(Example main.cpp)
# Set the TSL include directory 
target_include_directories(Example PUBLIC ${TSL_INCLUDE_DIRECTORY})
# Link TSL to your executable
target_link_libraries(Example tsl)

