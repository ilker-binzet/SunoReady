#!/usr/bin/env python3
"""
SunoReady - Audio Processing Tool
Main launcher for the organized project structure
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Change working directory to project root for relative paths
os.chdir(project_root)

if __name__ == "__main__":
    # Import and run the main application
    from app import SunoReadyApp
    
    print("🚀 Starting SunoReady Audio Processor...")
    print(f"📁 Project root: {project_root}")
    print(f"📂 Source path: {src_path}")
    
    # Create and run the application
    app = SunoReadyApp()
    app.run()
