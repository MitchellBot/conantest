cmake_minimum_required(VERSION 3.15)
project(sumtest CXX)

set(TEST_PROJECT test_sum)

find_package(GTest REQUIRED CONFIG)

add_executable(${TEST_PROJECT} src/test.cpp)

target_link_libraries(${TEST_PROJECT} 
    GTest::gtest 
    GTest::gtest_main 
    ${MAIN_PROJECT}
)

include(GoogleTest)

enable_testing()

gtest_discover_tests(${TEST_PROJECT})