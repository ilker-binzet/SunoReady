# 🎵 SunoReady - Audio Processing Tool for Suno AI

**Bypass Copyright Detection** | **Ultra Compact Design** | **Cross-Platform Audio Processing**

> 🎯 **Purpose**: Process audio files with subtle modifications to upload copyrighted/non-copyrighted songs to Suno AI platform seamlessly and bypass content detection systems.

## 📥 Latest Release: v1.0.0

### Quick Download:

- **🪟 Windows**: [Download SunoReady-v1.0.0-windows.exe](https://github.com/ilker-binzet/SunoReady/releases/download/v1.0.0/SunoReady-v1.0.0-windows.exe)
- **🍎 macOS**: [Download SunoReady-v1.0.0-macos.dmg](https://github.com/ilker-binzet/SunoReady/releases/download/v1.0.0/SunoReady-v1.0.0-macos.dmg)
- **🐧 Linux**: [Download SunoReady-v1.0.0-linux.AppImage](https://github.com/ilker-binzet/SunoReady/releases/download/v1.0.0/SunoReady-v1.0.0-linux.AppImage)

> **📱 No installation required!** Just download and run.

[📋 View All Releases](https://github.com/ilker-binzet/SunoReady/releases) | [🐛 Report Issues](https://github.com/ilker-binzet/SunoReady/issues)

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

---

## 📁 Project Structure

```
SunoReady - Python/
├── 🐍 run.py                  # Main launcher (START HERE)
├── 📦 requirements.txt        # Dependencies
│
├── 📁 src/                    # 💾 Core Application
│   ├── app.py                 # Main GUI application
│   ├── audio_utils.py         # Audio processing utilities
│   ├── yt_downloader.py       # YouTube audio downloader
│   ├── metadata_utils.py      # Metadata processing
│   ├── fast_processor.py      # Fast audio processor
│   ├── lightning_processor.py # Lightning-fast processor
│   └── audio_processor_dll.py # DLL wrapper (performance)
│
├── 📁 config/                 # ⚙️ Configuration
│   ├── config.json           # Main app settings
│   ├── theme_config.json     # UI theme settings
│   ├── pyproject.toml        # Project metadata
│   └── .env                  # Environment variables
│
├── 📁 assets/                 # 🎨 Resources
│   ├── fonts/                # Custom fonts (Noto Sans)
│   └── generated-icon.png    # App icon
│
├── 📁 build/                  # 🔧 Build Files
│   ├── sunoready_audio.dll   # High-performance audio DLL
│   ├── sunoready_audio.cpp   # DLL source code
│   └── SunoReady.spec        # PyInstaller config
│
├── 📁 scripts/                # 🛠️ Utilities
│   ├── launch.bat            # Windows launcher
│   ├── compile_dll.bat       # Compile performance DLL
│   ├── setup_dll.bat         # Setup DLL environment
│   └── organize_output_files.py # File organization
│
├── 📁 tests/                  # 🧪 Testing
│   ├── test_*.py             # All test files
│   └── *.wav                 # Test audio files
│
├── 📁 debug/                  # 🐛 Debugging
│   ├── debug_*.py            # Debug utilities
│   └── performance_*.py      # Performance analysis
│
├── 📁 docs/                   # 📚 Documentation
│   ├── README.md             # This file
│   ├── BUILD_INFO.md         # Build instructions
│   ├── COMPACT_DESIGN_COMPLETE.md # UI design docs
│   └── *.md                  # Feature documentation
│
└── 📁 output/                 # 📤 Output Files
    ├── processed/            # Processed audio files
    └── downloads/            # Downloaded YouTube audio
```

---

## ✨ Features

### 🎵 Audio Processing for Suno AI

- **Tempo Modification**: Subtle speed adjustments (95% - 105%) to avoid detection
- **Pitch Shifting**: Precise pitch control with −12 to +12 semitones range for audio fingerprint modification
- **Volume Normalization**: Consistent audio levels for platform compatibility
- **Noise Injection**: Add imperceptible white noise to alter audio signature
- **Highpass/Lowpass Filters**: Frequency adjustments to modify audio characteristics
- **Metadata Cleaning**: Remove/modify file metadata and copyright information
- **Format Conversion**: Multiple formats (MP3, WAV, FLAC, M4A, AAC, OGG)
- **Batch Processing**: Process multiple files simultaneously

### 🔧 Bypass Techniques

- **Audio Fingerprint Alteration**: Subtle modifications to avoid copyright detection
- **Spectral Modifications**: Frequency domain changes that are inaudible to humans
- **Temporal Adjustments**: Micro-timing changes to alter audio signature
- **Dynamic Range Processing**: Compression/expansion to change audio dynamics
- **Harmonic Distortion**: Minimal distortion to alter audio characteristics

### 📺 YouTube Integration

- **Audio Download**: High-quality audio extraction
- **Quality Selection**: 64kbps to 320kbps
- **Batch Processing**: Multiple URLs at once
- **Progress Tracking**: Real-time download status
- **Terminal Console**: yt-dlp command monitoring

### 🎨 Ultra Compact UI

- **Responsive Design**: Adapts to any screen size
- **Compact Mode**: Optimized for small monitors (600x400 minimum)
- **Scrollable Interface**: Never lose functionality
- **Modern Theme**: Dark theme with orange accents
- **Keyboard Shortcuts**: Efficient workflow

### ⚡ Performance

- **Lightning Processor**: Ultra-fast audio processing
- **DLL Acceleration**: Native C++ performance boost
- **Multi-threading**: Non-blocking UI operations
- **Memory Efficient**: Optimized for large files

---

## 🎯 Usage Examples

### Command Line Interface

```bash
# Show help with pitch control documentation
python sunoready_cli.py --help

# Process with pitch shift
python sunoready_cli.py process input.mp3 --pitch 3

# Batch process with multiple effects
python sunoready_cli.py process *.mp3 --pitch -2 --tempo 105 --normalize

# Show current configuration
python sunoready_cli.py config --show
```

### Basic Audio Processing

1. **Launch**: `python run.py`
2. **Select Files**: Click "Select Files" button
3. **Adjust Settings**:
   - **Tempo**: Use slider (50% - 200%)
   - **Pitch**: Adjust pitch shift (−12 to +12 semitones)
4. **Configure Options**: Check desired enhancements
5. **Process**: Click "🎵 Process Files"

### Pitch Control Usage

- **Range**: −12 to +12 semitones (2 full octaves)
- **Subtle Changes**: ±1 to ±3 semitones for copyright bypass
- **Creative Changes**: ±4 to ±12 semitones for artistic effects
- **Quality**: Smaller changes maintain better audio quality

### YouTube Audio Download

1. **Go to YouTube Tab** → "İndirme"
2. **Paste URL**: YouTube video/playlist URL
3. **Select Quality**: Choose audio bitrate
4. **Download**: Click "⬇️ Download Audio"

### Batch Processing

- Select multiple audio files at once
- All files processed with same settings
- Progress tracked individually
- Results saved to `output/processed/`

---

## 🔧 Configuration

### Main Config (`config/config.json`)

```json
{
  "tempo_change": 100,
  "normalize_volume": true,
  "add_noise": false,
  "apply_highpass": false,
  "clean_metadata": false,
  "output_format": "mp3",
  "youtube_quality": "192"
}
```

### Theme Config (`config/theme_config.json`)

- UI colors and appearance
- Font settings
- Layout preferences

---

## 🚀 Performance Modes

### 🐍 Standard Mode (Python)

- **Compatibility**: Works everywhere
- **Dependencies**: librosa, soundfile
- **Speed**: Good for small files

### ⚡ Lightning Mode (Fast Processor)

- **Speed**: 3-5x faster than standard
- **Memory**: Optimized algorithms
- **Quality**: Professional-grade processing

### 🔥 DLL Mode (Native C++)

- **Speed**: 10-20x faster than standard
- **Compilation**: Run `scripts/compile_dll.bat`
- **Platform**: Windows with Visual Studio

---

## 🧪 Testing

```bash
# Test compact design
python tests/test_compact_design.py

# Test responsive layout
python tests/test_responsive_design.py

# Test audio processing
python tests/test_audio_processing.py

# Performance benchmarks
python debug/performance_test.py
```

---

## 🛠️ Development

### Build Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build with spec file
pyinstaller build/SunoReady.spec
```

### Compile Performance DLL

```bash
# Windows with Visual Studio
scripts/compile_dll.bat

# Manual compilation
scripts/setup_dll.bat
```

---

## 📈 Recent Updates

- ✅ **Project Organization**: Clean, modular structure
- ✅ **Ultra Compact UI**: 30% smaller interface
- ✅ **Status Section Removed**: Maximum space efficiency
- ✅ **Responsive Design**: Works on any screen size
- ✅ **Performance Optimizations**: Lightning-fast processing
- ✅ **Better Documentation**: Complete guides and examples

---

## 🤝 Contributing

1. **Fork** the project
2. **Create** your feature branch
3. **Test** your changes thoroughly
4. **Document** new features
5. **Submit** a pull request

---

## ⚖️ Legal Disclaimer

**This tool is for educational and research purposes only.** Users are responsible for complying with copyright laws and platform terms of service. The developer does not encourage or endorse copyright infringement.

---

## 👨‍💻 Developer

**Ilker Binzet**  
🔗 [LinkedIn Profile](https://www.linkedin.com/in/binzet-me)  
📧 Contact for collaborations and inquiries

---

## 📄 License

This project is licensed under the MIT License.

---

## 🎉 Acknowledgments

- **CustomTkinter**: Modern UI framework
- **yt-dlp**: YouTube download functionality
- **librosa**: Audio processing library
- **Noto Sans**: Google Fonts typography
- **Suno AI**: Inspiration for this bypass tool

---

**Made with ❤️ for audio processing and AI enthusiasts**
