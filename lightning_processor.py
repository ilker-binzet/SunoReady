#!/usr/bin/env python3
"""
Ultra-minimal, lightning-fast audio processor
Only essential features, maximum performance
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path

class LightningProcessor:
    """Ultra-fast audio processor - only essential features"""
    
    def __init__(self, config):
        self.config = config
        self.processed_output_folder = config.get("processed_output_folder", "output/processed")
        os.makedirs(self.processed_output_folder, exist_ok=True)
    
    def process_lightning_fast(self, input_path, output_path=None, progress_callback=None, **options):
        """
        Lightning-fast processing - FFmpeg only, minimal steps
        """
        try:
            def update_progress(step, total_steps, message=""):
                if progress_callback:
                    progress = step / total_steps
                    progress_callback(progress, message)
                    
            if output_path is None:
                input_name = Path(input_path).stem
                output_path = f"{self.processed_output_folder}/{input_name}_processed.mp3"
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            update_progress(1, 3, "Initializing lightning processing...")
            
            # Build single FFmpeg command with all effects
            cmd = ['ffmpeg', '-y', '-i', input_path]
            
            # Audio filters chain
            filters = []
            
            # Tempo change (if needed)
            tempo_change = options.get('tempo_change', 100.0)
            if tempo_change != 100.0:
                tempo_rate = tempo_change / 100.0
                if 0.5 <= tempo_rate <= 2.0:
                    filters.append(f'atempo={tempo_rate}')
                elif tempo_rate > 2.0:
                    # Multiple atempo for extreme speeds
                    current = tempo_rate
                    while current > 2.0:
                        filters.append('atempo=2.0')
                        current /= 2.0
                    if current != 1.0:
                        filters.append(f'atempo={current}')
                elif tempo_rate < 0.5:
                    # Multiple atempo for slow speeds
                    current = tempo_rate
                    while current < 0.5:
                        filters.append('atempo=0.5')
                        current /= 0.5
                    if current != 1.0:
                        filters.append(f'atempo={current}')
            
            # Normalize (if enabled)
            if options.get('normalize', False):
                filters.append('dynaudnorm=f=75:g=25:p=0.95')
            
            # Highpass filter (if enabled)
            if options.get('apply_highpass', False):
                filters.append('highpass=f=80')
            
            update_progress(2, 3, "Applying effects...")
            
            # Add filters if any
            if filters:
                cmd.extend(['-af', ','.join(filters)])
            
            # Trim duration (final step)
            trim_duration = options.get('trim_duration')
            if trim_duration and trim_duration > 0:
                cmd.extend(['-t', str(trim_duration)])
            
            # Output settings - high quality, fast encoding
            cmd.extend(['-c:a', 'libmp3lame', '-b:a', '320k'])
            
            # Remove metadata if requested
            if options.get('clean_metadata', False):
                cmd.extend(['-map_metadata', '-1'])
            
            cmd.append(output_path)
            
            # Run single FFmpeg command
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"FFmpeg error: {result.stderr}")
            
            update_progress(3, 3, "Lightning processing complete!")
            return output_path
            
        except Exception as e:
            raise Exception(f"Lightning processing failed: {str(e)}")

def test_lightning_processor():
    """Test the lightning processor"""
    import json
    import time
    
    # Load config
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    processor = LightningProcessor(config)
    
    # Find test file
    test_files = list(Path("output").rglob("*.mp3"))
    if not test_files:
        print("No test files found")
        return
    
    input_file = str(test_files[0])
    output_file = "output/processed/lightning_test.mp3"
    
    print(f"⚡ LIGHTNING PROCESSOR TEST")
    print(f"Input: {Path(input_file).name}")
    
    # Test options from config
    options = {
        'trim_duration': config['trim_duration'],
        'tempo_change': config['tempo_change'],
        'normalize': config['normalize_volume'],
        'apply_highpass': config['apply_highpass'],
        'clean_metadata': config['clean_metadata']
    }
    
    print(f"Options: {options}")
    
    start_time = time.time()
    
    try:
        result = processor.process_lightning_fast(input_file, output_file, **options)
        end_time = time.time()
        
        execution_time = end_time - start_time
        print(f"⚡ Lightning processing: {execution_time:.2f}s")
        
        # Check result
        if os.path.exists(result):
            # Get duration
            cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', 
                   '-of', 'default=noprint_wrappers=1:nokey=1', result]
            probe_result = subprocess.run(cmd, capture_output=True, text=True)
            if probe_result.returncode == 0:
                duration = float(probe_result.stdout.strip())
                file_size = os.path.getsize(result) / (1024 * 1024)
                
                print(f"✅ Result duration: {duration:.1f}s (target: {config['trim_duration']}s)")
                print(f"📁 File size: {file_size:.1f}MB")
                
                # Performance rating
                if execution_time < 2:
                    print(f"🚀 Performance: LIGHTNING FAST!")
                elif execution_time < 5:
                    print(f"⚡ Performance: Very Fast")
                else:
                    print(f"⚠️ Performance: Could be faster")
        
    except Exception as e:
        print(f"❌ Lightning processing failed: {e}")

if __name__ == "__main__":
    test_lightning_processor()
