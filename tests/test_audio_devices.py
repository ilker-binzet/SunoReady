import pyaudio

def list_audio_devices():
    p = pyaudio.PyAudio()
    print("🎤 Ses Cihazları:")
    print("=" * 50)
    
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        print(f"{i}: {info['name']}")
        print(f"   Max Channels: {info['maxInputChannels']} in, {info['maxOutputChannels']} out")
        print(f"   Sample Rate: {info['defaultSampleRate']}")
        print()
    
    # Test default input device
    try:
        default_input = p.get_default_input_device_info()
        print(f"✅ Default Input: {default_input['name']}")
    except:
        print("❌ No default input device!")
    
    p.terminate()

if __name__ == "__main__":
    list_audio_devices()
