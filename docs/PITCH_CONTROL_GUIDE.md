# 🎵 SunoReady - Pitch Control Guide

## 📖 Overview

The **Pitch Control** feature in SunoReady allows you to adjust the pitch of audio files while maintaining their tempo. This is perfect for creating subtle variations in audio content to bypass copyright detection systems.

## 🎯 Feature Details

### Pitch Range
- **Range**: −12 to +12 semitones
- **Precision**: 1 semitone steps (24 total positions)
- **Real-time Display**: Current value shown as "Current: [value] st"

### What is a Semitone?
- **1 semitone** = the smallest musical interval in Western music
- **12 semitones** = 1 octave (double/half the frequency)
- **Positive values** = higher pitch (sharper)
- **Negative values** = lower pitch (deeper)

### Mathematical Relationship
```
Output Frequency = Input Frequency × 2^(semitones/12)
```

**Examples:**
- +1 semitone: frequency × 1.059 (5.9% higher)
- +7 semitones: frequency × 1.498 (49.8% higher)
- +12 semitones: frequency × 2.000 (1 octave higher)
- −12 semitones: frequency × 0.500 (1 octave lower)

## 🖥️ Using Pitch Control

### In the GUI

1. **Navigate to Audio Processing Tab**
   - Open SunoReady
   - Click on "Audio Processing" tab

2. **Locate Pitch Control**
   - Find "Pitch Shift (semitones): (Range: −12 … +12)"
   - Use the slider below to adjust pitch

3. **Set Your Desired Pitch**
   - Drag slider left for lower pitch (negative values)
   - Drag slider right for higher pitch (positive values)
   - Current value displays as "Current: [X] st"

4. **Process Your Files**
   - Select audio files using "Select Files" button
   - Configure other settings as needed
   - Click "🎵 Process Files" to apply pitch shift

### Visual Interface Elements

```
Pitch Shift (semitones): (Range: −12 … +12)
[==================●====================]
           Current: +3 st
```

## 🎼 Practical Usage Examples

### Subtle Copyright Bypass
- **+1 to +3 semitones**: Barely noticeable, effective for detection avoidance
- **−1 to −3 semitones**: Subtle deepening of audio

### Creative Applications
- **+7 semitones**: Significant pitch raise (perfect fifth)
- **−5 semitones**: Lower pitch while keeping clarity
- **+12 semitones**: One octave higher (chipmunk effect)
- **−12 semitones**: One octave lower (bass boost effect)

### Quality Considerations
- **±1-6 semitones**: Usually maintains good audio quality
- **±7-12 semitones**: More noticeable artifacts, use carefully
- **Extreme values**: May introduce audio distortion

## ⚙️ Configuration

### Config File Storage
The pitch setting is automatically saved to `config/config.json`:

```json
{
  "pitch_semitones": 3,
  "tempo_change": 100,
  "normalize_volume": true,
  ...
}
```

### Persistent Settings
- Your last pitch setting is remembered between sessions
- Automatically loads when you restart SunoReady
- Can be manually edited in the config file

## 🔬 Technical Implementation

### Processing Pipeline
1. **Audio Loading**: File loaded using librosa/soundfile
2. **Pitch Shifting**: Applied using high-quality algorithms
3. **Quality Preservation**: Advanced resampling maintains audio quality
4. **Output Generation**: Processed audio saved in selected format

### Performance Modes
- **Lightning Processor**: Ultra-fast pitch shifting (recommended)
- **Standard Mode**: Reliable fallback processing
- **DLL Mode**: Native C++ acceleration (if available)

### Supported Formats
- **Input**: MP3, WAV, FLAC, M4A, AAC, OGG
- **Output**: MP3, WAV, FLAC (based on configuration)

## 🧪 Testing and Validation

### Quality Check
1. Process a familiar audio file with +3 semitones
2. Listen for:
   - Pitch accuracy (higher but clear)
   - Audio quality preservation
   - No unwanted artifacts

