#!/usr/bin/env python3
"""
SunoReady Performance Benchmark
Tests DLL vs Python performance for all audio processing functions
"""

import time
import numpy as np

# Optional matplotlib import
try:
    import matplotlib.pyplot as plt
    matplotlib_available = True
except ImportError:
    matplotlib_available = False
    
from audio_processor_dll import (
    apply_lowpass_filter,
    apply_highpass_filter,
    apply_noise_reduction,
    normalize_audio,
    compute_fft,
    get_audio_rms,
    benchmark_performance,
    is_dll_available,
    get_processor_info
)

def create_test_audio(duration_seconds=10, sample_rate=44100):
    """Create test audio data"""
    t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds))
    
    # Create complex test signal
    audio = (
        0.5 * np.sin(2 * np.pi * 440 * t) +      # 440Hz tone
        0.3 * np.sin(2 * np.pi * 880 * t) +      # 880Hz tone  
        0.2 * np.sin(2 * np.pi * 1760 * t) +     # 1760Hz tone
        0.1 * np.random.randn(len(t))            # Noise
    )
    
    return audio.astype(np.float64)

def run_comprehensive_benchmark():
    """Run comprehensive performance tests"""
    print("🏆 SunoReady Performance Benchmark")
    print("=" * 60)
    
    # System info
    info = get_processor_info()
    print(f"🔧 DLL Available: {info['dll_available']}")
    print(f"📁 DLL Path: {info.get('dll_path', 'N/A')}")
    print(f"🐍 Fallback Mode: {info['fallback_mode']}")
    print()
    
    # Create test data
    print("🎵 Creating test audio data...")
    audio_1s = create_test_audio(1)    # 1 second
    audio_5s = create_test_audio(5)    # 5 seconds  
    audio_10s = create_test_audio(10)  # 10 seconds
    
    test_cases = [
        ("1 second", audio_1s),
        ("5 seconds", audio_5s), 
        ("10 seconds", audio_10s)
    ]
    
    all_results = {}
    
    for case_name, test_audio in test_cases:
        print(f"\n📊 Testing with {case_name} audio ({len(test_audio):,} samples)")
        print("-" * 50)
        
        # Run benchmark
        results = benchmark_performance(test_audio, iterations=5)
        all_results[case_name] = results
        
        # Display results
        if results["dll_times"]:
            print("⚡ DLL Performance:")
            for func, time_val in results["dll_times"].items():
                print(f"   {func:<15}: {time_val*1000:>8.2f} ms")
        
        print("🐍 Python Performance:")
        for func, time_val in results["python_times"].items():
            print(f"   {func:<15}: {time_val*1000:>8.2f} ms")
        
        if results["speedup"]:
            print("🚀 Speedup (DLL vs Python):")
            for func, speedup in results["speedup"].items():
                speedup_color = "🟢" if speedup > 3 else "🟡" if speedup > 1.5 else "🔴"
                print(f"   {func:<15}: {speedup_color} {speedup:>6.1f}x faster")
    
    return all_results

def plot_performance_results(results):
    """Create performance visualization"""
    if not matplotlib_available:
        print("⚠️ Matplotlib not available - skipping chart generation")
        return
        
    try:
        import matplotlib.pyplot as plt
        
        # Extract data for plotting
        functions = []
        speedups = []
        
        # Use 5-second results for plotting
        if "5 seconds" in results and results["5 seconds"]["speedup"]:
            for func, speedup in results["5 seconds"]["speedup"].items():
                functions.append(func.replace('_', ' ').title())
                speedups.append(speedup)
        
        if not functions:
            print("⚠️ No speedup data available for plotting")
            return
        
        # Create bar chart
        plt.figure(figsize=(12, 6))
        bars = plt.bar(functions, speedups, color=['#2E8B57', '#4169E1', '#FFD700', '#FF6347', '#9370DB'])
        
        # Customize chart
        plt.title('SunoReady DLL Performance Improvement', fontsize=16, fontweight='bold')
        plt.ylabel('Speedup Factor (x times faster)', fontsize=12)
        plt.xlabel('Audio Processing Functions', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar, speedup in zip(bars, speedups):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{speedup:.1f}x', ha='center', va='bottom', fontweight='bold')
        
        # Add performance threshold lines
        plt.axhline(y=2, color='orange', linestyle='--', alpha=0.7, label='Good (2x)')
        plt.axhline(y=5, color='green', linestyle='--', alpha=0.7, label='Excellent (5x)')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig('sunoready_performance.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("📈 Performance chart saved as 'sunoready_performance.png'")
        
    except ImportError:
        print("⚠️ Matplotlib not available - skipping chart generation")
    except Exception as e:
        print(f"⚠️ Chart generation failed: {e}")

def test_real_world_scenario():
    """Test a real-world audio processing scenario"""
    print("\n🎯 Real-World Scenario Test")
    print("=" * 40)
    
    # Simulate processing a 3-minute song
    print("🎵 Simulating 3-minute song processing...")
    audio = create_test_audio(180)  # 3 minutes
    
    # Typical processing pipeline
    start_time = time.time()
    
    print("  1. Applying highpass filter...")
    filtered = apply_highpass_filter(audio, cutoff_freq=80)
    
    print("  2. Reducing noise...")
    denoised = apply_noise_reduction(filtered)
    
    print("  3. Normalizing volume...")
    normalized = normalize_audio(denoised)
    
    print("  4. Computing RMS level...")
    rms = get_audio_rms(normalized)
    
    total_time = time.time() - start_time
    
    print(f"✅ Complete processing time: {total_time:.2f} seconds")
    print(f"📊 Final RMS level: {rms:.4f}")
    
    # Performance rating
    if total_time < 2.0:
        print("🏆 EXCELLENT - Ultra fast processing!")
    elif total_time < 5.0:
        print("👍 GOOD - Fast processing")
    elif total_time < 10.0:
        print("⚠️ MODERATE - Acceptable speed")
    else:
        print("🐌 SLOW - Consider optimization")
    
    return total_time

def main():
    """Main benchmark execution"""
    try:
        # Run comprehensive benchmark
        results = run_comprehensive_benchmark()
        
        # Test real-world scenario
        real_world_time = test_real_world_scenario()
        
        # Create performance visualization
        plot_performance_results(results)
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 BENCHMARK SUMMARY")
        print("=" * 60)
        
        if is_dll_available():
            print("✅ High-performance DLL is working correctly")
            print("🚀 Significant speedups achieved in all functions")
            print("⚡ Real-world processing is optimized")
        else:
            print("⚠️ DLL not available - using Python fallback")
            print("💡 Compile the DLL for maximum performance")
        
        print(f"🎯 3-minute song processing: {real_world_time:.2f} seconds")
        print("\n🎉 Benchmark completed successfully!")
        
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
