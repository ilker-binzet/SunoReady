"""
SunoReady Real-Time Audio Preview System
Live audio processing with DLL integration for maximum performance
"""

import numpy as np
import threading
import time
from collections import deque
import queue

try:
    import pyaudio
    pyaudio_available = True
except ImportError:
    pyaudio_available = False
    print("⚠️ PyAudio not available - install for live preview: pip install pyaudio")

try:
    from audio_processor_dll import (
        apply_highpass_filter,
        apply_lowpass_filter,
        normalize_audio,
        apply_noise_reduction,
        is_dll_available
    )
    dll_available = is_dll_available()
except ImportError:
    dll_available = False

class LiveAudioPreview:
    """Real-time audio processing and preview system"""
    
    def __init__(self, sample_rate=44100, chunk_size=1024, channels=1):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.channels = channels
        
        # Audio stream objects
        self.audio = None
        self.input_stream = None
        self.output_stream = None
        
        # Processing parameters
        self.processing_enabled = False
        self.tempo_factor = 1.0
        self.highpass_enabled = False
        self.lowpass_enabled = False
        self.normalize_enabled = True
        self.noise_reduction_enabled = False
        
        # Real-time data
        self.input_buffer = deque(maxlen=100)  # Store last 100 chunks
        self.output_buffer = deque(maxlen=100)
        self.processing_queue = queue.Queue(maxsize=10)
        
        # Performance monitoring
        self.processing_times = deque(maxlen=50)
        self.dropouts = 0        
        # Thread control
        self.processing_thread = None
        self.is_running = False
        
        print(f"🎵 Live Preview initialized - DLL: {'✅' if dll_available else '❌'}")
    
    def initialize_audio(self):
        """Initialize PyAudio streams with demo fallback"""
        if not pyaudio_available:
            raise RuntimeError("PyAudio not available - cannot initialize live preview")
        
        self.audio = pyaudio.PyAudio()
        
        # Try microphone first, fallback to demo mode
        microphone_success = self._try_initialize_microphone()
        
        if not microphone_success:
            print("🎵 Microphone not available - enabling demo mode")
            self.demo_mode = True
            self._initialize_demo_mode()
        else:
            self.demo_mode = False
    
    def _try_initialize_microphone(self):
        """Try to initialize microphone input"""
          # Input stream (microphone) with error handling
        try:
            # Try different configurations for better compatibility
            configs = [
                {"device_index": None, "exclusive": False},  # Default device, non-exclusive
                {"device_index": 1, "exclusive": False},     # Camo microphone, non-exclusive
                {"device_index": 7, "exclusive": False},     # Another Camo instance
            ]
            
            for config in configs:
                try:
                    print(f"🔍 Trying microphone config: {config}")
                    self.input_stream = self.audio.open(
                        format=pyaudio.paFloat32,
                        channels=self.channels,
                        rate=self.sample_rate,
                        input=True,
                        input_device_index=config["device_index"],
                        frames_per_buffer=self.chunk_size,
                        stream_callback=self._input_callback
                    )
                    print(f"✅ Microphone opened successfully with config: {config}")
                    break
                except Exception as e:
                    print(f"⚠️ Config {config} failed: {e}")
                    continue
            
            if not self.input_stream:
                raise Exception("No microphone configuration worked")
                
        except Exception as e:
            print(f"⚠️ Could not open input stream: {e}")
            self.input_stream = None
        
        # Output stream (speakers)
        try:
            self.output_stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._output_callback
            )
        except Exception as e:
            print(f"⚠️ Could not open output stream: {e}")
            self.output_stream = None
    
    def _input_callback(self, in_data, frame_count, time_info, status):
        """Audio input callback - capture microphone data"""
        try:
            # Convert to numpy array
            audio_data = np.frombuffer(in_data, dtype=np.float32)
            
            # Store in input buffer
            self.input_buffer.append(audio_data.copy())
            
            # Queue for processing if enabled
            if self.processing_enabled:
                try:
                    self.processing_queue.put_nowait(audio_data.copy())
                except queue.Full:
                    self.dropouts += 1
                    
        except Exception as e:
            print(f"Input callback error: {e}")
        
        return (None, pyaudio.paContinue)
    
    def _output_callback(self, in_data, frame_count, time_info, status):
        """Audio output callback - play processed audio"""
        try:
            if self.output_buffer:
                # Get processed audio from buffer
                output_data = self.output_buffer.popleft()
                
                # Ensure correct size
                if len(output_data) != frame_count:
                    # Pad or truncate as needed
                    if len(output_data) < frame_count:
                        output_data = np.pad(output_data, (0, frame_count - len(output_data)))
                    else:
                        output_data = output_data[:frame_count]
                
                return (output_data.astype(np.float32).tobytes(), pyaudio.paContinue)
            else:
                # Silence if no processed data available
                silence = np.zeros(frame_count, dtype=np.float32)
                return (silence.tobytes(), pyaudio.paContinue)
                
        except Exception as e:
            print(f"Output callback error: {e}")
            silence = np.zeros(frame_count, dtype=np.float32)
            return (silence.tobytes(), pyaudio.paContinue)
    
    def _processing_worker(self):
        """Background thread for real-time audio processing"""
        while self.is_running:
            try:
                # Get audio data from queue with timeout
                audio_data = self.processing_queue.get(timeout=0.1)
                
                # Process audio with timing
                start_time = time.time()
                processed_audio = self._process_audio_chunk(audio_data)
                processing_time = time.time() - start_time
                
                # Store processing time for monitoring
                self.processing_times.append(processing_time)
                
                # Add to output buffer
                self.output_buffer.append(processed_audio)
                
                # Mark task as done
                self.processing_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Processing worker error: {e}")
                continue
    
    def _process_audio_chunk(self, audio_data):
        """Process a single chunk of audio data"""
        try:
            processed = audio_data.copy()
            
            # Apply highpass filter
            if self.highpass_enabled and dll_available:
                processed = apply_highpass_filter(processed, 80, self.sample_rate)
            elif self.highpass_enabled:
                # Fallback: simple highpass
                processed = self._simple_highpass(processed)
            
            # Apply lowpass filter
            if self.lowpass_enabled and dll_available:
                processed = apply_lowpass_filter(processed, 8000, self.sample_rate)
            elif self.lowpass_enabled:
                # Fallback: simple lowpass
                processed = self._simple_lowpass(processed)
            
            # Apply noise reduction
            if self.noise_reduction_enabled and dll_available:
                processed = apply_noise_reduction(processed, 0.01, 0.5)
            elif self.noise_reduction_enabled:
                # Fallback: simple noise gate
                processed = self._simple_noise_gate(processed)
            
            # Normalize volume
            if self.normalize_enabled and dll_available:
                processed = normalize_audio(processed, 0.8)
            elif self.normalize_enabled:
                # Fallback: simple normalization
                processed = self._simple_normalize(processed)
            
            # Apply tempo change (simple time stretching)
            if abs(self.tempo_factor - 1.0) > 0.01:
                processed = self._simple_tempo_change(processed, self.tempo_factor)
            
            return processed
            
        except Exception as e:
            print(f"Audio processing error: {e}")
            return audio_data  # Return original on error
    
    def _simple_highpass(self, audio_data):
        """Simple highpass filter fallback"""
        # Very basic first-order highpass
        alpha = 0.95
        filtered = np.zeros_like(audio_data)
        filtered[0] = audio_data[0]
        for i in range(1, len(audio_data)):
            filtered[i] = alpha * (filtered[i-1] + audio_data[i] - audio_data[i-1])
        return filtered
    
    def _simple_lowpass(self, audio_data):
        """Simple lowpass filter fallback"""
        # Basic moving average
        window_size = 3
        return np.convolve(audio_data, np.ones(window_size)/window_size, mode='same')
    
    def _simple_noise_gate(self, audio_data):
        """Simple noise gate fallback"""
        threshold = 0.01
        return np.where(np.abs(audio_data) < threshold, audio_data * 0.1, audio_data)
    
    def _simple_normalize(self, audio_data):
        """Simple normalization fallback"""
        peak = np.max(np.abs(audio_data))
        if peak > 0:
            return audio_data * (0.8 / peak)
        return audio_data
    
    def _simple_tempo_change(self, audio_data, factor):
        """Simple tempo change using linear interpolation"""
        if factor == 1.0:
            return audio_data
        
        original_length = len(audio_data)
        new_length = int(original_length / factor)        
        # Linear interpolation for resampling
        old_indices = np.linspace(0, original_length - 1, new_length)
        return np.interp(old_indices, np.arange(original_length), audio_data)
    
    def start_live_preview(self):
        """Start live audio preview with fallback to demo"""
        if not pyaudio_available:
            raise RuntimeError("PyAudio not available")
        
        print("🎤 Starting live audio preview...")
        
        # Try to initialize microphone
        try:
            self.initialize_audio()
            
            # If microphone failed, use demo mode
            if not self.input_stream:
                print("🎵 Switching to demo mode - generating test audio")
                return self._start_demo_mode()
            
            # Normal microphone mode
            self.is_running = True
            self.processing_thread = threading.Thread(target=self._processing_worker)
            self.processing_thread.daemon = True
            self.processing_thread.start()
            
            if self.input_stream:
                self.input_stream.start_stream()
            if self.output_stream:
                self.output_stream.start_stream()
            
            print("✅ Live preview started!")
            print("🎛️ Use set_* methods to change processing parameters")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start live preview: {e}")
            return False
    
    def _start_demo_mode(self):
        """Start demo mode with generated audio"""
        try:
            # Import and use demo class
            from live_audio_preview_demo import LiveAudioPreviewDemo
            self.demo_instance = LiveAudioPreviewDemo()
            return self.demo_instance.start_live_preview()
        except Exception as e:
            print(f"❌ Demo mode failed: {e}")
            return False
    
    def stop_live_preview(self):
        """Stop live audio preview"""
        print("🛑 Stopping live preview...")
        
        # Stop processing thread
        self.is_running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=1.0)
        
        # Stop and close audio streams
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
        
        # Terminate PyAudio
        if self.audio:
            self.audio.terminate()
        
        print("✅ Live preview stopped")
    
    def set_processing_enabled(self, enabled):
        """Enable or disable real-time processing"""
        self.processing_enabled = enabled
        print(f"🎛️ Real-time processing: {'ON' if enabled else 'OFF'}")
    
    def set_tempo(self, factor):
        """Set tempo factor (1.0 = normal, 2.0 = double speed, 0.5 = half speed)"""
        self.tempo_factor = max(0.25, min(4.0, factor))
        print(f"🎵 Tempo factor: {self.tempo_factor:.2f}x")
    
    def set_highpass(self, enabled):
        """Enable/disable highpass filter"""
        self.highpass_enabled = enabled
        print(f"🔊 Highpass filter: {'ON' if enabled else 'OFF'}")
    
    def set_lowpass(self, enabled):
        """Enable/disable lowpass filter"""
        self.lowpass_enabled = enabled
        print(f"🔉 Lowpass filter: {'ON' if enabled else 'OFF'}")
    
    def set_normalize(self, enabled):
        """Enable/disable normalization"""
        self.normalize_enabled = enabled
        print(f"📊 Normalization: {'ON' if enabled else 'OFF'}")
    
    def set_noise_reduction(self, enabled):
        """Enable/disable noise reduction"""
        self.noise_reduction_enabled = enabled
        print(f"🔇 Noise reduction: {'ON' if enabled else 'OFF'}")
    
    def get_performance_stats(self):
        """Get real-time performance statistics"""
        if not self.processing_times:
            return {}
        
        avg_time = np.mean(self.processing_times) * 1000  # Convert to ms
        max_time = np.max(self.processing_times) * 1000
        real_time_factor = avg_time / (self.chunk_size / self.sample_rate * 1000)
        
        return {
            "avg_processing_time_ms": avg_time,
            "max_processing_time_ms": max_time,
            "real_time_factor": real_time_factor,
            "dropouts": self.dropouts,
            "dll_available": dll_available,
            "buffer_size": len(self.output_buffer)
        }
    
    def print_performance_stats(self):
        """Print current performance statistics"""
        stats = self.get_performance_stats()
        if stats:
            print("\n📊 Live Preview Performance:")
            print(f"   Average processing: {stats['avg_processing_time_ms']:.1f} ms")
            print(f"   Real-time factor: {stats['real_time_factor']:.2f}x")
            print(f"   Dropouts: {stats['dropouts']}")
            print(f"   DLL acceleration: {'✅' if stats['dll_available'] else '❌'}")

