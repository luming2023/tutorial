cmake_minimum_required(VERSION 3.10)

# set the project name and version
project(Tutorial VERSION 1.0)

# specify the C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# should we use our own math functions
option(USE_FIREDOG "Use tutorial provided  implementation" ON)

link_directories(
/home/lyu2/random-test-case/c++/FireDog
)

# configure a header file to pass some of the CMake settings
# to the source code
# configure_file(TutorialConfig.h.in TutorialConfig.h)

# TODO 2: Remove EXTRA_INCLUDES list

# add the MathFunctions library
if(USE_FIREDOG)
  add_subdirectory(FireDog)
  list(APPEND EXTRA_LIBS FIREDOG)
  list(APPEND EXTRA_INCLUDES "${PROJECT_SOURCE_DIR}/FireDog")
endif()

# add the executable
add_executable(Tutorial main.cpp)

target_link_libraries(Tutorial PUBLIC ${EXTRA_LIBS})

# TODO 3: Remove use of EXTRA_INCLUDES

# add the binary tree to the search path for include files
# so that we will find TutorialConfig.h
target_include_directories(Tutorial PUBLIC
                           "${PROJECT_BINARY_DIR}"
                           ${EXTRA_INCLUDES}
                           )
