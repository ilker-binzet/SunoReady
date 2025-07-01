#!/usr/bin/env python3
"""
Performance optimization for SunoReady audio processing
Creates a lightweight, FFmpeg-only processing pipeline
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path

class FastAudioProcessor:
    """Fast audio processor using only FFmpeg (no librosa)"""
    
    def __init__(self, config):
        self.config = config
        self.processed_output_folder = config.get("processed_output_folder", "output/processed")
        os.makedirs(self.processed_output_folder, exist_ok=True)
    
    def process_audio_fast(self, input_path, output_path=None, progress_callback=None, **options):
        """
        Ultra-fast audio processing using only FFmpeg
        Avoids heavy librosa operations for better performance
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
            
            update_progress(1, 6, "Initializing fast processing...")
            
            # Create processing chain using FFmpeg only
            temp_files = []
            current_file = input_path
            
            # Step 1: Tempo stretch (FFmpeg atempo filter)
            tempo_stretch = options.get('tempo_stretch', 1.0)
            if tempo_stretch != 1.0:
                update_progress(2, 6, f"Applying tempo stretch ({tempo_stretch}x)...")
                temp_tempo = tempfile.mktemp(suffix='.mp3')
                temp_files.append(temp_tempo)
                self._ffmpeg_tempo_stretch(current_file, temp_tempo, tempo_stretch)
                current_file = temp_tempo
            else:
                update_progress(2, 6, "Skipping tempo stretch...")
            
            # Step 2: Pitch shift (FFmpeg asetrate + atempo combination)
            pitch_shift = options.get('pitch_shift', self.config.get('pitch_semitones', 0))
            if pitch_shift != 0:
                update_progress(3, 6, f"Applying pitch shift ({pitch_shift:+d} semitones)...")
                temp_pitch = tempfile.mktemp(suffix='.mp3')
                temp_files.append(temp_pitch)
                self._ffmpeg_pitch_shift(current_file, temp_pitch, pitch_shift)
                current_file = temp_pitch
            else:
                update_progress(3, 6, "Skipping pitch shift...")
            
            # Step 3: Apply fade effects
            fade_in = options.get('fade_in', False)
            fade_out = options.get('fade_out', False)
            if fade_in or fade_out:
                update_progress(4, 6, "Applying fade effects...")
                temp_fade = tempfile.mktemp(suffix='.mp3')
                temp_files.append(temp_fade)
                self._ffmpeg_fade_effects(
                    current_file, temp_fade,
                    fade_in=fade_in,
                    fade_out=fade_out,
                    fade_in_duration=options.get('fade_in_duration', 3.0),
                    fade_out_duration=options.get('fade_out_duration', 3.0)
                )
                current_file = temp_fade
            else:
                update_progress(4, 6, "Skipping fade effects...")
            
            # Step 4: Final trim + normalize + filters in one FFmpeg pass
            update_progress(5, 6, "Applying final effects...")
            filters = []
            
            # Normalize volume
            if options.get('normalize', False):
                filters.append('dynaudnorm=f=75:g=25:p=0.95')
            
            # Highpass filter
            if options.get('apply_highpass', False):
                filters.append('highpass=f=80')
            
            # Trim duration (final step)
            trim_duration = options.get('trim_duration')
            
            # Build final FFmpeg command
            cmd = ['ffmpeg', '-y', '-i', current_file]
            
            # Add time limit for trim
            if trim_duration and trim_duration > 0:
                cmd.extend(['-t', str(trim_duration)])
            
            # Add audio filters
            if filters:
                cmd.extend(['-af', ','.join(filters)])
            
            # High quality output
            cmd.extend(['-c:a', 'libmp3lame', '-b:a', '320k'])
            
            # Remove metadata if requested
            if options.get('clean_metadata', False):
                cmd.extend(['-map_metadata', '-1'])
            
            cmd.append(output_path)
            
            # Run final FFmpeg command
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"FFmpeg error: {result.stderr}")
            
            # Clean up temporary files
            update_progress(6, 6, "Cleaning up...")
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass
            
            update_progress(6, 6, "Fast processing complete!")
            return output_path
            
        except Exception as e:
            # Clean up on error
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass
            raise Exception(f"Fast processing failed: {str(e)}")
    
    def _ffmpeg_tempo_stretch(self, input_path, output_path, speed):
        """Apply tempo stretch using FFmpeg atempo filter"""
        cmd = ['ffmpeg', '-y', '-i', input_path]
        
        # Handle atempo limitations
        if speed == 1.0:
            cmd.extend(['-c', 'copy'])
        elif 0.5 <= speed <= 2.0:
            cmd.extend(['-af', f'atempo={speed}'])
        else:
            # Multiple atempo filters for extreme speeds
            filters = []
            current_speed = speed
            
            while current_speed > 2.0:
                filters.append('atempo=2.0')
                current_speed /= 2.0
            
            while current_speed < 0.5:
                filters.append('atempo=0.5') 
                current_speed /= 0.5
            
            if current_speed != 1.0:
                filters.append(f'atempo={current_speed}')
            
            cmd.extend(['-af', ','.join(filters)])
        
        cmd.extend(['-c:a', 'libmp3lame', '-q:a', '2', output_path])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Tempo stretch failed: {result.stderr}")
    
    def _ffmpeg_pitch_shift(self, input_path, output_path, semitones):
        """Apply pitch shift using FFmpeg (asetrate + atempo combo)"""
        # Calculate pitch shift ratio
        pitch_ratio = 2 ** (semitones / 12.0)
        
        # Use asetrate to change pitch, then atempo to restore tempo
        cmd = [
            'ffmpeg', '-y', '-i', input_path,
            '-af', f'asetrate=44100*{pitch_ratio},atempo={1/pitch_ratio}',
            '-c:a', 'libmp3lame', '-q:a', '2',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Pitch shift failed: {result.stderr}")
    
    def _ffmpeg_fade_effects(self, input_path, output_path, fade_in=False, fade_out=False,
                           fade_in_duration=3.0, fade_out_duration=3.0):
        """Apply fade effects using FFmpeg"""
        # Get duration if needed for fade out
        total_duration = None
        if fade_out:
            probe_cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', 
                        '-of', 'default=noprint_wrappers=1:nokey=1', input_path]
            result = subprocess.run(probe_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                total_duration = float(result.stdout.strip())
        
        # Build filter chain
        filters = []
        
        if fade_in and fade_in_duration > 0:
            filters.append(f'afade=t=in:ss=0:d={fade_in_duration}')
        
        if fade_out and fade_out_duration > 0 and total_duration:
            fade_out_start = max(0, total_duration - fade_out_duration)
            filters.append(f'afade=t=out:st={fade_out_start}:d={fade_out_duration}')
        
        if not filters:
            # No fade effects, just copy
            shutil.copy2(input_path, output_path)
            return
        
        cmd = ['ffmpeg', '-y', '-i', input_path, '-af', ','.join(filters),
               '-c:a', 'libmp3lame', '-q:a', '2', output_path]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Fade effects failed: {result.stderr}")

def test_fast_processor():
    """Test the fast processor"""
    import json
    
    # Load config
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    processor = FastAudioProcessor(config)
    
    # Find test file
    test_files = []
    for ext in ['.mp3', '.wav']:
        test_files.extend(list(Path("output").rglob(f'*{ext}')))
    
    if not test_files:
        print("No test files found")
        return
    
    input_file = str(test_files[0])
    output_file = "output/processed/fast_test.mp3"
    
    print(f"Testing fast processing with: {Path(input_file).name}")
    
    import time
    start_time = time.time()
    
    # Test options
    options = {
        'trim_duration': 90,
        'tempo_change': 110.0,
        'fade_in': True,
        'fade_out': True,
        'fade_in_duration': 3.0,
        'fade_out_duration': 3.0,
        'normalize': True,
        'clean_metadata': True
    }
    
    try:
        result = processor.process_audio_fast(input_file, output_file, **options)
        end_time = time.time()
        
        print(f"✅ Fast processing completed in {end_time - start_time:.1f} seconds")
        print(f"📁 Output: {result}")
        
        # Check duration
        cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', 
               '-of', 'default=noprint_wrappers=1:nokey=1', result]
        probe_result = subprocess.run(cmd, capture_output=True, text=True)
        if probe_result.returncode == 0:
            duration = float(probe_result.stdout.strip())
            print(f"⏱️ Result duration: {duration:.1f}s (target: 90s)")
        
    except Exception as e:
        print(f"❌ Fast processing failed: {e}")

if __name__ == "__main__":
    test_fast_processor()
