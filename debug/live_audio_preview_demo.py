"""
Demo mode for live audio preview when microphone is not available
Generates test audio and applies effects for demonstration
"""
import numpy as np
import threading
import time
import queue
import math

try:
    import pyaudio
    pyaudio_available = True
except ImportError:
    pyaudio_available = False

class LiveAudioPreviewDemo:
    """Demo version of live audio preview using generated test signals"""
    
    def __init__(self, sample_rate=44100, chunk_size=1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        
        # Audio stream
        self.audio = None
        self.output_stream = None
        
        # Processing parameters
        self.processing_enabled = True
        self.tempo_factor = 1.0
        self.highpass_enabled = False
        self.normalize_enabled = True
        self.noise_reduction_enabled = False
        
        # Demo state
        self.is_running = False
        self.processing_thread = None
        self.output_buffer = queue.Queue(maxsize=50)
        
        # Test signal generation
        self.test_frequency = 440.0  # A4 note
        self.phase = 0
        
        print("🎵 Live Preview Demo Mode - DLL:", "✅" if self._check_dll() else "❌")
    
    def _check_dll(self):
        """Check if DLL is available"""
        try:
            from audio_processor_dll import is_dll_available
            return is_dll_available()
        except:
            return False
    
    def initialize_audio(self):
        """Initialize audio system for demo"""
        if not pyaudio_available:
            return False
            
        self.audio = pyaudio.PyAudio()
        
        # Only output stream for demo
        try:
            self.output_stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._output_callback
            )
            return True
        except Exception as e:
            print(f"⚠️ Could not open output stream: {e}")
            return False
    
    def _generate_test_signal(self, frame_count):
        """Generate test audio signal"""
        # Generate sine wave with some harmonics for richer sound
        t = np.arange(frame_count) / self.sample_rate
        
        # Base frequency
        signal = 0.3 * np.sin(2 * np.pi * self.test_frequency * t + self.phase)
        
        # Add some harmonics
        signal += 0.1 * np.sin(2 * np.pi * self.test_frequency * 2 * t + self.phase)
        signal += 0.05 * np.sin(2 * np.pi * self.test_frequency * 3 * t + self.phase)
        
        # Add some noise for realistic effect
        signal += 0.02 * np.random.randn(frame_count)
        
        # Update phase
        self.phase += 2 * np.pi * self.test_frequency * frame_count / self.sample_rate
        self.phase = self.phase % (2 * np.pi)
        
        return signal.astype(np.float32)
    
    def _apply_effects(self, audio_data):
        """Apply audio effects to demo signal"""
        if not self.processing_enabled:
            return audio_data
        
        processed = audio_data.copy()
        
        try:
            # Apply tempo change (simple pitch shifting for demo)
            if self.tempo_factor != 1.0:
                # Simple resampling effect for demo
                processed = processed * (1.0 + (self.tempo_factor - 1.0) * 0.5)
            
            # Apply highpass filter
            if self.highpass_enabled:
                # Simple high-pass effect
                processed = processed - np.mean(processed)
                processed *= 1.2
            
            # Apply normalization
            if self.normalize_enabled:
                max_val = np.max(np.abs(processed))
                if max_val > 0:
                    processed = processed / max_val * 0.8
            
            # Apply noise reduction (simple)
            if self.noise_reduction_enabled:
                # Simple noise gate
                threshold = 0.1
                processed = np.where(np.abs(processed) > threshold, processed, processed * 0.3)
        
        except Exception as e:
            print(f"Effect processing error: {e}")
            return audio_data
        
        return processed
    
    def _output_callback(self, in_data, frame_count, time_info, status):
        """Audio output callback"""
        try:
            if not self.output_buffer.empty():
                output_data = self.output_buffer.get_nowait()
            else:
                # Generate silence if buffer is empty
                output_data = np.zeros(frame_count, dtype=np.float32)
            
            return (output_data.tobytes(), pyaudio.paContinue)
        except:
            return (np.zeros(frame_count, dtype=np.float32).tobytes(), pyaudio.paContinue)
    
    def _processing_worker(self):
        """Main processing thread for demo"""
        while self.is_running:
            try:
                # Generate test signal
                test_audio = self._generate_test_signal(self.chunk_size)
                
                # Apply effects
                processed_audio = self._apply_effects(test_audio)
                
                # Add to output buffer
                try:
                    self.output_buffer.put_nowait(processed_audio)
                except queue.Full:
                    # Skip if buffer is full
                    pass
                
                # Control generation rate                time.sleep(self.chunk_size / self.sample_rate * 0.8)                
            except Exception as e:
                print(f"Processing worker error: {e}")
                time.sleep(0.1)
    
    def start_live_preview(self):
        """Start demo live preview"""
        if self.is_running:
            print("⚠️ Demo live preview already running")
            return True
            
        print("🎵 Starting demo live preview...")
        
        audio_result = self.initialize_audio()
        print(f"🔍 DEBUG: initialize_audio result: {audio_result}")
        if not audio_result:
            print("❌ Could not initialize audio for demo")
            return False
        
        # Start processing thread
        self.is_running = True
        self.processing_thread = threading.Thread(target=self._processing_worker)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        # Start output stream
        if self.output_stream:
            self.output_stream.start_stream()
        
        print("✅ Demo live preview started!")
        print("🎛️ Use set_* methods to change effects")
        print("🎵 Playing test tone with real-time effects")
        return True
    
    def stop_live_preview(self):
        """Stop demo live preview"""
        print("🛑 Stopping demo preview...")
        
        self.is_running = False
        
        if self.processing_thread:
            self.processing_thread.join(timeout=1.0)
        
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
        
        if self.audio:
            self.audio.terminate()
        
        print("✅ Demo preview stopped")
    
    # Effect control methods (same interface as main class)
    def set_processing_enabled(self, enabled):
        self.processing_enabled = enabled
        print(f"🎛️ Demo processing: {'ON' if enabled else 'OFF'}")
    
    def set_tempo(self, factor):
        self.tempo_factor = factor
        # Change test frequency based on tempo for demo
        self.test_frequency = 440.0 * factor
        print(f"🎵 Demo tempo factor: {factor:.2f}x")
    
    def set_highpass_enabled(self, enabled):
        self.highpass_enabled = enabled
        print(f"🔊 Demo highpass filter: {'ON' if enabled else 'OFF'}")
    
    def set_normalize_enabled(self, enabled):
        self.normalize_enabled = enabled
        print(f"📊 Demo normalization: {'ON' if enabled else 'OFF'}")
    
    def set_noise_reduction_enabled(self, enabled):
        self.noise_reduction_enabled = enabled
        print(f"🔇 Demo noise reduction: {'ON' if enabled else 'OFF'}")
    
    def get_stats(self):
        """Get demo performance stats"""
        return {
            'cpu_usage': 5.0,  # Simulated
            'latency_ms': 23.0,  # Simulated
            'dropouts': 0,
            'buffer_size': self.output_buffer.qsize(),
            'demo_mode': True
        }

# Test the demo
if __name__ == "__main__":
    demo = LiveAudioPreviewDemo()
    if demo.start_live_preview():
        print("Demo running... Press Ctrl+C to stop")
        try:
            time.sleep(3)
            demo.set_tempo(1.5)
            time.sleep(2)
            demo.set_highpass_enabled(True)
            time.sleep(2)
            demo.set_processing_enabled(False)
            time.sleep(2)
        except KeyboardInterrupt:
            pass
        finally:
            demo.stop_live_preview()
