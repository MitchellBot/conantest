from conan import ConanFile
from conan.tools.files import copy
from conans.errors import ConanException
from conan.api.output import ConanOutput
from os import path
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout

class Package(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def to_string(self):
        return self.Name + "/" + self.Version

LibraryVersions = {
    "sum" : Package(Name="sum", Version="1.0.0")
}

ThirdPartyVersions = {
    "boost" : Package(Name="boost", Version="1.79.0"),
    "gtest" : Package(Name="gtest", Version="1.12.1")
}

def standard_layout(self):
    cmake_layout(self)

def standard_export(self):
    copy(self, "include/*", self.recipe_folder, self.export_sources_folder)
    copy(self, "src/*", self.recipe_folder, self.export_sources_folder)
    copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
    copy(self, "test/*", self.recipe_folder, self.export_sources_folder, excludes="build")

def standard_package(self):
    copy(self, pattern="*.h", src=path.join(self.source_folder, "Include"), dst=path.join(self.package_folder, "Include"))
    copy(self, pattern="*.hpp", src=path.join(self.source_folder, "Include"), dst=path.join(self.package_folder, "Include"))
    copy(self, pattern="*.tpp", src=path.join(self.source_folder, "Include"), dst=path.join(self.package_folder, "Include"))
    copy(self, pattern="*.so", src=self.build_folder, dst=path.join(self.package_folder, "lib"), keep_path=False)
    copy(self, pattern="*.a", src=self.build_folder, dst=path.join(self.package_folder, "lib"), keep_path=False)

def standard_config(self):
    if self.settings.os == "Windows":
        del self.options.fPIC

def standard_generate(self):
    cmake = CMakeDeps(self)
    cmake.generate()
    tc = CMakeToolchain(self)
    tc.generate()

def standard_build(self):
    cmake = CMake(self)
    cmake.configure()
    cmake.build()
    cmake.test()

def no_test_build(self):
    cmake = CMake(self)
    cmake.configure()
    cmake.build()

def set_package_info(self, libname, alias):
    self.cpp_info.libs = [libname]
    self.cpp_info.set_property("cmake_target_name", alias)
    self.cpp_info.includedirs = ["Include"]

def set_header_only_package_info(self, alias):
    self.cpp_info.set_property("cmake_target_name", alias)
    self.cpp_info.bindirs = []
    self.cpp_info.libdirs = []
    self.cpp_info.includedirs = ["Include"]

def get_dependency_full(self, lookup_table, thirdparty_table, dependency):
    ConanOutput().verbose(f"Looking for dependency: {dependency}")

    if dependency in lookup_table:
        lib = lookup_table[dependency].to_string()

        ConanOutput().verbose(f"Found dependency: {lib} in own lookup table")
        return lib
    elif dependency in thirdparty_table:
        tplib = thirdparty_table[dependency].to_string()

        ConanOutput().verbose(f"Found dependency: {tplib} in third party dependencies")
        return tplib
    else:
        ConanOutput().error(f"Failed to find dependency {dependency} inside the lookup table.\n \
Have all ThirdParty references been added to the ThirdParty Versions?\n \
Have all Library references been added to the Library Versions?")
        raise ConanException(f"Failed to find dependency {dependency} inside the lookup table.")

class StandardPackage:
    global name
    global dependencies
    global test_dependencies

    # Only rebuild this library if it doesn't exist (or has been changed).
    build_policy = "missing"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}

    def requirements(self):
        self.requires('boost/1.79.0')
        self.test_requires('gtest/1.12.1')
        # if hasattr(self, 'dependencies') and self.dependencies:
        #     for dependency in self.dependencies:
        #         self.requires(get_dependency_full(self, LibraryVersions, ThirdPartyVersions, dependency))

        # if hasattr(self, 'test_dependencies') and self.test_dependencies:
        #     for dependency in self.test_dependencies:
        #         self.test_requires(get_dependency_full(self, LibraryVersions, ThirdPartyVersions, dependency))

    def init(self):
        if not self.package_type or self.package_type == "unknown":
            raise ConanException("You must define the package_type as [application, library, header-library] for proper build.")
        if not self.name:
            raise ConanException("You must define the `name` for this package.")

        # TODO: remove these and only extend one of the other classes
        self.version = LibraryVersions[self.name].Version
        self.name = LibraryVersions[self.name].Name

    def export_sources(self):
        if self.package_type == "header-library":
            copy(self, "*.h", self.recipe_folder, self.export_sources_folder)
            copy(self, "*.hpp", self.recipe_folder, self.export_sources_folder)
        else:
            standard_export(self)

    def config_options(self):
        if self.package_type != "header-library":
            standard_config(self)

    def layout(self):
        if self.package_type != "header-library":
            standard_layout(self)

    def generate(self):
        if self.package_type != "header-library":
            standard_generate(self)

    def build(self):
        if self.package_type != "header-library":
            standard_build(self)

    def package(self):
        standard_package(self)

class StandardLibrary(StandardPackage):
    global cmake_name
    global cmake_alias

    def init(self):
        super().init()

        # Only compiled packages get a CMake name
        if self.package_type != "header-library" and not self.cmake_name:
            raise ConanException("You must define the `cmake_name` for this library.")

        # But everything gets a CMake alias because it's how the package is referenced
        if not self.cmake_alias:
            raise ConanException("You must define the `cmake_alias` for this library.")

        # We also need a name for look up in the versions table
        if self.name not in LibraryVersions:
            raise ConanException(f"'{self.name}' not in LibraryVersions, are you sure this is a regular library?")
            
        self.version = LibraryVersions[self.name].Version
        self.name = LibraryVersions[self.name].Name

    def package_info(self):
        if self.package_type == "header-library":
            set_header_only_package_info(self, self.cmake_alias)
        else:
            set_package_info(self, self.cmake_name, self.cmake_alias)

    def package_id(self):
        if self.package_type == "header-library":
            self.info.clear()

class LibraryPackage(StandardLibrary):
    package_type = "library"

class HeaderLibraryPackage(StandardLibrary):
    package_type = "header-library"

class UtilRecipe(ConanFile):
    name = "util"
    version = "1.0.0"
    package_type = "python-require"