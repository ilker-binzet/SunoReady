#!/bin/bash
# Cross-platform shared library compilation script for SunoReady
# Compiles sunoready_audio.cpp to appropriate shared library format

echo "🔧 SunoReady Shared Library Compiler"
echo "===================================="

# Detect platform
OS=$(uname -s)
ARCH=$(uname -m)

echo "🖥️ Platform: $OS ($ARCH)"

# Set paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_ROOT/build"
CPP_FILE="$BUILD_DIR/sunoready_audio.cpp"

echo "📂 Project root: $PROJECT_ROOT"
echo "📂 Build directory: $BUILD_DIR"
echo "📄 Source file: $CPP_FILE"

# Check if source file exists
if [ ! -f "$CPP_FILE" ]; then
    echo "❌ Error: Source file not found: $CPP_FILE"
    exit 1
fi

# Set compiler and flags based on platform
case "$OS" in
    "Linux")
        COMPILER="g++"
        OUTPUT_FILE="$BUILD_DIR/sunoready_audio.so"
        COMPILE_FLAGS="-shared -fPIC -O3 -std=c++11"
        LIB_FLAGS=""
        echo "🐧 Linux detected - compiling to .so"
        ;;
    "Darwin")  # macOS
        COMPILER="clang++"
        OUTPUT_FILE="$BUILD_DIR/sunoready_audio.dylib"
        COMPILE_FLAGS="-shared -fPIC -O3 -std=c++11"
        LIB_FLAGS=""
        echo "🍎 macOS detected - compiling to .dylib"
        ;;
    "MINGW"*|"MSYS"*|"CYGWIN"*)  # Windows with MinGW/MSYS
        COMPILER="g++"
        OUTPUT_FILE="$BUILD_DIR/sunoready_audio.dll"
        COMPILE_FLAGS="-shared -O3 -std=c++11"
        LIB_FLAGS=""
        echo "🪟 Windows (MinGW) detected - compiling to .dll"
        ;;
    *)
        echo "❌ Error: Unsupported platform: $OS"
        echo "💡 Supported platforms: Linux, macOS, Windows (MinGW)"
        exit 1
        ;;
esac

# Check if compiler exists
if ! command -v "$COMPILER" &> /dev/null; then
    echo "❌ Error: Compiler '$COMPILER' not found"
    case "$OS" in
        "Linux")
            echo "💡 Install with: sudo apt-get install g++ (Ubuntu/Debian) or sudo yum install gcc-c++ (RHEL/CentOS)"
            ;;
        "Darwin")
            echo "💡 Install Xcode command line tools: xcode-select --install"
            ;;
        "MINGW"*|"MSYS"*|"CYGWIN"*)
            echo "💡 Install MinGW-w64 or use MSYS2"
            ;;
    esac
    exit 1
fi

echo "✅ Compiler found: $COMPILER"

# Clean previous build
if [ -f "$OUTPUT_FILE" ]; then
    echo "🗑️ Removing previous build: $OUTPUT_FILE"
    rm -f "$OUTPUT_FILE"
fi

# Compile
echo "🔨 Compiling shared library..."
echo "📝 Command: $COMPILER $COMPILE_FLAGS \"$CPP_FILE\" -o \"$OUTPUT_FILE\" $LIB_FLAGS"

if $COMPILER $COMPILE_FLAGS "$CPP_FILE" -o "$OUTPUT_FILE" $LIB_FLAGS; then
    echo "✅ Compilation successful!"
    echo "📄 Output: $OUTPUT_FILE"
    
    # Verify the file was created
    if [ -f "$OUTPUT_FILE" ]; then
        FILE_SIZE=$(stat -c%s "$OUTPUT_FILE" 2>/dev/null || stat -f%z "$OUTPUT_FILE" 2>/dev/null || echo "unknown")
        echo "📊 File size: $FILE_SIZE bytes"
        echo "🎉 SunoReady high-performance library is ready!"
        echo ""
        echo "🚀 To test the library:"
        echo "   cd \"$PROJECT_ROOT\""
        echo "   python test_dll_integration.py"
    else
        echo "❌ Error: Output file was not created"
        exit 1
    fi
else
    echo "❌ Compilation failed!"
    echo "💡 Check the error messages above for details"
    exit 1
fi