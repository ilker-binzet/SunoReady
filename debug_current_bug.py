#!/usr/bin/env python3
"""
Debug current issues with the latest config
"""

import subprocess
import os
import json
from pathlib import Path
from audio_utils import AudioProcessor

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

def test_current_config():
    """Test with current user config"""
    print("=== TESTING WITH CURRENT CONFIG ===")
    
    # Load current config
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("Current config settings:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    print()
    
    # Find a test audio file
    test_files = []
    output_dir = Path("output")
    if output_dir.exists():
        for ext in ['.mp3', '.wav']:
            test_files.extend(list(output_dir.rglob(f'*{ext}')))
    
    if not test_files:
        print("No test audio files found in output directory")
        return
    
    # Use the first available file
    input_file = str(test_files[0])
    print(f"Using test file: {input_file}")
    
    # Get original duration
    original_duration = get_audio_duration(input_file)
    print(f"Original duration: {original_duration:.2f}s")
    
    if original_duration is None:
        print("Could not get original duration, aborting test")
        return
    
    processor = AudioProcessor(config)
    
    # Test with current config settings
    output_file = "current_config_test.mp3"
    output_path = f"output/processed/{output_file}"
    
    print(f"\n--- Testing with current config ---")
    print(f"Expected final duration: {config['trim_duration']}s")
    print(f"Tempo setting: {config['tempo_change']}%")
    print(f"Fade in: {config['fade_in']} ({config['fade_in_duration']}s)")
    print(f"Fade out: {config['fade_out']} ({config['fade_out_duration']}s)")
    
    try:
        print("Processing...")
        
        # Use the enhanced processing method
        processor.process_audio_enhanced(
            input_file, 
            output_path,
            trim_duration=config['trim_duration'],
            tempo_change=config['tempo_change'] / 100.0,
            pitch_shift=config['pitch_shift'],
            normalize=config['normalize_volume'],
            add_noise=config['add_noise'],
            apply_highpass=config['apply_highpass'],
            fade_in=config['fade_in'],
            fade_out=config['fade_out'],
            fade_in_duration=config['fade_in_duration'],
            fade_out_duration=config['fade_out_duration'],
            clean_metadata=config['clean_metadata']
        )
        
        # Check result duration
        result_duration = get_audio_duration(output_path)
        if result_duration:
            expected_duration = config['trim_duration']
            print(f"Expected duration: {expected_duration}s")
            print(f"Actual duration: {result_duration:.2f}s")
            
            # Check if there's still a duration bug
            tolerance = 3.0  # 3 second tolerance
            if abs(result_duration - expected_duration) <= tolerance:
                print("✅ Duration is correct!")
            else:
                print(f"❌ DURATION BUG DETECTED!")
                print(f"   Expected: {expected_duration}s")
                print(f"   Got: {result_duration:.2f}s")
                print(f"   Difference: {abs(result_duration - expected_duration):.2f}s")
                
                # Check file size
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
                    print(f"   File size: {file_size:.2f} MB")
                    
                return False
        else:
            print("❌ Could not get result duration")
            return False
            
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_edge_cases():
    """Test edge cases that might reveal bugs"""
    print("\n" + "="*50)
    print("EDGE CASE TESTING")
    print("="*50)
    
    # Load config
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Find a test file
    test_files = []
    output_dir = Path("output")
    if output_dir.exists():
        for ext in ['.mp3', '.wav']:
            test_files.extend(list(output_dir.rglob(f'*{ext}')))
    
    if not test_files:
        print("No test files found")
        return
    
    input_file = str(test_files[0])
    processor = AudioProcessor(config)
    
    edge_cases = [
        {
            'name': 'Very slow tempo + long fade',
            'settings': {
                'tempo_change': 0.5,  # 50%
                'fade_in_duration': 10.0,
                'fade_out_duration': 10.0,
                'trim_duration': 60.0
            }
        },
        {
            'name': 'Very fast tempo + short trim',
            'settings': {
                'tempo_change': 1.8,  # 180%
                'trim_duration': 30.0
            }
        },
        {
            'name': 'All effects combined',
            'settings': {
                'tempo_change': 0.85,
                'pitch_shift': -3,
                'fade_in': True,
                'fade_out': True,
                'fade_in_duration': 5.0,
                'fade_out_duration': 5.0,
                'trim_duration': 75.0,
                'normalize': True,
                'add_noise': True,
                'apply_highpass': True
            }
        }
    ]
    
    for i, test_case in enumerate(edge_cases):
        print(f"\n--- Edge Case {i+1}: {test_case['name']} ---")
        
        output_file = f"edge_case_{i+1}.mp3"
        output_path = f"output/processed/{output_file}"
        
        try:
            processor.process_audio_enhanced(input_file, output_path, **test_case['settings'])
            
            result_duration = get_audio_duration(output_path)
            expected_duration = test_case['settings']['trim_duration']
            
            if result_duration:
                print(f"Expected: {expected_duration}s, Got: {result_duration:.2f}s")
                if abs(result_duration - expected_duration) > 3.0:
                    print(f"⚠️ Duration issue detected!")
                else:
                    print("✅ Duration OK")
            else:
                print("❌ Could not check duration")
                
        except Exception as e:
            print(f"❌ Failed: {e}")

if __name__ == "__main__":
    success = test_current_config()
    if success:
        test_edge_cases()
    else:
        print("\n🚨 Main test failed - investigating...")
        print("Please check the error above for details.")
