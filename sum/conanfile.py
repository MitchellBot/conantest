from conan import ConanFile

class SumRecipe(ConanFile):
    name = "sum"
    cmake_name = "sum"
    cmake_alias = "sum::sum"

    python_requires =  "util/[>=1.0.0]"
    python_requires_extend = "util.LibraryPackage"
 
    dependencies = ["boost"]

    test_dependencies = ["gtest"]