### Frequency Verification
For technical validation, you can verify the frequency change:
- Original 440Hz → +12 semitones → 880Hz (exactly double)
- Original 440Hz → −12 semitones → 220Hz (exactly half)

## 🚨 Important Notes

### Audio Quality
- **Small changes** (±1-3 semitones): Minimal quality loss
- **Medium changes** (±4-8 semitones): Slight quality reduction
- **Large changes** (±9-12 semitones): Noticeable quality impact

### Copyright Bypass Effectiveness
- **Recommended range**: ±1 to ±5 semitones for optimal bypass
- **Too small** (±0.5): May not be effective
- **Too large** (±10+): Easily detectable as modified

### Processing Time
- Pitch shifting is CPU-intensive
- Larger files take longer to process
- Lightning processor significantly reduces processing time

## 🛠️ Troubleshooting

### Common Issues

**1. No Pitch Change Heard**
- Check if pitch value is set to 0
- Ensure files are processing correctly
- Verify output files are being generated

**2. Audio Quality Issues**
- Try smaller pitch changes (±1-5 semitones)
- Check input file quality
- Use Lightning processor for better results

**3. Processing Errors**
- Ensure sufficient disk space
- Check file permissions
- Verify input files are not corrupted

**4. Slow Processing**
- Enable Lightning processor if available
- Close other applications to free up CPU
- Process smaller batches of files

### Debug Tips
- Check terminal tab for processing logs
- Look for error messages in red
- Verify config file contains correct pitch_semitones value

## 📊 Performance Benchmarks

### Typical Processing Times
- **3-minute MP3 file**:
  - Lightning Mode: ~5-10 seconds
  - Standard Mode: ~30-60 seconds
  - DLL Mode: ~3-7 seconds

- **Quality vs Speed**: Lightning mode offers best balance

## 🎯 Best Practices

### For Copyright Bypass
1. Use subtle changes: ±2 to ±4 semitones
2. Combine with other modifications (tempo, noise)
3. Test effectiveness with your target platform
4. Don't use the same pitch shift repeatedly

### For Audio Quality
1. Start with small changes and increase gradually
2. Always preview results before batch processing
3. Keep original files as backup
4. Use highest quality input files

### For Workflow Efficiency
1. Set your preferred pitch shift as default
2. Use batch processing for multiple files
3. Enable Lightning processor for speed
4. Organize output files properly

## 🔮 Advanced Usage

### Combining with Other Effects
```
Recommended combination for maximum bypass effectiveness:
- Pitch: +3 semitones
- Tempo: 102%
- Volume: Normalize ON
- Noise: Light noise ON
- Metadata: Clean ON
```

### Scripting Integration
For advanced users, the pitch value can be set programmatically:
```python
config["pitch_semitones"] = 5  # +5 semitones
```

## 📈 Updates and Improvements

### Version History
- **v1.0**: Initial pitch control implementation
- **Current**: Optimized algorithms, improved quality

### Future Enhancements
- Fractional semitone control (e.g., +2.5 semitones)
- Pitch envelope automation
- Real-time preview functionality
- Advanced formant preservation

---

## 💡 Quick Reference

| Pitch Value | Musical Interval | Frequency Ratio | Use Case |
|-------------|------------------|-----------------|----------|
| 0 st        | No change       | 1.000×          | Baseline |
| +1 st       | Minor second    | 1.059×          | Subtle raise |
| +3 st       | Minor third     | 1.189×          | Noticeable raise |
| +7 st       | Perfect fifth   | 1.498×          | Musical interval |
| +12 st      | Octave          | 2.000×          | Double frequency |
| −5 st       | Perfect fourth down | 0.841×      | Lower pitch |
| −12 st      | Octave down     | 0.500×          | Half frequency |

**Remember**: The range is −12 to +12 semitones, giving you 2 full octaves of pitch adjustment!

---

**🎵 Happy audio processing with SunoReady!**
