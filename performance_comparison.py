#!/usr/bin/env python3
"""
Quick performance comparison test
"""

import time
import json
from pathlib import Path

# Test both processors
def test_performance_comparison():
    print("=== PERFORMANCE COMPARISON TEST ===")
    
    # Load config
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Find test file
    test_files = []
    for ext in ['.mp3', '.wav']:
        test_files.extend(list(Path("output").rglob(f'*{ext}')))
    
    if not test_files:
        print("No test files found")
        return
    
    input_file = str(test_files[0])
    print(f"Test file: {Path(input_file).name}")
    
    # Test options - realistic scenario
    options = {
        'trim_duration': 90,
        'tempo_change': 120.0,
        'pitch_shift': 2,
        'fade_in': True,
        'fade_out': True,
        'fade_in_duration': 3.0,
        'fade_out_duration': 3.0,
        'normalize': True,
        'clean_metadata': True
    }
    
    # Test 1: Fast Processor
    print("\n1. Testing Fast Processor (FFmpeg-only)...")
    try:
        from fast_processor import FastAudioProcessor
        fast_processor = FastAudioProcessor(config)
        
        start_time = time.time()
        result1 = fast_processor.process_audio_fast(
            input_file, 
            "output/processed/performance_test_fast.mp3", 
            **options
        )
        fast_time = time.time() - start_time
        
        print(f"✅ Fast processor completed in {fast_time:.1f} seconds")
        
        # Check duration
        import subprocess
        cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', 
               '-of', 'default=noprint_wrappers=1:nokey=1', result1]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            duration = float(result.stdout.strip())
            print(f"   Result duration: {duration:.1f}s")
        
    except Exception as e:
        print(f"❌ Fast processor failed: {e}")
        fast_time = float('inf')
    
    # Test 2: Standard Processor
    print("\n2. Testing Standard Processor (Librosa)...")
    try:
        from audio_utils import AudioProcessor
        audio_processor = AudioProcessor(config)
        
        start_time = time.time()
        result2 = audio_processor.process_audio_enhanced(
            input_file,
            "output/processed/performance_test_standard.mp3",
            **{**options, 'tempo_change': options['tempo_change'] / 100.0}  # Convert to rate
        )
        standard_time = time.time() - start_time
        
        print(f"✅ Standard processor completed in {standard_time:.1f} seconds")
        
        # Check duration
        cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', 
               '-of', 'default=noprint_wrappers=1:nokey=1', result2]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            duration = float(result.stdout.strip())
            print(f"   Result duration: {duration:.1f}s")
        
    except Exception as e:
        print(f"❌ Standard processor failed: {e}")
        standard_time = float('inf')
    
    # Comparison
    print("\n" + "="*50)
    print("PERFORMANCE COMPARISON RESULTS:")
    print("="*50)
    
    if fast_time != float('inf') and standard_time != float('inf'):
        speedup = standard_time / fast_time
        print(f"🚀 Fast Processor:     {fast_time:.1f} seconds")
        print(f"🐢 Standard Processor: {standard_time:.1f} seconds")
        print(f"📊 Speed improvement:  {speedup:.1f}x faster!")
        
        if speedup > 5:
            print("🎉 MAJOR PERFORMANCE IMPROVEMENT!")
        elif speedup > 2:
            print("✅ Significant performance improvement")
        else:
            print("⚠️ Modest improvement")
    
    elif fast_time != float('inf'):
        print(f"🚀 Fast Processor:     {fast_time:.1f} seconds")
        print(f"🐢 Standard Processor: FAILED")
        print("📊 Fast processor is the clear winner!")
    
    elif standard_time != float('inf'):
        print(f"🚀 Fast Processor:     FAILED")
        print(f"🐢 Standard Processor: {standard_time:.1f} seconds")
        print("📊 Standard processor is more reliable")
    
    else:
        print("❌ Both processors failed!")

if __name__ == "__main__":
    test_performance_comparison()
