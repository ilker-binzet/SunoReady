/*
 * SunoReady High-Performance Audio Processing DLL
 * Optimized C++ audio processing functions for Python integration
 * Compiled as: sunoready_audio.dll
 */

#include <vector>
#include <complex>
#include <cmath>
#include <algorithm>
#include <memory>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

extern "C" {
    
    // Forward declarations
    void fft(std::vector<std::complex<double>>& data, bool inverse = false);
    
    // Export definitions for DLL
    __declspec(dllexport) int process_audio_fft(
        double* input_data, 
        int length, 
        double* output_real, 
        double* output_imag
    );
    
    __declspec(dllexport) int apply_lowpass_filter(
        double* audio_data, 
        int length, 
        double cutoff_freq, 
        double sample_rate
    );
    
    __declspec(dllexport) int apply_highpass_filter(
        double* audio_data, 
        int length, 
        double cutoff_freq, 
        double sample_rate
    );
    
    __declspec(dllexport) int apply_noise_reduction(
        double* audio_data, 
        int length, 
        double noise_floor, 
        double reduction_factor
    );
    
    __declspec(dllexport) int normalize_audio(
        double* audio_data, 
        int length, 
        double target_level
    );
    
    __declspec(dllexport) int apply_tempo_change(
        double* audio_data, 
        int length, 
        double tempo_factor,
        double* output_data,
        int* output_length
    );
    
    __declspec(dllexport) double get_audio_rms(
        double* audio_data, 
        int length
    );
    
    __declspec(dllexport) int dll_change_pitch(
        double* samples, 
        int length, 
        int sample_rate, 
        double semitones
    );
}

// Fast FFT implementation (Cooley-Tukey algorithm)
void fft(std::vector<std::complex<double>>& data, bool inverse) {
    int n = data.size();
    if (n <= 1) return;
    
    // Bit-reversal permutation
    for (int i = 1, j = 0; i < n; i++) {
        int bit = n >> 1;
        for (; j & bit; bit >>= 1) {
            j ^= bit;
        }
        j ^= bit;
        if (i < j) {
            std::swap(data[i], data[j]);
        }
    }
    
    // FFT computation
    for (int len = 2; len <= n; len <<= 1) {
        double angle = 2 * M_PI / len * (inverse ? 1 : -1);
        std::complex<double> wlen(cos(angle), sin(angle));
        
        for (int i = 0; i < n; i += len) {
            std::complex<double> w(1);
            for (int j = 0; j < len / 2; j++) {
                std::complex<double> u = data[i + j];
                std::complex<double> v = data[i + j + len / 2] * w;
                data[i + j] = u + v;
                data[i + j + len / 2] = u - v;
                w *= wlen;
            }
        }
    }
    
    if (inverse) {
        for (auto& x : data) {
            x /= n;
        }
    }
}

// FFT processing for Python
int process_audio_fft(double* input_data, int length, double* output_real, double* output_imag) {
    try {
        // Find next power of 2
        int fft_size = 1;
        while (fft_size < length) fft_size <<= 1;
        
        std::vector<std::complex<double>> data(fft_size);
        
        // Copy input data and pad with zeros
        for (int i = 0; i < length; i++) {
            data[i] = std::complex<double>(input_data[i], 0.0);
        }
        for (int i = length; i < fft_size; i++) {
            data[i] = std::complex<double>(0.0, 0.0);
        }
        
        // Perform FFT
        fft(data, false);
        
        // Copy results
        for (int i = 0; i < length; i++) {
            output_real[i] = data[i].real();
            output_imag[i] = data[i].imag();
        }
        
        return 0; // Success
    } catch (...) {
        return -1; // Error
    }
}

// Optimized Butterworth lowpass filter
int apply_lowpass_filter(double* audio_data, int length, double cutoff_freq, double sample_rate) {
    try {
        double rc = 1.0 / (2.0 * M_PI * cutoff_freq);
        double dt = 1.0 / sample_rate;
        double alpha = dt / (rc + dt);
        
        // Apply filter
        for (int i = 1; i < length; i++) {
            audio_data[i] = audio_data[i-1] + alpha * (audio_data[i] - audio_data[i-1]);
        }
        
        return 0;
    } catch (...) {
        return -1;
    }
}

