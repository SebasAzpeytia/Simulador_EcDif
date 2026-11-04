cmake_minimum_required(VERSION 3.20)
project(rc_simulator_core VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

add_library(rc_solver_lib STATIC
    cpp/src/rc_solver.cpp
)

target_include_directories(rc_solver_lib PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/cpp/include
)

if(MSVC)
    target_compile_options(rc_solver_lib PRIVATE /W4 /O2 /fp:fast)
else()
    target_compile_options(rc_solver_lib PRIVATE -Wall -Wextra -Wpedantic -O3)
endif()

pybind11_add_module(rc_core_cpp MODULE
    cpp/src/bindings.cpp
)

target_link_libraries(rc_core_cpp PRIVATE rc_solver_lib)

if(MSVC)
    target_compile_options(rc_core_cpp PRIVATE /W4 /O2)
else()
    target_compile_options(rc_core_cpp PRIVATE -Wall -Wextra -Wpedantic -O3)
endif()

install(TARGETS rc_core_cpp LIBRARY DESTINATION rc_simulator)

add_custom_command(TARGET rc_core_cpp POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        $<TARGET_FILE:rc_core_cpp>
        ${CMAKE_CURRENT_SOURCE_DIR}/src/rc_simulator/$<TARGET_FILE_NAME:rc_core_cpp>
    COMMENT "Copiando modulo nativo rc_core_cpp a src/rc_simulator para desarrollo local"
)

