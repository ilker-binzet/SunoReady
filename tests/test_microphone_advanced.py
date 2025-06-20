"""
Advanced PyAudio microphone test with different APIs
"""
import pyaudio
import numpy as np

def test_different_apis():
    print("🎤 Testing different audio APIs...")
    
    p = pyaudio.PyAudio()
    
    # Get host API info
    print(f"Host API count: {p.get_host_api_count()}")
    for i in range(p.get_host_api_count()):
        api_info = p.get_host_api_info_by_index(i)
        print(f"API {i}: {api_info['name']}")
    
    # Test different configurations
    configs = [
        {"api": None, "device": None, "name": "Default"},
        {"api": None, "device": 0, "name": "Sound Mapper"},
        {"api": None, "device": 1, "name": "Camo Microphone"},
        {"api": None, "device": 6, "name": "Primary Capture"},
        {"api": None, "device": 7, "name": "Camo Alternative"},
    ]
    
    for config in configs:
        try:
            print(f"\n🔍 Testing {config['name']}...")
            
            stream_params = {
                'format': pyaudio.paInt16,  # Try different format
                'channels': 1,
                'rate': 44100,
                'input': True,
                'frames_per_buffer': 2048,  # Larger buffer
            }
            
            if config['device'] is not None:
                stream_params['input_device_index'] = config['device']
            
            stream = p.open(**stream_params)
            
            # Try to read one frame
            data = stream.read(1024, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            level = np.max(np.abs(audio_data))
            
            print(f"✅ {config['name']} works! Level: {level}")
            
            stream.stop_stream()
            stream.close()
            
            return config  # Return first working config
            
        except Exception as e:
            print(f"❌ {config['name']} failed: {e}")
    
    p.terminate()
    return None

if __name__ == "__main__":
    working_config = test_different_apis()
    if working_config:
        print(f"\n🎉 Found working configuration: {working_config}")
    else:
        print("\n😞 No working microphone configuration found")