// Optimized highpass filter
int apply_highpass_filter(double* audio_data, int length, double cutoff_freq, double sample_rate) {
    try {
        double rc = 1.0 / (2.0 * M_PI * cutoff_freq);
        double dt = 1.0 / sample_rate;
        double alpha = rc / (rc + dt);
        
        std::vector<double> filtered(length);
        filtered[0] = audio_data[0];
        
        for (int i = 1; i < length; i++) {
            filtered[i] = alpha * (filtered[i-1] + audio_data[i] - audio_data[i-1]);
        }
        
        // Copy back
        for (int i = 0; i < length; i++) {
            audio_data[i] = filtered[i];
        }
        
        return 0;
    } catch (...) {
        return -1;
    }
}

// Spectral noise reduction
int apply_noise_reduction(double* audio_data, int length, double noise_floor, double reduction_factor) {
    try {
        // Simple spectral gating approach
        for (int i = 0; i < length; i++) {
            double magnitude = std::abs(audio_data[i]);
            if (magnitude < noise_floor) {
                audio_data[i] *= reduction_factor;
            }
        }
        return 0;
    } catch (...) {
        return -1;
    }
}

// Peak normalization
int normalize_audio(double* audio_data, int length, double target_level) {
    try {
        // Find peak
        double peak = 0.0;
        for (int i = 0; i < length; i++) {
            peak = std::max(peak, std::abs(audio_data[i]));
        }
        
        if (peak > 0.0) {
            double gain = target_level / peak;
            for (int i = 0; i < length; i++) {
                audio_data[i] *= gain;
            }
        }
        
        return 0;
    } catch (...) {
        return -1;
    }
}

// Simple time-stretching for tempo change
int apply_tempo_change(double* audio_data, int length, double tempo_factor, double* output_data, int* output_length) {
    try {
        int new_length = static_cast<int>(length / tempo_factor);
        *output_length = new_length;
        
        for (int i = 0; i < new_length; i++) {
            double src_index = i * tempo_factor;
            int index1 = static_cast<int>(src_index);
            int index2 = std::min(index1 + 1, length - 1);
            double fraction = src_index - index1;
            
            // Linear interpolation
            output_data[i] = audio_data[index1] * (1.0 - fraction) + audio_data[index2] * fraction;
        }
        
        return 0;
    } catch (...) {
        return -1;
    }
}

// Calculate RMS level
double get_audio_rms(double* audio_data, int length) {
    try {
        double sum = 0.0;
        for (int i = 0; i < length; i++) {
            sum += audio_data[i] * audio_data[i];
        }
        return std::sqrt(sum / length);
    } catch (...) {
        return -1.0;
    }
}

// Simple and robust pitch shifting using linear interpolation
int dll_change_pitch(double* samples, int length, int sample_rate, double semitones) {
    try {
        // Validate inputs
        if (samples == nullptr || length <= 0 || sample_rate <= 0) {
            return -1;
        }
        
        if (semitones == 0.0) {
            return 0; // No change needed
        }
        
        // Calculate pitch ratio from semitones
        double pitch_ratio = std::pow(2.0, semitones / 12.0);
        
        // Clamp to reasonable range to prevent crashes
        if (pitch_ratio < 0.25 || pitch_ratio > 4.0) {
            return -2; // Pitch shift too extreme
        }
        
        // Use simple linear interpolation approach (more stable)
        std::vector<double> temp_data;
        try {
            temp_data.reserve(length);
            temp_data.assign(samples, samples + length);
        } catch (...) {
            return -3; // Memory allocation failed
        }
        
        // Apply pitch shift using resampling
        for (int i = 0; i < length; i++) {
            double src_index = i / pitch_ratio;
            
            if (src_index >= length - 1) {
                samples[i] = 0.0; // Pad with silence
            } else if (src_index < 0) {
                samples[i] = 0.0; // Pad with silence
            } else {
                int index1 = static_cast<int>(std::floor(src_index));
                int index2 = index1 + 1;
                
                // Ensure bounds safety
                if (index1 < 0) index1 = 0;
                if (index2 >= length) index2 = length - 1;
                if (index1 >= length) index1 = length - 1;
                
                double fraction = src_index - index1;
                
                // Linear interpolation
                samples[i] = temp_data[index1] * (1.0 - fraction) + temp_data[index2] * fraction;
                
                // Clamp output to prevent overflow
                if (samples[i] > 1.0) samples[i] = 1.0;
                if (samples[i] < -1.0) samples[i] = -1.0;
            }
        }
        
        return 0; // Success
    } catch (const std::exception& e) {
        return -4; // Standard exception
    } catch (...) {
        return -5; // Unknown error
    }
}
