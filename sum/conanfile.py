from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy

class ConsumerRecipe(ConanFile):
    name = "sum"
    version = "0.1"
    settings = "os", "compiler", "build_type", "arch"

    export_sources = "include/*", "src/*"

    def requirements(self):
        self.test_requires("gtest/1.12.1")

    def export_sources(self):
        copy(self, "include/*", self.recipe_folder, self.export_sources_folder)
        copy(self, "src/*", self.recipe_folder, self.export_sources_folder)
        copy(self, "test/*", self.recipe_folder, self.export_sources_folder)
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)

    def generate(self):
        cmake = CMakeDeps(self)
        cmake.generate()
        tc = CMakeToolchain(self)
        tc.generate()
        
    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.test()

    def package(self):
        copy(self, "*.h", self.source_folder, self.package_folder)
        copy(self, "*.a", self.source_folder, self.package_folder)

    def package_info(self):
        self.cpp_info.libs = ["sum"]