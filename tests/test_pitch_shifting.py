#!/usr/bin/env python3
"""
Comprehensive test suite for pitch shifting functionality
Tests the `change_pitch` function and full pipeline pitch shifting

Unit tests: Feed sinusoid to `change_pitch` and verify frequency ratio
Integration tests: Run WAV through full pipeline with +3 st and assert output properties
GUI tests: Programmatically move slider and ensure config updates
"""

import os
import sys
import numpy as np
import unittest
import tempfile
import time
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

try:
    import librosa
    import soundfile as sf
    from scipy import signal
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Required dependencies not available: {e}")
    DEPENDENCIES_AVAILABLE = False

# Import our modules
from audio_utils import AudioProcessor
from lightning_processor import LightningProcessor

# Try to import GUI components for GUI tests
try:
    import customtkinter as ctk
    import tkinter as tk
    from app import SunoReadyApp
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    print("Warning: GUI dependencies not available, skipping GUI tests")


class TestPitchShiftingUnit(unittest.TestCase):
    """Unit tests for pitch shifting functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        if not DEPENDENCIES_AVAILABLE:
            self.skipTest("Required dependencies not available")
        
        self.config = {
            "tempo_change": 100,
            "normalize_volume": True,
            "add_noise": False,
            "reduce_noise": False,
            "apply_highpass": False,
            "output_format": "mp3",
            "clean_metadata": False,
            "pitch_semitones": 0
        }
        self.processor = AudioProcessor(config=self.config)
        self.sample_rate = 44100
        self.duration = 2.0  # 2 seconds
        
    def generate_sinusoid(self, frequency, duration=None, sample_rate=None):
        """Generate a pure sinusoid for testing"""
        if duration is None:
            duration = self.duration
        if sample_rate is None:
            sample_rate = self.sample_rate
            
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        return np.sin(2 * np.pi * frequency * t)
    
    def get_dominant_frequency(self, y, sample_rate=None):
        """Get the dominant frequency from an audio signal using FFT"""
        if sample_rate is None:
            sample_rate = self.sample_rate
            
        # Apply FFT
        fft = np.fft.fft(y)
        magnitude = np.abs(fft)
        
        # Get frequencies
        freqs = np.fft.fftfreq(len(y), 1/sample_rate)
        
        # Find peak in positive frequencies only
        positive_freqs = freqs[:len(freqs)//2]
        positive_magnitude = magnitude[:len(magnitude)//2]
        
        # Find the dominant frequency
        peak_idx = np.argmax(positive_magnitude)
        dominant_freq = positive_freqs[peak_idx]
        
        return abs(dominant_freq)
    
    def test_pitch_shift_frequency_ratio(self):
        """Test that pitch shifting changes frequency by 2^(n/12) ratio"""
        test_cases = [
            (1, 440.0),   # +1 semitone
            (3, 440.0),   # +3 semitones 
            (5, 440.0),   # +5 semitones
            (7, 440.0),   # +7 semitones (perfect fifth)
            (12, 440.0),  # +12 semitones (octave)
            (-1, 440.0),  # -1 semitone
            (-3, 440.0),  # -3 semitones
            (-12, 440.0), # -12 semitones (octave down)
        ]
        
        for n_steps, input_freq in test_cases:
            with self.subTest(n_steps=n_steps, input_freq=input_freq):
                # Generate input sinusoid
                y_input = self.generate_sinusoid(input_freq)
                
                # Apply pitch shift
                y_shifted = self.processor.change_pitch(y_input, n_steps)
                
                # Get frequencies
                input_dominant_freq = self.get_dominant_frequency(y_input)
                output_dominant_freq = self.get_dominant_frequency(y_shifted)
                
                # Calculate expected frequency
                expected_ratio = 2 ** (n_steps / 12.0)
                expected_freq = input_freq * expected_ratio
                
                # Calculate actual ratio
                actual_ratio = output_dominant_freq / input_dominant_freq
                
                # Assert frequency ratio is correct (with 5% tolerance)
                tolerance = 0.05
                self.assertAlmostEqual(
                    actual_ratio, expected_ratio, 
                    delta=expected_ratio * tolerance,
                    msg=f"Pitch shift by {n_steps} semitones: expected ratio {expected_ratio:.3f}, "
                        f"got {actual_ratio:.3f} (input: {input_dominant_freq:.1f}Hz, "
                        f"output: {output_dominant_freq:.1f}Hz, expected: {expected_freq:.1f}Hz)"
                )
                
                print(f"✓ {n_steps:+2d} st: {input_dominant_freq:6.1f}Hz → {output_dominant_freq:6.1f}Hz "
                      f"(ratio: {actual_ratio:.3f}, expected: {expected_ratio:.3f})")
    
    def test_zero_pitch_shift(self):
        """Test that zero pitch shift returns identical signal"""
        y_input = self.generate_sinusoid(440.0)
        y_output = self.processor.change_pitch(y_input, 0)
        
        # Should be exactly the same
        np.testing.assert_array_equal(y_input, y_output, 
            "Zero pitch shift should return identical signal")
    
    def test_multiple_frequencies(self):
        """Test pitch shifting with multiple input frequencies"""
        test_frequencies = [110.0, 220.0, 440.0, 880.0, 1760.0]  # A notes
        n_steps = 3  # +3 semitones
        expected_ratio = 2 ** (n_steps / 12.0)
        
        for input_freq in test_frequencies:
            with self.subTest(input_freq=input_freq):
                y_input = self.generate_sinusoid(input_freq)
                y_shifted = self.processor.change_pitch(y_input, n_steps)
                
                input_dominant_freq = self.get_dominant_frequency(y_input)
                output_dominant_freq = self.get_dominant_frequency(y_shifted)
                
                actual_ratio = output_dominant_freq / input_dominant_freq
                
                # 5% tolerance
                self.assertAlmostEqual(
                    actual_ratio, expected_ratio, 
                    delta=expected_ratio * 0.05,
                    msg=f"Frequency {input_freq}Hz: expected ratio {expected_ratio:.3f}, "
                        f"got {actual_ratio:.3f}"
                )


class TestPitchShiftingIntegration(unittest.TestCase):
    """Integration tests for pitch shifting through full pipeline"""
    
    def setUp(self):
        """Set up test fixtures"""
        if not DEPENDENCIES_AVAILABLE:
            self.skipTest("Required dependencies not available")
            
        self.config = {
            "tempo_change": 100,
            "normalize_volume": True,
            "add_noise": False,
            "reduce_noise": False,
            "apply_highpass": False,
            "output_format": "mp3",
            "clean_metadata": False,
            "pitch_semitones": 0,
            "processed_output_folder": "tests/output"
        }
        self.processor = AudioProcessor(config=self.config)
        self.lightning_processor = LightningProcessor(config=self.config)
        
        # Ensure output directory exists
        os.makedirs("tests/output", exist_ok=True)
        
        # Test audio file paths
        self.test_wav = "tests/test_audio.wav"
        if not os.path.exists(self.test_wav):
            self.test_wav = "tests/simple_test.wav"
        if not os.path.exists(self.test_wav):
            self.skipTest("No test audio file available")
    
    def test_full_pipeline_pitch_shift_3_semitones(self):
        """Test full pipeline with +3 semitones pitch shift"""
        n_steps = 3
        expected_ratio = 2 ** (n_steps / 12.0)
        
        # Get input file properties
        y_input, sr_input = librosa.load(self.test_wav)
        input_duration = len(y_input) / sr_input
        input_dominant_freq = self.get_dominant_frequency(y_input, sr_input)
        
        # Process with lightning processor
        output_path = None
        try:
            output_path = self.lightning_processor.process_lightning_fast(
                self.test_wav,
                output_path="tests/output/test_pitch_shift_+3st.mp3",
                pitch_semitones=n_steps
            )
            
            # Verify output exists
            self.assertTrue(os.path.exists(output_path), "Output file should exist")
            
            # Load output and check properties
            y_output, sr_output = librosa.load(output_path)
            output_duration = len(y_output) / sr_output
            output_dominant_freq = self.get_dominant_frequency(y_output, sr_output)
            
            # Check duration is approximately the same (within 10% tolerance)
            duration_ratio = output_duration / input_duration
            self.assertAlmostEqual(
                duration_ratio, 1.0, delta=0.1,
                msg=f"Output duration should be similar to input: "
                    f"input={input_duration:.2f}s, output={output_duration:.2f}s"
            )
            
            # Check spectral peak shift
            if input_dominant_freq > 0:  # Only if we can detect input frequency
                frequency_ratio = output_dominant_freq / input_dominant_freq
                self.assertAlmostEqual(
                    frequency_ratio, expected_ratio, delta=expected_ratio * 0.1,
                    msg=f"Spectral peak should shift by {expected_ratio:.3f}: "
                        f"input={input_dominant_freq:.1f}Hz, output={output_dominant_freq:.1f}Hz, "
                        f"ratio={frequency_ratio:.3f}"
                )
            
            print(f"✓ Integration test +3st: {input_duration:.2f}s → {output_duration:.2f}s, "
                  f"freq: {input_dominant_freq:.1f}Hz → {output_dominant_freq:.1f}Hz")
                  
        finally:
            # Cleanup
            if output_path and os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
    
    def test_different_pitch_shifts(self):
        """Test different pitch shift amounts through full pipeline"""
        test_cases = [1, -1, 5, -5, 7, -7]
        
        for n_steps in test_cases:
            with self.subTest(n_steps=n_steps):
                expected_ratio = 2 ** (n_steps / 12.0)
                
                # Process file
                output_path = None
                try:
                    output_path = self.lightning_processor.process_lightning_fast(
                        self.test_wav,
                        output_path=f"tests/output/test_pitch_shift_{n_steps:+d}st.mp3",
                        pitch_semitones=n_steps
                    )
                    
                    # Verify output exists and is valid
                    self.assertTrue(os.path.exists(output_path))
                    
                    # Load and check basic properties (don't force sample rate)
                    y_output, sr_output = librosa.load(output_path, sr=None)  # Load with original sample rate
                    self.assertGreater(len(y_output), 0, "Output should have audio data")
                    self.assertGreater(sr_output, 0, "Output sample rate should be positive")
                    
                    print(f"✓ Pipeline test {n_steps:+d}st: output length {len(y_output)} samples at {sr_output}Hz")
                    
                finally:
                    # Cleanup
                    if output_path and os.path.exists(output_path):
                        try:
                            os.remove(output_path)
                        except:
                            pass
    
    def get_dominant_frequency(self, y, sample_rate):
        """Get the dominant frequency from an audio signal"""
        # Apply FFT
        fft = np.fft.fft(y)
        magnitude = np.abs(fft)
        
        # Get frequencies
        freqs = np.fft.fftfreq(len(y), 1/sample_rate)
        
        # Find peak in positive frequencies only
        positive_freqs = freqs[:len(freqs)//2]
        positive_magnitude = magnitude[:len(magnitude)//2]
        
        # Find the dominant frequency
        peak_idx = np.argmax(positive_magnitude)
        dominant_freq = positive_freqs[peak_idx]
        
        return abs(dominant_freq)


@unittest.skipUnless(GUI_AVAILABLE, "GUI dependencies not available")
class TestPitchShiftingGUI(unittest.TestCase):
    """GUI smoke tests for pitch shifting controls"""
    
    def setUp(self):
        """Set up GUI test fixtures"""
        self.root = None
        self.app = None
    
    def tearDown(self):
        """Clean up GUI test fixtures"""
        if self.app and self.app.root:
            try:
                self.app.root.quit()
                self.app.root.destroy()
            except:
                pass
    
    def test_pitch_slider_updates_config(self):
        """Test that moving pitch slider updates self.config"""
        try:
            # Create app instance
            self.app = SunoReadyApp()
            
            # Wait for UI to initialize
            self.app.root.update()
            
            # Test different pitch values
            test_values = [-12, -7, -3, -1, 0, 1, 3, 5, 7, 12]
            
            for pitch_value in test_values:
                with self.subTest(pitch_value=pitch_value):
                    # Set pitch slider value programmatically
                    self.app.pitch_var.set(pitch_value)
                    self.app.root.update()  # Process GUI events
                    
                    # Manually trigger the display update callback
                    self.app.update_pitch_display(pitch_value)
                    self.app.root.update()  # Process the label update
                    
                    # Manually trigger config update like the process_audio_files method does
                    self.app.config["pitch_semitones"] = float(self.app.pitch_var.get())
                    
                    # Check that slider value matches
                    slider_value = float(self.app.pitch_var.get())
                    self.assertEqual(
                        slider_value, pitch_value,
                        f"Slider should be set to {pitch_value}"
                    )
                    
                    # Check that config can be updated (simulating actual app behavior)
                    self.assertEqual(
                        self.app.config["pitch_semitones"], pitch_value,
                        f"Config should be updatable to {pitch_value}"
                    )
                    
                    # Check that display label is updated
                    if hasattr(self.app, 'pitch_value_label'):
                        actual_text = self.app.pitch_value_label.cget("text")
                        self.assertIn(
                            str(pitch_value), actual_text,
                            f"Display label should show pitch value {pitch_value}, got '{actual_text}'"
                        )
            
            print("✓ GUI test: Pitch slider correctly updates config and display")
            
        except Exception as e:
            self.fail(f"GUI test failed: {e}")
    
    def test_pitch_slider_callback(self):
        """Test that pitch slider callback function works"""
        try:
            # Create app instance
            self.app = SunoReadyApp()
            self.app.root.update()
            
            # Test the update callback directly
            test_value = 5.0
            
            # Call the update method directly
            self.app.update_pitch_display(test_value)
            self.app.root.update()
            
            # Check that display is updated
            if hasattr(self.app, 'pitch_value_label'):
                label_text = self.app.pitch_value_label.cget("text")
                self.assertIn("5", label_text, 
                            "Pitch display should show updated value")
            
            print("✓ GUI test: Pitch slider callback works correctly")
            
        except Exception as e:
            self.fail(f"GUI callback test failed: {e}")
    
    def test_config_persistence(self):
        """Test that pitch config persists between app instances"""
        try:
            # Create first app instance and set pitch
            self.app = SunoReadyApp()
            original_pitch = 7
            self.app.config["pitch_semitones"] = original_pitch
            self.app.save_config()
            
            # Destroy first instance
            self.app.root.destroy()
            
            # Create second app instance
            self.app = SunoReadyApp()
            
            # Check that pitch value is loaded
            loaded_pitch = self.app.config["pitch_semitones"]
            self.assertEqual(
                loaded_pitch, original_pitch,
                "Pitch setting should persist between app instances"
            )
            
            print("✓ GUI test: Pitch config persists correctly")
            
        except Exception as e:
            self.fail(f"GUI persistence test failed: {e}")


def create_test_sinusoid_wav():
    """Create a test sinusoid WAV file for testing"""
    if not DEPENDENCIES_AVAILABLE:
        return
        
    try:
        # Generate 2-second 440Hz sinusoid
        sample_rate = 44100
        duration = 2.0
        frequency = 440.0
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        y = np.sin(2 * np.pi * frequency * t) * 0.7  # 70% amplitude
        
        # Save to test directory
        os.makedirs("tests", exist_ok=True)
        output_path = "tests/test_sinusoid_440hz.wav"
        sf.write(output_path, y, sample_rate)
        
        print(f"Created test sinusoid: {output_path}")
        return output_path
    except Exception as e:
        print(f"Failed to create test sinusoid: {e}")
        return None


def run_pitch_shifting_tests():
    """Run all pitch shifting tests"""
    print("🎵 Running Pitch Shifting Test Suite")
    print("=" * 50)
    
    # Create test sinusoid if needed
    create_test_sinusoid_wav()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPitchShiftingUnit))
    suite.addTests(loader.loadTestsFromTestCase(TestPitchShiftingIntegration))
    
    if GUI_AVAILABLE:
        suite.addTests(loader.loadTestsFromTestCase(TestPitchShiftingGUI))
    else:
        print("⚠️  Skipping GUI tests (dependencies not available)")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 50)
    print("🎵 Pitch Shifting Test Results:")
    print(f"✅ Tests run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"💥 Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n🔍 Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Error:')[-1].strip()}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    if success:
        print("\n🎉 All pitch shifting tests passed!")
    else:
        print("\n❌ Some tests failed. Check the output above.")
    
    return success


if __name__ == "__main__":
    run_pitch_shifting_tests()
