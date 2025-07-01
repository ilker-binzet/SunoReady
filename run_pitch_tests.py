#!/usr/bin/env python3
"""
Simple runner for pitch shifting tests
Execute this script to run all pitch shifting tests
"""

import sys
import os
from pathlib import Path

# Add tests directory to path
tests_path = Path(__file__).parent / "tests"
sys.path.insert(0, str(tests_path))

try:
    from test_pitch_shifting import run_pitch_shifting_tests
    
    if __name__ == "__main__":
        print("🎵 SunoReady - Pitch Shifting Test Suite")
        print("🚀 Testing pitch shifting functionality...")
        print()
        
        success = run_pitch_shifting_tests()
        
        if success:
            print("\n✅ All tests passed! Pitch shifting is working correctly.")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed. Please check the output above.")
            sys.exit(1)
            
except ImportError as e:
    print(f"❌ Failed to import test module: {e}")
    print("Make sure all dependencies are installed:")
    print("  pip install librosa soundfile scipy numpy customtkinter")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error running tests: {e}")
    sys.exit(1)
