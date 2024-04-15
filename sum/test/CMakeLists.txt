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

if (${CMAKE_SYSTEM_PROCESSOR} STREQUAL "aarch64")
    set_target_properties(${TEST_PROJECT} PROPERTIES LINK_FLAGS 
        "-Wl,--dynamic-linker=${CMAKE_CXX_COMPILER_SYSROOT}/../lib/ld-linux-aarch64.so.1"
    )
endif ()

include(GoogleTest)

enable_testing()

gtest_discover_tests(${TEST_PROJECT})