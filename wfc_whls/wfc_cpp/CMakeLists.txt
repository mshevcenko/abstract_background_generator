cmake_minimum_required(VERSION 3.15)
project(wfc_cpp)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Add pybind11
add_subdirectory(pybind11)
#set(pybind11_DIR "D:/Programs/vcpkg/installed/x64-windows/share/pybind11")
#find_package(pybind11 CONFIG REQUIRED)

# Specify source files (excluding example directory)
file(GLOB_RECURSE SOURCES "src/*.cpp")
list(FILTER SOURCES EXCLUDE REGEX "example/.*")  # Exclude everything in the example directory

# Create the shared library (Python module)
pybind11_add_module(wfc_cpp ${SOURCES})

# Link the necessary libraries
target_link_libraries(wfc_cpp PRIVATE pybind11::module)

# Include directories
include_directories(${CMAKE_SOURCE_DIR})
