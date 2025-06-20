"""
Audio processing utilities for SunoReady
Handles pitch shifting, tempo changes, trimming, normalization, effects, and advanced features
"""

from typing import Optional, Tuple, Union
import numpy as np
import os
import subprocess
from pathlib import Path
import tempfile
import shutil

# Critical imports with error handling
try:
    import librosa
    librosa_available = True
except ImportError as e:
    print(f"Warning: librosa import failed: {e}")
    librosa = None
    librosa_available = False

try:
    import soundfile as sf
    soundfile_available = True
except ImportError as e:
    print(f"Warning: soundfile import failed: {e}")
    sf = None
    soundfile_available = False

try:
    from scipy import signal
    scipy_available = True
except ImportError as e:
    print(f"Warning: scipy import failed: {e}")
    signal = None
    scipy_available = False

try:
    import ffmpeg
    ffmpeg_available = True
except ImportError as e:
    print(f"Warning: ffmpeg-python import failed: {e}")
    ffmpeg = None
    ffmpeg_available = False

try:
    import mutagen
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from mutagen.mp4 import MP4
    mutagen_available = True
except ImportError as e:
    print(f"Warning: mutagen import failed: {e}")
    mutagen = None
    MP3 = None
    FLAC = None
    MP4 = None
    mutagen_available = False

