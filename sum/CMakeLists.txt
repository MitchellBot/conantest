cmake_minimum_required(VERSION 3.15)
project(sum CXX)

set(MAIN_PROJECT ${PROJECT_NAME})

add_library(${MAIN_PROJECT} src/sum.cpp)

target_include_directories(${MAIN_PROJECT} PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/include")

################################################################################
# Testing
################################################################################
if(NOT BUILD_TESTING STREQUAL OFF)
    include (CTest)
    add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/test")
endif(NOT BUILD_TESTING STREQUAL OFF)
