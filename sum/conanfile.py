from conan import ConanFile

class SumRecipe(ConanFile):
    name = "sum"
    cmake_name = "sum"
    cmake_alias = "sum::sum"

    package_type = "library"

    python_requires =  "util/[>=1.0.0]"
    python_requires_extend = "util.StandardPackage"
 
    dependencies = ["boost"]

    test_dependencies = ["gtest"]
