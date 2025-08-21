# Makefile for SunoReady cross-platform audio processing
# Supports Linux, macOS, and Windows (with MinGW)

# Detect OS
UNAME_S := $(shell uname -s)
UNAME_M := $(shell uname -m)

# Set compiler and flags based on OS
ifeq ($(UNAME_S),Linux)
    CC = g++
    SHARED_EXT = .so
    CFLAGS = -shared -fPIC -O3 -std=c++11
    PLATFORM = Linux
endif

ifeq ($(UNAME_S),Darwin)
    CC = clang++
    SHARED_EXT = .dylib
    CFLAGS = -shared -fPIC -O3 -std=c++11
    PLATFORM = macOS
endif

# Windows detection (MinGW/MSYS)
ifeq ($(findstring MINGW,$(UNAME_S)),MINGW)
    CC = g++
    SHARED_EXT = .dll
    CFLAGS = -shared -O3 -std=c++11
    PLATFORM = Windows
endif

ifeq ($(findstring MSYS,$(UNAME_S)),MSYS)
    CC = g++
    SHARED_EXT = .dll
    CFLAGS = -shared -O3 -std=c++11
    PLATFORM = Windows
endif

# Default fallback (assume Linux-like)
ifndef PLATFORM
    CC = g++
    SHARED_EXT = .so
    CFLAGS = -shared -fPIC -O3 -std=c++11
    PLATFORM = Unknown
endif

# Paths
BUILD_DIR = build
SRC_FILE = $(BUILD_DIR)/sunoready_audio.cpp
OUTPUT_FILE = $(BUILD_DIR)/sunoready_audio$(SHARED_EXT)

# Default target
.PHONY: all
all: info build test

# Show build info
.PHONY: info
info:
	@echo "🔧 SunoReady Build System"
	@echo "========================="
	@echo "Platform: $(PLATFORM) ($(UNAME_S) $(UNAME_M))"
	@echo "Compiler: $(CC)"
	@echo "Output:   $(OUTPUT_FILE)"
	@echo ""

# Build the shared library
.PHONY: build
build: $(OUTPUT_FILE)

$(OUTPUT_FILE): $(SRC_FILE)
	@echo "🔨 Compiling shared library for $(PLATFORM)..."
	@$(CC) $(CFLAGS) "$(SRC_FILE)" -o "$(OUTPUT_FILE)"
	@echo "✅ Build successful: $(OUTPUT_FILE)"
	@ls -la "$(OUTPUT_FILE)"

# Test the build
.PHONY: test
test: $(OUTPUT_FILE)
	@echo "🧪 Testing shared library..."
	@python test_dll_integration.py

# Full test suite
.PHONY: test-full
test-full: $(OUTPUT_FILE)
	@echo "🧪 Running full test suite..."
	@python test_cross_platform.py

# Clean build artifacts
.PHONY: clean
clean:
	@echo "🗑️ Cleaning build artifacts..."
	@rm -f $(BUILD_DIR)/*.so $(BUILD_DIR)/*.dll $(BUILD_DIR)/*.dylib
	@echo "✅ Clean completed"

# Install dependencies
.PHONY: deps
deps:
	@echo "📦 Installing Python dependencies..."
	@pip install -r requirements.txt

# Setup development environment
.PHONY: setup
setup: deps build
	@echo "🚀 Development environment ready!"
	@echo "Run 'make test' to verify everything works"

# Help target
.PHONY: help
help:
	@echo "SunoReady Build System"
	@echo "====================="
	@echo ""
	@echo "Targets:"
	@echo "  all        - Build and test (default)"
	@echo "  build      - Compile shared library"
	@echo "  test       - Run DLL integration test"
	@echo "  test-full  - Run complete test suite"
	@echo "  clean      - Remove build artifacts"
	@echo "  deps       - Install Python dependencies"
	@echo "  setup      - Full setup (deps + build)"
	@echo "  info       - Show build information"
	@echo "  help       - Show this help"
	@echo ""
	@echo "Platform support:"
	@echo "  - Linux   (builds .so)"
	@echo "  - macOS   (builds .dylib)"
	@echo "  - Windows (builds .dll with MinGW)"

# Check if source file exists
$(SRC_FILE):
	@if [ ! -f "$(SRC_FILE)" ]; then \
		echo "❌ Source file not found: $(SRC_FILE)"; \
		echo "💡 Make sure the C++ source code is available"; \
		exit 1; \
	fi