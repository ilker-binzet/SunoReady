"""
SunoReady Version Information
Audio Processing Tool for Suno AI Platform
"""

__version__ = "1.0.0"
__version_info__ = (1, 0, 0)
__author__ = "Ilker Binzet"
__email__ = "contact@ilkerbinzet.dev"
__linkedin__ = "https://www.linkedin.com/in/binzet-me"
__description__ = "High-performance audio processing tool for Suno AI bypass and YouTube integration"
__url__ = "https://github.com/ilker-binzet/SunoReady"

# Build information
BUILD_DATE = "2025-06-19"
BUILD_TYPE = "Release"
PYTHON_VERSION = "3.11+"

# Feature flags
FEATURES = {
    "dll_acceleration": True,
    "youtube_downloader": True,
    "batch_processing": True,
    "suno_bypass": True,        # Suno AI bypass capabilities
    "audio_fingerprint": True,  # Audio fingerprint modification
    "copyright_bypass": True,   # Copyright detection bypass
    "live_preview": False,      # Removed for compact design
    "progress_tracking": False, # Removed for compact design
    "cross_platform": True,
    "auto_updates": False,
}

def get_version_string():
    """Get formatted version string"""
    return f"SunoReady v{__version__} ({BUILD_TYPE})"

def get_build_info():
    """Get build information"""
    return {
        "version": __version__,
        "build_date": BUILD_DATE,
        "build_type": BUILD_TYPE,
        "python_version": PYTHON_VERSION,
        "features": FEATURES
    }
