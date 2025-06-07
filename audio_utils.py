"""
Audio processing utilities for SunoReady
Handles pitch shifting, tempo changes, trimming, normalization, and effects
"""

import librosa
import soundfile as sf
import numpy as np
from scipy import signal
import os
import subprocess
from pathlib import Path

class AudioProcessor:
    def __init__(self):
        self.sample_rate = 44100
        
    def load_audio(self, file_path):
        """Load audio file using librosa"""
        try:
            # Load audio file
            y, sr = librosa.load(file_path, sr=self.sample_rate)
            return y, sr
        except Exception as e:
            raise Exception(f"Failed to load audio file {file_path}: {str(e)}")
    
    def save_audio(self, y, sr, output_path):
        """Save audio file using soundfile"""
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
        
        try:
            # Use librosa's pitch shift
            y_shifted = librosa.effects.pitch_shift(y, sr=self.sample_rate, n_steps=n_steps)
            return y_shifted
        except Exception as e:
            raise Exception(f"Failed to change pitch: {str(e)}")
    
    def change_tempo(self, y, rate):
        """Change tempo by rate (1.0 = no change, 1.2 = 20% faster)"""
        if rate == 1.0:
            return y
        
        try:
            # Use librosa's time stretch
            y_stretched = librosa.effects.time_stretch(y, rate=rate)
            return y_stretched
        except Exception as e:
            raise Exception(f"Failed to change tempo: {str(e)}")
    
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
    
    def apply_highpass_filter(self, y, cutoff_freq=80):
        """Apply highpass filter to remove low frequencies"""
        try:
            # Design highpass filter
            nyquist = self.sample_rate / 2
            normalized_cutoff = cutoff_freq / nyquist
            
            # Butterworth highpass filter
            b, a = signal.butter(4, normalized_cutoff, btype='high')
            y_filtered = signal.filtfilt(b, a, y)
            
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
    
    def process_audio(self, input_path, pitch_shift=0, tempo_change=1.0, 
                     trim_duration=None, normalize=True, add_noise=False, 
                     apply_highpass=False, apply_compression=False, 
                     apply_reverb=False):
        """
        Process audio file with specified parameters
        
        Args:
            input_path (str): Path to input audio file
            pitch_shift (float): Pitch shift in semitones
            tempo_change (float): Tempo change ratio (1.0 = no change)
            trim_duration (float): Duration to trim to in seconds
            normalize (bool): Whether to normalize volume
            add_noise (bool): Whether to add light noise
            apply_highpass (bool): Whether to apply highpass filter
            apply_compression (bool): Whether to apply compression
            apply_reverb (bool): Whether to apply reverb
            
        Returns:
            str: Path to output file
        """
        try:
            # Load audio
            y, sr = self.load_audio(input_path)
            
            # Apply pitch shift
            if pitch_shift != 0:
                y = self.change_pitch(y, pitch_shift)
            
            # Apply tempo change
            if tempo_change != 1.0:
                y = self.change_tempo(y, tempo_change)
            
            # Trim audio
            if trim_duration and trim_duration > 0:
                y = self.trim_audio(y, trim_duration)
            
            # Apply highpass filter
            if apply_highpass:
                y = self.apply_highpass_filter(y)
            
            # Apply compression
            if apply_compression:
                y = self.apply_compression(y)
            
            # Apply reverb
            if apply_reverb:
                y = self.apply_reverb(y)
            
            # Add light noise
            if add_noise:
                y = self.add_light_noise(y)
            
            # Normalize volume
            if normalize:
                y = self.normalize_volume(y)
            
            # Generate output filename
            input_name = Path(input_path).stem
            output_path = f"output/{input_name}_processed.mp3"
            
            # Save processed audio
            self.save_audio(y, sr, output_path)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Failed to process audio: {str(e)}")
