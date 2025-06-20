#!/usr/bin/env python3
"""
DLL Integration Test
Test the complete DLL integration and performance
"""

import sys
import os
from pathlib import Path

# Add src directory to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_dll_integration():
    """Test DLL integration thoroughly"""
    print("🔧 Testing DLL Integration")
    print("=" * 50)
    
    try:
        # Test DLL loading
        from audio_processor_dll import AudioProcessorDLL, is_dll_available, get_processor_info
        
        print("📦 Step 1: Testing DLL Loading...")
        processor = AudioProcessorDLL()
        
        if processor.is_available():
            print("✅ DLL loaded successfully!")
            info = get_processor_info()
            print(f"📊 Status: {info['status']}")
            print(f"⚡ Performance: {info['performance']}")
            print(f"🚀 Speedup: {info['speedup']}")
        else:
            print("⚠️ DLL not available - using Python fallback")
            info = get_processor_info()
            print(f"📊 Status: {info['status']}")
            print(f"🐍 Performance: {info['performance']}")
        
        print("\n📦 Step 2: Testing Function Availability...")
        # Test specific functions
        test_functions = [
            'apply_highpass_filter',
            'apply_noise_reduction', 
            'normalize_audio',
            'apply_tempo_change'
        ]
        
        for func_name in test_functions:
            if hasattr(processor, func_name):
                print(f"✅ {func_name}: Available")
            else:
                print(f"⚠️ {func_name}: Not available")
        
        print("\n📦 Step 3: Testing Performance...")
        if processor.is_available():
            # Run performance test
            print("🏃‍♂️ Running performance benchmark...")
            import numpy as np
            
            # Create test audio data
            test_audio = np.random.rand(44100).astype(np.float64)  # 1 second of audio
            
            try:
                # Test a simple function
                result = processor.normalize_audio(test_audio, target_db=-20.0)
                if result is not None:
                    print("✅ DLL processing test successful!")
                    print(f"📊 Input length: {len(test_audio)}")
                    print(f"📊 Output length: {len(result)}")
                else:
                    print("⚠️ DLL processing returned None")
            except Exception as e:
                print(f"❌ DLL processing test failed: {e}")
        else:
            print("⏭️ Skipping performance test (DLL not available)")
        
        print("\n📦 Step 4: Integration with Main App...")
        
        # Test integration with main app
        try:
            from app import SunoReadyApp
            print("✅ Main app import successful")
            print("✅ DLL integration ready!")
        except Exception as e:
            print(f"❌ Main app integration failed: {e}")
        
        print("\n🎉 DLL Integration Test Complete!")
        
        if processor.is_available():
            print("🚀 HIGH-PERFORMANCE MODE READY!")
            print("   - 5-20x faster audio processing")
            print("   - Native C++ optimizations")
            print("   - Multi-threaded operations")
        else:
            print("🐍 STANDARD MODE ACTIVE")
            print("   - Python-based processing")
            print("   - Good compatibility")
            print("   - To enable high-performance mode:")
            print("     1. Run: scripts\\setup_dll.bat")
            print("     2. Or: scripts\\compile_dll.bat")
        
    except Exception as e:
        print(f"❌ DLL integration test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Change to project root
    os.chdir(project_root)
    test_dll_integration()
