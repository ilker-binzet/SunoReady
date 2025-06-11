#!/usr/bin/env python3
"""
Quick performance analysis focused on bottlenecks
"""

import sys
import os
import time
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.getcwd())

def quick_performance_test():
    """Quick test to identify main bottlenecks"""
    
    try:
        print("⚡ Quick Performance Analysis...")
        
        from audio_utils import AudioProcessor
        import json
        
        # Load config
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Initialize processor
        processor = AudioProcessor(config=config)
        
        # Test file
        test_file = r"output\downloads\Mem ARARAT - Evîn.mp3"
        
        if not os.path.exists(test_file):
            print(f"❌ Test file not found: {test_file}")
            return
        
        print(f"📁 File: {test_file}")
        file_size = os.path.getsize(test_file)
        print(f"📊 Size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        
        # Test file loading time
        start_time = time.time()
        y, sr = processor.load_audio(test_file)
        load_time = time.time() - start_time
        duration = len(y) / sr
        print(f"⏱️ File loading: {load_time:.2f}s for {duration:.1f}s audio")
        
        print(f"\n🔍 Config-based processing test:")
        print(f"   Tempo change: {config['tempo_change']}%")
        
        # Test individual operations with config values
        if config['tempo_change'] != 100:
            start_time = time.time()
            tempo_rate = config['tempo_change'] / 100.0
            y_tempo = processor.change_tempo(y, rate=tempo_rate)
            tempo_time = time.time() - start_time
            print(f"🎵 Tempo change ({tempo_rate}x): {tempo_time:.2f}s")
        
        # Test full processing with timing
        print(f"\n🎵 Full processing test...")
        start_time = time.time()
        
        step_times = []
        last_time = start_time
        
        def timing_callback(progress, message):
            nonlocal last_time
            current_time = time.time()
            step_time = current_time - last_time
            step_times.append((message, step_time))
            
            if step_time > 5:  # Only show slow steps
                print(f"   🐌 SLOW: {message:<35} {step_time:>6.2f}s")
            elif step_time > 1:
                print(f"   ⚠️  MODERATE: {message:<35} {step_time:>6.2f}s")
            
            last_time = current_time
        
        output_path = processor.process_audio_enhanced(
            test_file,
            progress_callback=timing_callback,
            pitch_shift=config["pitch_shift"],
            tempo_change=config["tempo_change"] / 100.0,
            trim_duration=config["trim_duration"],
            normalize=config["normalize_volume"],
            add_noise=config["add_noise"],
            apply_highpass=config["apply_highpass"],
            tempo_stretch=config["tempo_stretch"],
            fade_in=config["fade_in"],
            fade_out=config["fade_out"],
            fade_in_duration=config["fade_in_duration"],
            fade_out_duration=config["fade_out_duration"],
            clean_metadata=config["clean_metadata"]
        )
        
        total_time = time.time() - start_time
        print(f"\n⏰ TOTAL PROCESSING TIME: {total_time:.2f}s ({total_time/60:.1f} minutes)")
        
        # Performance analysis
        ratio = total_time / duration
        print(f"📈 Performance ratio: {ratio:.1f}x (processing time / audio duration)")
        
        if ratio > 3:
            print("🚨 CRITICAL: Processing is extremely slow!")
        elif ratio > 2:
            print("⚠️  WARNING: Processing is very slow!")
        elif ratio > 1:
            print("⚠️  Processing is slower than real-time")
        else:
            print("✅ Processing is faster than real-time")
        
        # Suggest optimizations
        print(f"\n💡 Optimization suggestions:")
        
        for step_name, step_time in step_times:
            if step_time > 30:
                print(f"🔧 CRITICAL BOTTLENECK: {step_name} ({step_time:.1f}s)")
            elif step_time > 10:
                print(f"🔧 Major bottleneck: {step_name} ({step_time:.1f}s)")
        
        if config['pitch_shift'] != 0:
            print(f"💡 Pitch shifting is computationally expensive. Consider:")
            print(f"   - Using FFmpeg for pitch shifting instead of librosa")
            print(f"   - Reducing pitch shift amount")
        
        if config['tempo_change'] != 100:
            print(f"💡 Tempo change with librosa is slow. Consider:")
            print(f"   - Using FFmpeg atempo filter")
            print(f"   - Processing smaller chunks")
        
        if config['trim_duration'] > 120:
            print(f"💡 Long audio processing:")
            print(f"   - Consider trimming first before other operations")
            print(f"   - Process in smaller segments")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_performance_test()
