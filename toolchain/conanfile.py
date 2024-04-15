import os
from conan import ConanFile
from conan.tools.files import get, copy, download
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Version
from conan.tools.cmake import CMakeToolchain

class ArmToolchainPackage(ConanFile):
    name = "armtoolchain"
    version = "13.2"

    license = "GPL-3.0-only"
    homepage = "https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads"
    description = "Conan package for the ARM toolchain, targeting different Linux ARM architectures."
    settings = "os", "arch"
    package_type = "application"

    def _archs64(self):
        return ["armv8", "armv8.3"]

    def _get_toolchain(self, target_arch):
        return ("aarch64-none-linux-gnu", 
                "12fcdf13a7430655229b20438a49e8566e26551ba08759922cdaf4695b0d4e23")

    def validate(self):
        if self.settings.arch != "x86_64" or self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"This toolchain is not compatible with {self.settings.os}-{self.settings.arch}. "
                                            "It can only run on Linux-x86_64.")

        if self.settings_target.os != "Linux" or self.settings_target.arch not in self._archs64():
            raise ConanInvalidConfiguration(f"This toolchain only supports building for Linux-{self._archs64()}. "
                                           f"{self.settings_target.os}-{self.settings_target.arch} is not supported.")

        if self.settings_target.compiler != "gcc":
            raise ConanInvalidConfiguration(f"The compiler is set to '{self.settings_target.compiler}', but this "
                                            "toolchain only supports building with gcc.")

        if Version(self.settings_target.compiler.version) >= Version("14") or Version(self.settings_target.compiler.version) < Version("13"):
            raise ConanInvalidConfiguration(f"Invalid gcc version '{self.settings_target.compiler.version}'. "
                                            "Only 13.X versions are supported for the compiler.")

    def source(self):
        toolchain, sha = self._get_toolchain(self.settings_target.arch)
        get(self, f"https://developer.arm.com/-/media/Files/downloads/gnu/13.2.rel1/binrel/arm-gnu-toolchain-13.2.rel1-x86_64-{toolchain}.tar.xz",
            sha256=sha, strip_root=True)   
        download(self, "https://developer.arm.com/GetEula?Id=37988a7c-c40e-4b78-9fd1-62c20b507aa8", "LICENSE", verify=False)

    def package(self):
        toolchain, _ = self._get_toolchain(self.settings_target.arch)
        dirs_to_copy = [toolchain, "bin", "include", "lib", "libexec"]
        for dir_name in dirs_to_copy:
            copy(self, pattern=f"{dir_name}/*", src=self.build_folder, dst=self.package_folder, keep_path=True)
        copy(self, "LICENSE", src=self.build_folder, dst=os.path.join(self.package_folder, "licenses"), keep_path=False)

    def package_id(self):
        self.info.settings_target = self.settings_target
        # We only want the ``arch`` setting
        self.info.settings_target.rm_safe("os")
        self.info.settings_target.rm_safe("compiler")
        self.info.settings_target.rm_safe("build_type")

    def package_info(self):
        toolchain, _ = self._get_toolchain(self.settings_target.arch)
        self.cpp_info.bindirs.append(os.path.join(self.package_folder, toolchain, "bin"))
        self.cpp_info.libdirs.append(os.path.join(self.package_folder, toolchain, "libc", "lib64"))
        self.cpp_info.libdirs.append(os.path.join(self.package_folder, toolchain, "lib64"))

        self.conf_info.define("tools.build:compiler_executables", {
            "c":   f"{toolchain}-gcc",
            "cpp": f"{toolchain}-g++",
            "asm": f"{toolchain}-as"
        })