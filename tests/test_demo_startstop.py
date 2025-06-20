"""
Quick test of demo mode start/stop
"""
from live_audio_preview_demo import LiveAudioPreviewDemo
import time

print("🧪 Testing demo mode start/stop...")

demo = LiveAudioPreviewDemo()

print("Starting...")
result1 = demo.start_live_preview()
print(f"First start result: {result1}")

time.sleep(1)

print("Starting again (should be ignored)...")
result2 = demo.start_live_preview()
print(f"Second start result: {result2}")

time.sleep(1)

print("Stopping...")
demo.stop_live_preview()

print("Starting after stop...")
result3 = demo.start_live_preview()
print(f"Third start result: {result3}")

time.sleep(1)

print("Final stop...")
demo.stop_live_preview()

print("✅ Test completed!")
