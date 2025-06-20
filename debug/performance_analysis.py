#!/usr/bin/env python3
"""
Comprehensive performance analysis with detailed timing
Compare original vs current processing pipeline
"""

import time
import subprocess
import os
import json
import tempfile
import shutil
from pathlib import Path

def get_audio_duration(file_path):
    """Get audio duration using ffprobe"""
    try:
        cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', 
               '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return float(result.stdout.strip())
        return None
    except Exception as e:
        print(f"Error getting duration: {e}")
        return None

def time_function(func, *args, **kwargs):
    """Time a function execution"""
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    execution_time = end_time - start_time
    return result, execution_time

def test_minimal_ffmpeg_only():
    """Test minimal FFmpeg-only processing"""
    print("="*60)
    print("MINIMAL FFMPEG-ONLY TEST")
    print("="*60)
    
    # Find test file
    test_files = list(Path("output").rglob("*.mp3"))
    if not test_files:
        print("No test files found")
        return
    
    input_file = str(test_files[0])
    print(f"Input: {Path(input_file).name}")
    
    # Get original duration
    original_duration = get_audio_duration(input_file)
    print(f"Original duration: {original_duration:.1f}s")
    
    # Test cases with increasing complexity
    test_cases = [
        {
            'name': 'Simple trim only',
            'cmd': ['ffmpeg', '-y', '-i', input_file, '-t', '75', '-c', 'copy', 'test_simple.mp3']
        },
        {
            'name': 'Trim + re-encode',
            'cmd': ['ffmpeg', '-y', '-i', input_file, '-t', '75', '-c:a', 'libmp3lame', '-b:a', '320k', 'test_reencode.mp3']
        },
        {
            'name': 'Trim + normalize',
            'cmd': ['ffmpeg', '-y', '-i', input_file, '-t', '75', '-af', 'dynaudnorm', '-c:a', 'libmp3lame', '-b:a', '320k', 'test_normalize.mp3']
        },
        {
            'name': 'Trim + tempo 105%',
            'cmd': ['ffmpeg', '-y', '-i', input_file, '-t', '75', '-af', 'atempo=1.05', '-c:a', 'libmp3lame', '-b:a', '320k', 'test_tempo.mp3']
        },
        {
            'name': 'All effects',
            'cmd': ['ffmpeg', '-y', '-i', input_file, '-t', '75', '-af', 'atempo=1.05,dynaudnorm,highpass=f=80', '-c:a', 'libmp3lame', '-b:a', '320k', 'test_all.mp3']
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        
        def run_ffmpeg():
            result = subprocess.run(test_case['cmd'], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"FFmpeg failed: {result.stderr}")
            return result
        
        try:
            result, exec_time = time_function(run_ffmpeg)
            output_file = test_case['cmd'][-1]
            
            # Check result
            if os.path.exists(output_file):
                result_duration = get_audio_duration(output_file)
                file_size = os.path.getsize(output_file) / (1024 * 1024)
                
                print(f"✅ Success: {exec_time:.2f}s")
                print(f"   Duration: {result_duration:.1f}s")
                print(f"   Size: {file_size:.1f}MB")
                
                # Clean up
                os.remove(output_file)
            else:
                print(f"❌ Output file not created")
                
        except Exception as e:
            print(f"❌ Failed: {e}")

def test_current_audio_utils():
    """Test current audio_utils processing"""
    print("\n" + "="*60)
    print("CURRENT AUDIO_UTILS TEST")
    print("="*60)
    
    # Load config
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("Current config:")
    for key, value in config.items():
        if key in ['pitch_shift', 'tempo_change', 'trim_duration', 'fade_in', 'fade_out', 'use_fast_processing']:
            print(f"  {key}: {value}")
    print()
    
    # Find test file
    test_files = list(Path("output").rglob("*.mp3"))
    if not test_files:
        print("No test files found")
        return
    
    input_file = str(test_files[0])
    print(f"Input: {Path(input_file).name}")
    
    # Test different processing modes
    test_modes = [
        {
            'name': 'Fast Processor',
            'use_fast': True,
            'config_override': {'use_fast_processing': True, 'fade_in': False, 'fade_out': False}
        },
        {
            'name': 'Standard Processor',
            'use_fast': False,
            'config_override': {'use_fast_processing': False, 'fade_in': False, 'fade_out': False}
        }
    ]
    
    for mode in test_modes:
        print(f"\n--- {mode['name']} ---")
        
        # Update config for this test
        test_config = config.copy()
        test_config.update(mode['config_override'])
        
        def run_processor():
            if mode['use_fast']:
                from fast_processor import FastAudioProcessor
                processor = FastAudioProcessor(test_config)
                return processor.process_audio_fast(
                    input_file,
                    f"test_{mode['name'].lower().replace(' ', '_')}.mp3",
                    **{
                        'trim_duration': test_config['trim_duration'],
                        'tempo_change': test_config['tempo_change'],
                        'pitch_shift': test_config['pitch_shift'],
                        'normalize': test_config['normalize_volume'],
                        'apply_highpass': test_config['apply_highpass'],
                        'clean_metadata': test_config['clean_metadata']
                    }
                )
            else:
                from audio_utils import AudioProcessor
                processor = AudioProcessor(test_config)
                return processor.process_audio_enhanced(
                    input_file,
                    f"test_{mode['name'].lower().replace(' ', '_')}.mp3",
                    **{
                        'trim_duration': test_config['trim_duration'],
                        'tempo_change': test_config['tempo_change'] / 100.0,
                        'pitch_shift': test_config['pitch_shift'],
                        'normalize': test_config['normalize_volume'],
                        'apply_highpass': test_config['apply_highpass'],
                        'clean_metadata': test_config['clean_metadata']
                    }
                )
        
        try:
            result_path, exec_time = time_function(run_processor)
            
            if os.path.exists(result_path):
                result_duration = get_audio_duration(result_path)
                file_size = os.path.getsize(result_path) / (1024 * 1024)
                
                print(f"✅ Success: {exec_time:.2f}s")
                print(f"   Duration: {result_duration:.1f}s")
                print(f"   Size: {file_size:.1f}MB")
                
                # Performance rating
                if exec_time < 5:
                    print(f"   Performance: 🚀 Excellent")
                elif exec_time < 15:
                    print(f"   Performance: ✅ Good")
                elif exec_time < 30:
                    print(f"   Performance: ⚠️ Slow")
                else:
                    print(f"   Performance: 🐌 Very Slow")
                
                # Clean up
                os.remove(result_path)
            else:
                print(f"❌ Output file not created")
                
        except Exception as e:
            print(f"❌ Failed: {e}")

def analyze_bottlenecks():
    """Analyze potential bottlenecks"""
    print("\n" + "="*60)
    print("BOTTLENECK ANALYSIS")
    print("="*60)
    
    # Check librosa import time
    print("Testing librosa import time...")
    
    def import_librosa():
        import librosa
        return librosa
    
    librosa_mod, import_time = time_function(import_librosa)
    print(f"Librosa import: {import_time:.2f}s")
    
    if import_time > 2:
        print("⚠️ Librosa import is slow - this adds overhead to every processing")
    
    # Test file I/O
    test_files = list(Path("output").rglob("*.mp3"))
    if test_files:
        input_file = str(test_files[0])
        print(f"\nTesting file I/O with: {Path(input_file).name}")
        
        def load_with_librosa():
            y, sr = librosa_mod.load(input_file, sr=44100)
            return y, sr
        
        (y, sr), load_time = time_function(load_with_librosa)
        print(f"Librosa load: {load_time:.2f}s for {len(y)/sr:.1f}s audio")
        
        if load_time > len(y)/sr:  # If load time > audio duration
            print("⚠️ Loading takes longer than audio duration - major bottleneck!")
        
        # Test pitch shift
        if len(y) > 0:
            print("\nTesting librosa effects...")
            
            def test_pitch_shift():
                return librosa_mod.effects.pitch_shift(y[:sr*10], sr=sr, n_steps=2)  # 10 seconds only
            
            def test_time_stretch():
                return librosa_mod.effects.time_stretch(y[:sr*10], rate=1.05)  # 10 seconds only
            
            try:
                _, pitch_time = time_function(test_pitch_shift)
                print(f"Pitch shift (10s): {pitch_time:.2f}s")
                
                _, tempo_time = time_function(test_time_stretch)
                print(f"Time stretch (10s): {tempo_time:.2f}s")
                
                if pitch_time > 5 or tempo_time > 5:
                    print("🚨 Librosa effects are extremely slow!")
                    print("💡 Recommendation: Use FFmpeg-only processing")
                
            except Exception as e:
                print(f"❌ Librosa effects failed: {e}")

def main():
    """Run comprehensive performance analysis"""
    print("SUNOREADY PERFORMANCE ANALYSIS")
    print("Starting comprehensive timing tests...")
    print(f"Test time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_total = time.time()
    
    # Run tests
    test_minimal_ffmpeg_only()
    test_current_audio_utils()
    analyze_bottlenecks()
    
    end_total = time.time()
    total_time = end_total - start_total
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total analysis time: {total_time:.1f}s")
    print()
    print("🎯 RECOMMENDATIONS:")
    print("1. Use FFmpeg-only processing for best performance")
    print("2. Avoid librosa for real-time processing")
    print("3. Remove fade effects if not essential")
    print("4. Keep config simple (basic trim + tempo only)")

if __name__ == "__main__":
    main()