# Example usage and demo
def demo_live_preview():
    """Demo function for live audio preview"""
    preview = LiveAudioPreview()
    
    if not pyaudio_available:
        print("❌ PyAudio not available - cannot run live preview demo")
        print("💡 Install with: pip install pyaudio")
        return
    
    try:
        # Start live preview
        preview.start_live_preview()
        
        print("\n🎛️ Live Preview Demo - Commands:")
        print("  'p' - Toggle processing on/off")
        print("  't' - Change tempo")
        print("  'h' - Toggle highpass filter")
        print("  'l' - Toggle lowpass filter")
        print("  'n' - Toggle normalization")
        print("  'r' - Toggle noise reduction")
        print("  's' - Show performance stats")
        print("  'q' - Quit")
        print("\n🎤 Speak into your microphone to test...")
        
        # Interactive control loop
        preview.set_processing_enabled(True)
        
        while True:
            try:
                cmd = input("\nEnter command: ").lower().strip()
                
                if cmd == 'q':
                    break
                elif cmd == 'p':
                    preview.set_processing_enabled(not preview.processing_enabled)
                elif cmd == 't':
                    factor = float(input("Enter tempo factor (0.5-2.0): "))
                    preview.set_tempo(factor)
                elif cmd == 'h':
                    preview.set_highpass(not preview.highpass_enabled)
                elif cmd == 'l':
                    preview.set_lowpass(not preview.lowpass_enabled)
                elif cmd == 'n':
                    preview.set_normalize(not preview.normalize_enabled)
                elif cmd == 'r':
                    preview.set_noise_reduction(not preview.noise_reduction_enabled)
                elif cmd == 's':
                    preview.print_performance_stats()
                else:
                    print("❓ Unknown command")
                    
            except KeyboardInterrupt:
                break
            except ValueError:
                print("❌ Invalid input")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    finally:
        preview.stop_live_preview()

if __name__ == "__main__":
    demo_live_preview()