class AudioProcessor:
    def __init__(self, config=None):
        self.sample_rate = 44100
        self.config = config or {}
        
        # Set output directory from config
        self.processed_output_folder = self.config.get('processed_output_folder', 'output/processed')
        
        # Check if required libraries are available
        if librosa is None:
            raise ImportError("librosa is required but not available")
        if sf is None:
            raise ImportError("soundfile is required but not available")
        if signal is None:
            raise ImportError("scipy.signal is required but not available")
            
    def load_audio(self, file_path):
        """Load audio file using librosa"""
        if librosa is None:
            raise ImportError("librosa is not available")
            
        try:
            # Load audio file
            y, sr = librosa.load(file_path, sr=self.sample_rate)
            return y, sr
        except Exception as e:
            raise Exception(f"Failed to load audio file {file_path}: {str(e)}")
    
    def save_audio(self, y, sr, output_path):
        """Save audio file using soundfile"""
        if sf is None:
            raise ImportError("soundfile is not available")
            
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save as WAV first (high quality)
            temp_wav = output_path.replace('.mp3', '_temp.wav')
            sf.write(temp_wav, y, sr)
            
            # Convert to MP3 using FFmpeg
            self._convert_to_mp3(temp_wav, output_path)
            
            # Remove temporary WAV file
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
                
            return output_path
            
        except Exception as e:
            raise Exception(f"Failed to save audio file {output_path}: {str(e)}")
    
    def _convert_to_mp3(self, input_path, output_path):
        """Convert audio file to MP3 using FFmpeg"""
        try:
            cmd = [
                'ffmpeg', '-y',  # -y to overwrite output files
                '-i', input_path,
                '-codec:a', 'libmp3lame',
                '-b:a', '320k',  # High quality MP3
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"FFmpeg error: {result.stderr}")
                
        except FileNotFoundError:
            raise Exception("FFmpeg not found. Please install FFmpeg and add it to your PATH.")
        except Exception as e:
            raise Exception(f"Failed to convert to MP3: {str(e)}")
    
    def change_pitch(self, y, n_steps):
        """Change pitch by n_steps semitones"""
        if n_steps == 0:
            return y
        
        if not librosa_available:
            raise ImportError("librosa is required for pitch shifting")
        
        try:
            # Use librosa's pitch shift
            y_shifted = librosa.effects.pitch_shift(y, sr=self.sample_rate, n_steps=n_steps)  # type: ignore
            return y_shifted
        except Exception as e:
            raise Exception(f"Failed to change pitch: {str(e)}")
    
    def change_tempo(self, y, rate):
        """Change tempo by rate (1.0 = no change, 1.2 = 20% faster)"""
        if rate == 1.0:
            return y
        
        try:
            # Use librosa's time stretch - FIXED VERSION
            y_stretched = librosa.effects.time_stretch(y, rate=rate)
            
            # Debug: Check if output makes sense
            input_duration = len(y) / self.sample_rate
            output_duration = len(y_stretched) / self.sample_rate
            expected_duration = input_duration / rate
            
            print(f"DEBUG tempo change:")
            print(f"  Input duration: {input_duration:.2f}s")
            print(f"  Rate: {rate}")
            print(f"  Expected duration: {expected_duration:.2f}s")
            print(f"  Actual duration: {output_duration:.2f}s")
            
            # Safety check - if result is way off, return original
            if abs(output_duration - expected_duration) > expected_duration * 0.1:  # 10% tolerance
                print(f"WARNING: Tempo change result is suspicious, using original audio")
                return y
            
            return y_stretched
        except Exception as e:
            print(f"WARNING: Tempo change failed: {str(e)}, using original audio")
            return y
    
    def trim_audio(self, y, duration_seconds):
        """Trim audio to specified duration"""
        if duration_seconds <= 0:
            return y
        
        try:
            max_samples = int(duration_seconds * self.sample_rate)
            if len(y) > max_samples:
                return y[:max_samples]
            return y
        except Exception as e:
            raise Exception(f"Failed to trim audio: {str(e)}")
    
    def normalize_volume(self, y):
        """Normalize audio volume to prevent clipping"""
        try:
            # Normalize to peak amplitude of 0.95 to prevent clipping
            max_val = np.max(np.abs(y))
            if max_val > 0:
                y = y * (0.95 / max_val)
            return y
        except Exception as e:
            raise Exception(f"Failed to normalize volume: {str(e)}")
    
    def add_light_noise(self, y, noise_level=0.001):
        """Add very light noise to break pattern detection"""
        try:
            # Generate white noise
            noise = np.random.normal(0, noise_level, len(y))
            y_with_noise = y + noise
            
            # Ensure we don't clip
            return self.normalize_volume(y_with_noise)
        except Exception as e:
            raise Exception(f"Failed to add noise: {str(e)}")
    
    def add_noise(self, y, noise_level=0.01):
        """Add light noise to audio signal"""
        try:
            # Generate white noise
            noise = np.random.normal(0, noise_level, len(y))
            
            # Add noise to signal
            y_noisy = y + noise
            
            # Ensure signal stays within valid range
            y_noisy = np.clip(y_noisy, -1.0, 1.0)
            
            return y_noisy
        except Exception as e:
            raise Exception(f"Failed to add noise: {str(e)}")
    
    def apply_highpass_filter(self, y, cutoff_freq=80):
        """Apply highpass filter to remove low frequencies"""
        try:
            # Design highpass filter
            nyquist = self.sample_rate / 2
            normalized_cutoff = cutoff_freq / nyquist
            
            # Butterworth highpass filter
            sos = signal.butter(4, normalized_cutoff, btype='high', output='sos')
            y_filtered = signal.sosfiltfilt(sos, y)
            
            return y_filtered
        except Exception as e:
            raise Exception(f"Failed to apply highpass filter: {str(e)}")
    
    def apply_compression(self, y, threshold=0.3, ratio=4.0):
        """Apply dynamic range compression"""
        try:
            # Simple compression algorithm
            y_compressed = np.copy(y)
            
            # Find samples above threshold
            above_threshold = np.abs(y_compressed) > threshold
            
            # Apply compression to samples above threshold
            sign = np.sign(y_compressed[above_threshold])
            magnitude = np.abs(y_compressed[above_threshold])
            
            # Compress the magnitude
            compressed_magnitude = threshold + (magnitude - threshold) / ratio
            y_compressed[above_threshold] = sign * compressed_magnitude
            
            return y_compressed
        except Exception as e:
            raise Exception(f"Failed to apply compression: {str(e)}")
    
    def apply_reverb(self, y, room_size=0.2, damping=0.5):
        """Apply simple reverb effect"""
        try:
            # Simple reverb using convolution with exponential decay
            reverb_length = int(0.5 * self.sample_rate)  # 0.5 seconds
            
            # Create impulse response
            t = np.arange(reverb_length) / self.sample_rate
            impulse = np.exp(-damping * t * 10) * np.random.normal(0, 0.1, reverb_length)
            impulse[0] = 1.0  # Direct signal
            
            # Apply reverb
            y_reverb = np.convolve(y, impulse * room_size, mode='same')
            
            # Mix with dry signal
            y_with_reverb = y + y_reverb
            
            return self.normalize_volume(y_with_reverb)
        except Exception as e:
            raise Exception(f"Failed to apply reverb: {str(e)}")
    
    def tempo_stretch_ffmpeg(self, input_path, output_path, playback_speed):
        """
        Apply tempo stretch using ffmpeg's atempo filter without changing pitch
        
        Args:
            input_path (str): Input file path
            output_path (str): Output file path  
            playback_speed (float): Playback speed (0.5-2.0, 1.0 = normal)
        """
        try:
            # Validate speed range
            if playback_speed <= 0:
                raise ValueError("Playback speed must be positive")
            
            # Build ffmpeg input
            input_stream = ffmpeg.input(input_path)
            
            # Handle atempo filter limitations (0.5 to 2.0 range)
            if playback_speed == 1.0:
                # No tempo change needed
                output_stream = input_stream
            elif 0.5 <= playback_speed <= 2.0:
                # Single atempo filter
                output_stream = input_stream.audio.filter('atempo', playback_speed)
            else:
                # Multiple atempo filters for extreme speeds
                current_speed = playback_speed
                output_stream = input_stream.audio
                
                while current_speed > 2.0:
                    output_stream = output_stream.filter('atempo', 2.0)
                    current_speed /= 2.0
                
                while current_speed < 0.5:
                    output_stream = output_stream.filter('atempo', 0.5)
                    current_speed /= 0.5
                
                if current_speed != 1.0:
                    output_stream = output_stream.filter('atempo', current_speed)
            
            # Output with high quality MP3
            output_stream = ffmpeg.output(
                output_stream, 
                output_path,
                acodec='libmp3lame',
                audio_bitrate='320k'
            )
            
            # Run ffmpeg
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            
        except Exception as e:
            raise Exception(f"Failed to apply tempo stretch: {str(e)}")
    
    def apply_fade_effects(self, input_path, output_path, fade_in=True, fade_out=True,
                          fade_in_duration=3.0, fade_out_duration=3.0, total_duration=None):
        """
        Apply fade in and/or fade out effects using ffmpeg (optimized for speed)
        
        Args:
            input_path (str): Input file path
            output_path (str): Output file path
            fade_in (bool): Enable fade in
            fade_out (bool): Enable fade out
            fade_in_duration (float): Fade in duration in seconds
            fade_out_duration (float): Fade out duration in seconds
            total_duration (float): Total audio duration (for fade out calculation)
        """
        try:
            # If no fade effects requested, just copy the file
            if not fade_in and not fade_out:
                import shutil
                shutil.copy2(input_path, output_path)
                return
            
            # Get duration if not provided and needed for fade out
            if fade_out and fade_out_duration > 0 and total_duration is None:
                import subprocess
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
            
            # Use optimized FFmpeg command
            cmd = ['ffmpeg', '-y', '-i', input_path]
            
            if filters:
                cmd.extend(['-af', ','.join(filters)])
            
            # Optimized encoding settings for speed
            cmd.extend(['-c:a', 'libmp3lame', '-q:a', '2'])  # VBR quality 2 (fast & good)
            cmd.append(output_path)
            
            # Run ffmpeg
            import subprocess
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"FFmpeg error: {result.stderr}")
            
        except Exception as e:
            raise Exception(f"Failed to apply fade effects: {str(e)}")
    
    def clean_metadata(self, file_path):
        """
        Remove all metadata from audio file using mutagen
        
        Args:
            file_path (str): Path to audio file
        """
        if not mutagen_available:
            # Use ffmpeg fallback if mutagen is not available
            return self._clean_metadata_ffmpeg(file_path)
            
        try:
            # Load file with mutagen
            audio_file = mutagen.File(file_path)
            
            if audio_file is not None:
                # Delete all tags
                audio_file.delete()
                # Save changes
                audio_file.save()
                return True
            else:
                # Fallback: use ffmpeg to strip metadata
                return self._clean_metadata_ffmpeg(file_path)
                
        except Exception as e:
            # Fallback to ffmpeg method
            try:
                return self._clean_metadata_ffmpeg(file_path)
            except:
                raise Exception(f"Failed to clean metadata: {str(e)}")
    
    def _clean_metadata_ffmpeg(self, file_path):
        """
        Remove metadata using ffmpeg as fallback method
        
        Args:
            file_path (str): Path to audio file
        """
        try:
            # Create temporary file
            temp_file = file_path + '_temp_clean.mp3'
            
            # Use ffmpeg to remove metadata
            input_stream = ffmpeg.input(file_path)
            output_stream = ffmpeg.output(
                input_stream,
                temp_file,
                map_metadata=-1,  # Remove all metadata
                acodec='libmp3lame',
                audio_bitrate='320k'
            )
            
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            
            # Replace original with cleaned version
            shutil.move(temp_file, file_path)
            
            return True
            
        except Exception as e:
            # Clean up temp file if it exists
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise Exception(f"Failed to clean metadata with ffmpeg: {str(e)}")
    
    def process_audio_enhanced(self, input_path, output_path=None, progress_callback=None, **options):
        """
        Enhanced audio processing with new features
        
        Args:
            input_path (str): Input file path
            output_path (str): Output file path (optional)
            progress_callback (callable): Callback for progress updates
            **options: Processing options
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
            
            update_progress(1, 8, "Initializing...")
            
            # Create temporary file for processing chain
            temp_files = []
            current_file = input_path
            
            # Store trim duration for final step
            trim_duration = options.get('trim_duration')
            
            # Step 1: Tempo stretch (if needed) - do before other processing
            tempo_stretch = options.get('tempo_stretch', 1.0)
            if tempo_stretch != 1.0:
                update_progress(2, 8, "Applying tempo stretch...")
                temp_tempo = tempfile.mktemp(suffix='.mp3')
                temp_files.append(temp_tempo)
                self.tempo_stretch_ffmpeg(current_file, temp_tempo, tempo_stretch)
                current_file = temp_tempo
            else:
                update_progress(2, 8, "Skipping tempo stretch...")
            
            # Step 2: Apply other processing (pitch, tempo change, normalize, etc.)
            if any([
                options.get('pitch_shift', 0) != 0,
                options.get('tempo_change', 1.0) != 1.0,
                options.get('normalize', False),
                options.get('add_noise', False),
                options.get('apply_highpass', False)
            ]):
                update_progress(3, 8, "Applying audio effects...")
                temp_processed = tempfile.mktemp(suffix='.mp3')
                temp_files.append(temp_processed)
                
                # Use existing process_audio method
                self._process_with_librosa(current_file, temp_processed, options)
                current_file = temp_processed
            else:
                update_progress(3, 8, "Skipping audio effects...")
            
            # Step 3: Apply fade effects
            fade_in = options.get('fade_in', False)
            fade_out = options.get('fade_out', False)
            if fade_in or fade_out:
                update_progress(4, 8, "Applying fade effects...")
                temp_fade = tempfile.mktemp(suffix='.mp3')
                temp_files.append(temp_fade)
                
                self.apply_fade_effects(
                    current_file, temp_fade,
                    fade_in=fade_in,
                    fade_out=fade_out,
                    fade_in_duration=options.get('fade_in_duration', 3.0),
                    fade_out_duration=options.get('fade_out_duration', 3.0),
                    total_duration=None  # Let function calculate actual duration
                )
                current_file = temp_fade
            else:
                update_progress(4, 8, "Skipping fade effects...")
            
            # Step 4: FINAL TRIM - Guarantee exact duration requested by user
            if trim_duration and trim_duration > 0:
                update_progress(5, 8, f"Final trim to {trim_duration}s...")
                temp_final_trim = tempfile.mktemp(suffix='.mp3')
                temp_files.append(temp_final_trim)
                
                # Use FFmpeg for final trimming to exact duration
                import subprocess
                cmd = ['ffmpeg', '-y', '-i', current_file, '-t', str(trim_duration), 
                      '-c:a', 'libmp3lame', '-q:a', '2', temp_final_trim]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    current_file = temp_final_trim
                else:
                    print(f"Warning: Final trimming failed, using previous result")
            else:
                update_progress(5, 8, "No final trimming needed...")
            
            # Step 5: Copy to final output
            update_progress(6, 8, "Copying to output...")
            if current_file != output_path:
                shutil.copy2(current_file, output_path)
            
            # Step 6: Clean metadata (if requested)
            if options.get('clean_metadata', False):
                update_progress(7, 8, "Cleaning metadata...")
                self.clean_metadata(output_path)
            else:
                update_progress(7, 8, "Skipping metadata cleaning...")
            
            # Clean up temporary files
            update_progress(8, 8, "Cleaning up temporary files...")
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass  # Ignore cleanup errors
            
            update_progress(8, 8, "Processing complete!")
            return output_path
            
        except Exception as e:
            # Clean up temporary files on error
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass
            raise Exception(f"Failed to process audio with enhanced features: {str(e)}")
    
    def _process_with_librosa(self, input_path, output_path, options):
        """Helper method for librosa-based processing"""
        # Load audio
        y, sr = self.load_audio(input_path)
        
        # Apply processing (trim is done earlier with FFmpeg)
        if options.get('pitch_shift', 0) != 0:
            y = self.change_pitch(y, options['pitch_shift'])
        
        if options.get('tempo_change', 1.0) != 1.0:
            rate = options['tempo_change'] / 100.0
            y = self.change_tempo(y, rate)
        
        if options.get('normalize', False):
            y = self.normalize_volume(y)
        
        if options.get('add_noise', False):
            y = self.add_noise(y)
        
        if options.get('apply_highpass', False):
            y = self.apply_highpass_filter(y)
        
        # Save
        self.save_audio(y, sr, output_path)
