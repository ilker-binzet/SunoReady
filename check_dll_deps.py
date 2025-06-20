#!/usr/bin/env python3
"""
DLL Dependency Checker
Check DLL dependencies and try to fix loading issues
"""

import ctypes
import os
import sys

def check_dll_dependencies():
    """Check DLL dependencies and provide solutions"""
    print("🔍 DLL Dependency Checker")
    print("=" * 40)
    
    dll_path = "build\\sunoready_audio.dll"
    
    if not os.path.exists(dll_path):
        print(f"❌ DLL not found: {dll_path}")
        return
    
    print(f"✅ DLL found: {dll_path}")
    print(f"📏 Size: {os.path.getsize(dll_path)} bytes")
    
    # Try loading with different methods
    print("\n🧪 Testing DLL loading methods...")
    
    # Method 1: Direct ctypes.CDLL
    try:
        dll = ctypes.CDLL(os.path.abspath(dll_path))
        print("✅ Method 1 (ctypes.CDLL): SUCCESS")
        return dll
    except Exception as e:
        print(f"❌ Method 1 (ctypes.CDLL): {e}")
    
    # Method 2: ctypes.WinDLL (Windows specific)
    try:
        dll = ctypes.WinDLL(os.path.abspath(dll_path))
        print("✅ Method 2 (ctypes.WinDLL): SUCCESS")
        return dll
    except Exception as e:
        print(f"❌ Method 2 (ctypes.WinDLL): {e}")
    
    # Method 3: Load with different settings
    try:
        os.add_dll_directory(os.path.dirname(os.path.abspath(dll_path)))
        dll = ctypes.CDLL(os.path.abspath(dll_path))
        print("✅ Method 3 (with dll_directory): SUCCESS")
        return dll
    except Exception as e:
        print(f"❌ Method 3 (with dll_directory): {e}")
    
    print("\n💡 Possible solutions:")
    print("1. Install Microsoft Visual C++ Redistributable")
    print("2. Recompile with static linking: g++ -static")
    print("3. Check for missing runtime libraries")
    print("4. Use Dependency Walker to check dependencies")
    
    return None

def create_simple_dll():
    """Create a simple test DLL to verify compilation works"""
    print("\n🔧 Creating simple test DLL...")
    
    simple_cpp = """
#include <cmath>

extern "C" {
    __declspec(dllexport) double test_function(double x) {
        return x * 2.0;
    }
    
    __declspec(dllexport) int add_numbers(int a, int b) {
        return a + b;
    }
}
"""
    
    # Write simple C++ file
    with open("build\\simple_test.cpp", "w") as f:
        f.write(simple_cpp)
    
    # Compile simple test
    os.system("cd build && g++ -shared -o simple_test.dll simple_test.cpp")
    
    if os.path.exists("build\\simple_test.dll"):
        print("✅ Simple test DLL created successfully")
        
        # Test the simple DLL
        try:
            test_dll = ctypes.CDLL("build\\simple_test.dll")
            test_dll.add_numbers.argtypes = [ctypes.c_int, ctypes.c_int]
            test_dll.add_numbers.restype = ctypes.c_int
            
            result = test_dll.add_numbers(5, 3)
            print(f"✅ Simple DLL test: 5 + 3 = {result}")
            
            if result == 8:
                print("✅ DLL compilation and loading works!")
                return True
        except Exception as e:
            print(f"❌ Simple DLL test failed: {e}")
    else:
        print("❌ Simple test DLL creation failed")
    
    return False

if __name__ == "__main__":
    check_dll_dependencies()
    create_simple_dll()
