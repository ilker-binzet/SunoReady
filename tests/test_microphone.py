"""
Simple PyAudio test to debug microphone issues
"""
import pyaudio
import numpy as np
import time

def test_microphone():
    print("🎤 Testing microphone access...")
    
    p = pyaudio.PyAudio()
    
    try:
        # Test 1: Simple blocking read
        print("Test 1: Blocking mode")
        stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024
        )
        
        print("✅ Microphone opened successfully!")
        
        # Read a few frames
        for i in range(5):
            data = stream.read(1024)
            audio_data = np.frombuffer(data, dtype=np.float32)
            level = np.max(np.abs(audio_data))
            print(f"Frame {i+1}: Level = {level:.4f}")
            time.sleep(0.1)
            
        stream.stop_stream()
        stream.close()
        print("✅ Blocking test successful!")
        
        # Test 2: Callback mode
        print("\nTest 2: Callback mode")
        
        def callback(in_data, frame_count, time_info, status):
            audio_data = np.frombuffer(in_data, dtype=np.float32)
            level = np.max(np.abs(audio_data))
            print(f"Callback: Level = {level:.4f}")
            return (in_data, pyaudio.paContinue)
        
        stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024,
            stream_callback=callback
        )
        
        stream.start_stream()
        print("✅ Callback mode started!")
        time.sleep(2)
        stream.stop_stream()
        stream.close()
        print("✅ Callback test successful!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    finally:
        p.terminate()

if __name__ == "__main__":
    test_microphone()
