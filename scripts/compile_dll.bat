@echo off
REM SunoReady DLL Compilation Script
REM Compiles C++ code to DLL for Windows

echo 🔧 Compiling SunoReady Audio DLL...

REM Change to project root directory
cd /d "%~dp0.."

REM Check if build directory exists
if not exist "build" mkdir build

REM Check if source file exists
if not exist "build\sunoready_audio.cpp" (
    echo ❌ Source file not found: build\sunoready_audio.cpp
    echo Please ensure the C++ source file is in the build directory
    pause
    exit /b 1
)

REM Method 1: Using MinGW-w64 (Recommended)
echo Checking for MinGW-w64...
g++ --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ MinGW-w64 not found. Installing via winget...
    winget install mingw-w64
    if %errorlevel% neq 0 (
        echo ❌ Failed to install MinGW-w64
        echo Please install manually from: https://www.mingw-w64.org/
        pause
        exit /b 1
    )
)

REM Compile the DLL with static linking
echo Compiling with static linking and optimizations...
cd build
g++ -shared -static -fPIC -O3 -march=native -DNDEBUG sunoready_audio.cpp -o sunoready_audio.dll -static-libgcc -static-libstdc++ -lm

if %errorlevel% equ 0 (
    echo ✅ DLL compilation completed successfully!
    echo 📁 Output: build\sunoready_audio.dll
    echo 🚀 High-performance mode is now available!
) else (
    echo ❌ Compilation failed
    echo Check the error messages above
)

cd ..
pause
