# SunoReady DLL Compilation Script
# Compiles C++ code to DLL for Windows

# Method 1: Using MinGW-w64 (Recommended)
echo "🔧 Compiling SunoReady Audio DLL..."

# Install MinGW-w64 if not available:
# winget install mingw-w64

# Compile command:
g++ -shared -fPIC -O3 -march=native -DNDEBUG sunoready_audio.cpp -o sunoready_audio.dll -static-libgcc -static-libstdc++

echo "✅ DLL compilation completed!"
echo "📁 Output: sunoready_audio.dll"

# Method 2: Using Visual Studio (Alternative)
# cl /LD /O2 /GL sunoready_audio.cpp /Fe:sunoready_audio.dll

# Method 3: Using CMake (Cross-platform)
# Create CMakeLists.txt:
# cmake_minimum_required(VERSION 3.10)
# project(SunoReadyAudio)
# add_library(sunoready_audio SHARED sunoready_audio.cpp)
# target_compile_options(sunoready_audio PRIVATE -O3 -march=native)
