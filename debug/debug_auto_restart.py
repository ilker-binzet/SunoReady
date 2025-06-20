"""
Minimal test to find the issue
"""
import time
import sys

# Add debug print to demo class
print("🔍 Creating demo instance...")

from live_audio_preview_demo import LiveAudioPreviewDemo
demo = LiveAudioPreviewDemo()

print("🔍 Starting demo...")
result = demo.start_live_preview()
print(f"Result: {result}")

# Wait and see if it restarts itself
print("🔍 Waiting 5 seconds to see if it restarts...")
time.sleep(5)

print("🔍 Stopping demo...")
demo.stop_live_preview()

print("✅ Test completed - no auto restart should happen")
