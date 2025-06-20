#!/usr/bin/env python3
"""
Quick Performance Test for SunoReady
Tests all major components and features
"""

import os
import sys
import time
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test all module imports"""
    print("🔍 Testing module imports...")
    
    try:
        from version import __version__, get_version_string
        print(f"  ✅ Version: {get_version_string()}")
    except ImportError as e:
        print(f"  ❌ Version import failed: {e}")
        return False
    
    try:
        from audio_utils import AudioProcessor
        print("  ✅ AudioProcessor imported")
    except ImportError as e:
        print(f"  ❌ AudioProcessor import failed: {e}")
        return False
    
    try:
        from yt_downloader import YouTubeDownloader
        print("  ✅ YouTubeDownloader imported")
    except ImportError as e:
        print(f"  ❌ YouTubeDownloader import failed: {e}")
        return False
    
    try:
        from audio_processor_dll import AudioProcessorDLL
        print("  ✅ AudioProcessorDLL imported")
    except ImportError as e:
        print(f"  ❌ AudioProcessorDLL import failed: {e}")
        return False
    
    return True

def test_dll_integration():
    """Test DLL loading and performance"""
    print("\n🔧 Testing DLL integration...")
    
    try:
        from audio_processor_dll import AudioProcessorDLL
        processor = AudioProcessorDLL()
        
        if processor.dll_available:
            print("  ✅ DLL loaded successfully")
            print(f"  📍 DLL available: {processor.dll_available}")
            return True
        else:
            print("  ⚠️ DLL not loaded - using Python fallback")
            return True  # Still ok, just slower
    except Exception as e:
        print(f"  ❌ DLL test failed: {e}")
        return False

def test_config_loading():
    """Test configuration file loading"""
    print("\n⚙️ Testing configuration loading...")
    
    config_files = [
        "config/config.json",
        "config/theme_config.json",
        "config/pyproject.toml"
    ]
    
    all_good = True
    for config_file in config_files:
        config_path = project_root / config_file
        if config_path.exists():
            print(f"  ✅ {config_file} exists")
        else:
            print(f"  ❌ {config_file} missing")
            all_good = False
    
    return all_good

def test_assets():
    """Test asset files"""
    print("\n🎨 Testing assets...")
    
    asset_files = [
        "assets/generated-icon.png",
        "assets/fonts/Noto_Sans/NotoSans-VariableFont_wdth,wght.ttf"
    ]
    
    all_good = True
    for asset_file in asset_files:
        asset_path = project_root / asset_file
        if asset_path.exists():
            print(f"  ✅ {asset_file} exists")
        else:
            print(f"  ❌ {asset_file} missing")
            all_good = False
    
    return all_good

def test_build_files():
    """Test build files"""
    print("\n🔨 Testing build files...")
    
    build_files = [
        "build/sunoready_audio.cpp",
        "scripts/compile_dll.bat",
        "scripts/setup_dll.bat"
    ]
    
    all_good = True
    for build_file in build_files:
        build_path = project_root / build_file
        if build_path.exists():
            print(f"  ✅ {build_file} exists")
        else:
            print(f"  ❌ {build_file} missing")
            all_good = False
    
    # Check if DLL exists
    dll_path = project_root / "build/sunoready_audio.dll"
    if dll_path.exists():
        print("  ✅ sunoready_audio.dll compiled")
    else:
        print("  ⚠️ sunoready_audio.dll not compiled (run scripts/compile_dll.bat)")
    
    return all_good

def test_gui_startup():
    """Test GUI startup (without showing window)"""
    print("\n🖥️ Testing GUI startup...")
    
    try:
        # Set environment to prevent window from showing
        os.environ['DISPLAY'] = ':99'  # Fake display for Linux
        
        from app import SunoReadyApp
        print("  ✅ GUI classes imported successfully")
        
        # Don't actually start the GUI, just test import
        return True
    except Exception as e:
        print(f"  ❌ GUI startup test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 SunoReady Quick Performance Test")
    print("=" * 50)
    
    start_time = time.time()
    
    tests = [
        ("Module Imports", test_imports),
        ("DLL Integration", test_dll_integration),
        ("Configuration Loading", test_config_loading),
        ("Assets", test_assets),
        ("Build Files", test_build_files),
        ("GUI Startup", test_gui_startup),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  💥 {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
        if result:
            passed += 1
    
    elapsed = time.time() - start_time
    print(f"\n⏱️ Total time: {elapsed:.2f} seconds")
    print(f"🎯 Score: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! SunoReady is ready to rock! 🎵")
        return 0
    else:
        print(f"\n⚠️ {total - passed} tests failed. Check the issues above.")
        return 1

if __name__ == "__main__":
    exit(main())
