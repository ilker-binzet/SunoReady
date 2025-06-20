@echo off
echo 🔧 SunoReady DLL Quick Setup
echo ================================

REM Change to project root directory
cd /d "%~dp0.."

echo.
echo 📦 Step 1: Install MinGW-w64 (if not already installed)
g++ --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ MinGW-w64 not found. Installing...
    winget install mingw-w64
) else (
    echo ✅ MinGW-w64 is already installed
)
echo.

echo 🔨 Step 2: Compiling DLL...
if exist "build\sunoready_audio.cpp" (
    echo ✅ Source file found: build\sunoready_audio.cpp
    
    echo 🚀 Attempting compilation...
    cd build
    g++ -shared -fPIC -O3 -march=native -DNDEBUG sunoready_audio.cpp -o sunoready_audio.dll -static-libgcc -static-libstdc++ 2>compilation_errors.txt
    
    if exist sunoready_audio.dll (
        echo ✅ SUCCESS! DLL compiled successfully
        echo 📁 Output: build\sunoready_audio.dll
        del compilation_errors.txt 2>nul
        cd ..
    ) else (
        echo ❌ Compilation failed
        echo 📋 Check build\compilation_errors.txt for details
        if exist compilation_errors.txt (
            echo.
            echo Error details:
            type compilation_errors.txt
        )
        cd ..
    )
) else (
    echo ❌ Source file not found: build\sunoready_audio.cpp
    echo Please ensure the C++ source file is in the build directory
)
) else (
    echo ❌ Source file not found: sunoready_audio.cpp
)

echo.
echo 🧪 Step 3: Testing DLL integration...
python -c "from audio_processor_dll import is_dll_available, get_processor_info; print('DLL Available:', is_dll_available()); print('Info:', get_processor_info())" 2>test_errors.txt

if %ERRORLEVEL% == 0 (
    echo ✅ Python integration test successful
    del test_errors.txt 2>nul
) else (
    echo ❌ Python integration test failed
    if exist test_errors.txt (
        echo Error details:
        type test_errors.txt
    )
)

echo.
echo 📊 Step 4: Running performance benchmark...
python performance_benchmark.py

echo.
echo 🎉 Setup completed!
echo 💡 If there were errors, check the error files for details
pause
