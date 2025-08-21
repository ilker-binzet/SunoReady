"""
SunoReady - Cross-platform audio processing application entry point
This file provides a fallback for environments without GUI support
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

try:
    # Try to import the main GUI application
    from app import SunoReadyApp
    GUI_AVAILABLE = True
except ImportError as e:
    GUI_AVAILABLE = False
    
    # Create a stub class for non-GUI environments
    class SunoReadyApp:
        """Stub class for headless environments"""
        def __init__(self):
            self.gui_available = False
        
        def run(self):
            print("🚀 SunoReady is ready for CLI usage")

if __name__ == "__main__":
    app = SunoReadyApp()
    if not GUI_AVAILABLE:
        print("⚠️ GUI not available - install tkinter for full GUI support")
    app.run()
