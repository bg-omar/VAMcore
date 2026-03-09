# **Hydrogen Quantum Orbital Visualizer**

Here is the raw code for the atom simulation, includes raytracer version, realtime runner, and 2D version

web version: [kavang.com/atom](https://www.kavang.com/atom)

What the model does:
1. Takes the quantum numbers (n, l, m) that describe an orbital's shape
2. Using the schrodinger equation, sample r, theta, and phi coordinates from those quantum numbers
3. Render those possible positions and color code them relative to their probabilities (brighter areas have higher probability)

## **Building Requirements:**

1. C++ Compiler supporting C++ 17 or newer
2. [CMake](https://cmake.org/)
3. **Libraries:** GLFW, GLEW, GLM, OpenGL (see below for how to install)

## **Getting the packages**

Pick one method depending on your OS and toolchain.

### Windows — MSYS2 MinGW (recommended for CLion + MinGW)

Open **MSYS2 MinGW 64-bit** (not the default MSYS2 shell) and run:

```bash
pacman -S mingw-w64-x86_64-glfw mingw-w64-x86_64-glew mingw-w64-x86_64-glm
```

This installs headers and libs into `C:\msys64\mingw64`. Then in CLion set `-DMINGW64_ROOT=C:/msys64/mingw64` and use the MinGW toolchain. OpenGL and GDI32 come with the toolchain; no extra package needed.

### Windows — vcpkg

Install [vcpkg](https://vcpkg.io/en/docs/getting-started.html), then in a normal terminal (e.g. PowerShell):

```bash
vcpkg install glfw3 glew glm
```

Then configure CMake with the vcpkg toolchain (see Build Instructions below). Leave `MINGW64_ROOT` empty and use a compiler that can see vcpkg’s installed libs (e.g. Visual Studio or a vcpkg-aware MinGW).

### Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install build-essential cmake \
  libglew-dev libglfw3-dev libglm-dev libgl1-mesa-dev
```

## **Build Instructions:**

1. Clone the repository:
	-  `git clone https://github.com/kavan010/Atoms.git`
2. CD into the newly cloned directory
	- `cd ./Atoms` 
3. Install dependencies with Vcpkg
	- `vcpkg install`
4. Get the vcpkg cmake toolchain file path
	- `vcpkg integrate install`
	- This will output something like : `CMake projects should use: "-DCMAKE_TOOLCHAIN_FILE=/path/to/vcpkg/scripts/buildsystems/vcpkg.cmake"`
5. Create a build directory
	- `mkdir build`
6. Configure project with CMake
	-  `cmake -B build -S . -DCMAKE_TOOLCHAIN_FILE=/path/to/vcpkg/scripts/buildsystems/vcpkg.cmake`
	- Use the vcpkg cmake toolchain path from above
7. Build the project
	- `cmake --build build`
8. Run the program
	- The executables will be located in the build folder




-DCMAKE_TOOLCHAIN_FILE=C:/dev/vcpkg/scripts/buildsystems/vcpkg.cmake
### CLion (Windows with MSYS2)

1. **Open the project:** File → Open → choose `examples/atoms` (or the whole SSTcore repo).
2. **CMake options:** Settings → Build, Execution, Deployment → CMake. Add:  
   `-DMINGW64_ROOT=C:/msys64/mingw64` (adjust if your MSYS2 is elsewhere).
3. **Toolchain:** Set the CMake profile to use MinGW (e.g. `C:/msys64/mingw64/bin/g++.exe`).
4. **Run:** Select the `atom` target, then Run. Set **Working directory** to `src` (Edit Configurations → Working directory: `$ProjectFileDir$/src`) so paths like `mesh.json` resolve.

### Alternative: Debian/Ubuntu apt workaround

If you don't want to use vcpkg, or you just need a quick way to install the native development packages on Debian/Ubuntu, install these packages and then run the normal CMake steps above:

```bash
sudo apt update
sudo apt install build-essential cmake \
	libglew-dev libglfw3-dev libglm-dev libgl1-mesa-dev
```

This provides the GLEW, GLFW, GLM and OpenGL development files so `find_package(...)` calls in `CMakeLists.txt` can locate the libraries. After installing, run the `cmake -B build -S .` and `cmake --build build` commands as shown in the Build Instructions.

## **How the code works:**
the 2D bohr model works is in atom.cpp, the raytracer and realtime models are right beside
* warning, I would recommend running the realtime model with <100k particles first to be sure, raytracer is super compu-intensive so make sure your system can handle it!