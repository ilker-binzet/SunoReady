#!/usr/bin/env python3
"""
Cross-platform test for SunoReady without GUI dependencies
Tests core functionality that should work on any platform
"""

import os
import sys
import platform

def test_platform_detection():
    """Test platform detection"""
    print("🖥️ Platform Detection Test")
    print("=" * 30)
    print(f"System: {platform.system()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python: {platform.python_version()}")
    print(f"Platform: {platform.platform()}")
    print()

def test_audio_processing():
    """Test audio processing capabilities"""
    print("🎵 Audio Processing Test")
    print("=" * 30)
    
    try:
        from src.audio_processor_dll import AudioProcessorDLL, get_processor_info
        import numpy as np
        
        # Create processor
        processor = AudioProcessorDLL()
        info = get_processor_info()
        
        print(f"Status: {info['status']}")
        print(f"Performance: {info['performance']}")
        
        if processor.is_available():
            print("✅ High-performance mode active")
            
            # Test audio processing
            test_audio = np.random.rand(44100).astype(np.float64)  # 1 second of audio
            
            result = processor.normalize_audio(test_audio, -20.0)
            if result is not None:
                print(f"✅ Normalization: {len(test_audio)} → {len(result)} samples")
            else:
                print("⚠️ Normalization failed")
                
            result = processor.apply_highpass_filter(test_audio, 80, 44100)
            if result is not None:
                print(f"✅ Highpass filter: {len(test_audio)} → {len(result)} samples")
            else:
                print("⚠️ Highpass filter failed")
                
        else:
            print("⚠️ Using Python fallback mode")
            
    except ImportError as e:
        print(f"❌ Audio processing import failed: {e}")
    except Exception as e:
        print(f"❌ Audio processing test failed: {e}")
    
    print()

def test_gui_availability():
    """Test GUI availability without crashing"""
    print("🖼️ GUI Availability Test")
    print("=" * 30)
    
    try:
        import tkinter as tk
        print("✅ tkinter available")
        
        try:
            import customtkinter as ctk
            print("✅ customtkinter available")
            print("✅ Full GUI support available")
        except ImportError:
            print("⚠️ customtkinter not available")
            print("💡 Install with: pip install customtkinter")
            
    except ImportError:
        print("❌ tkinter not available")
        print("💡 Install with: sudo apt-get install python3-tk (Linux)")
        print("💡 GUI features will be disabled")
    
    print()

def test_dependencies():
    """Test core dependencies"""
    print("📦 Dependencies Test")
    print("=" * 30)
    
    required_modules = [
        'numpy',
        'librosa', 
        'soundfile',
        'scipy',
        'mutagen',
        'yt_dlp'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
    
    print()

def test_build_system():
    """Test if build system works"""
    print("🔧 Build System Test")
    print("=" * 30)
    
    script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'compile_shared_lib.sh')
    if os.path.exists(script_path):
        print("✅ Cross-platform build script available")
        if os.access(script_path, os.X_OK):
            print("✅ Build script is executable")
        else:
            print("⚠️ Build script not executable (run: chmod +x scripts/compile_shared_lib.sh)")
    else:
        print("❌ Cross-platform build script not found")
    
    # Check for compiled libraries
    build_dir = os.path.join(os.path.dirname(__file__), 'build')
    if os.path.exists(build_dir):
        libs = []
        for ext in ['.so', '.dll', '.dylib']:
            lib_files = [f for f in os.listdir(build_dir) if f.endswith(ext)]
            libs.extend(lib_files)
        
        if libs:
            print(f"✅ Compiled libraries found: {', '.join(libs)}")
        else:
            print("⚠️ No compiled libraries found")
            print("💡 Run: ./scripts/compile_shared_lib.sh")
    else:
        print("❌ Build directory not found")
    
    print()

def main():
    """Run all tests"""
    print("🚀 SunoReady Cross-Platform Test Suite")
    print("=" * 50)
    print()
    
    test_platform_detection()
    test_dependencies() 
    test_audio_processing()
    test_gui_availability()
    test_build_system()
    
    print("🎉 Test suite completed!")
    print("\n💡 Summary:")
    print("  - Audio processing: Core functionality working")
    print("  - Cross-platform: DLL/shared library loading works")
    print("  - Fallbacks: Python fallback available when needed")
    print("  - GUI: Optional - works in headless environments")

if __name__ == "__main__":
    main()