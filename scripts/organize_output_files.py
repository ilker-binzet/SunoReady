#!/usr/bin/env python3
"""
Script to organize existing output files into new folder structure
Moves processed files to output/processed/ and keeps downloads separate
"""

import os
import shutil
from pathlib import Path

def organize_output_files():
    """Organize existing files in output folder"""
    
    output_dir = Path("output")
    processed_dir = output_dir / "processed"
    downloads_dir = output_dir / "downloads"
    
    # Create directories if they don't exist
    processed_dir.mkdir(exist_ok=True)
    downloads_dir.mkdir(exist_ok=True)
    
    print("🗂️ Organizing output files...")
    
    moved_count = 0
    
    # Move all _processed files to processed folder
    for file_path in output_dir.glob("*_processed.*"):
        if file_path.is_file():
            dest_path = processed_dir / file_path.name
            print(f"📁 Moving {file_path.name} -> processed/")
            shutil.move(str(file_path), str(dest_path))
            moved_count += 1
    
    # Move other audio files (likely downloads) to downloads folder  
    audio_extensions = {'.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg'}
    for file_path in output_dir.iterdir():
        if (file_path.is_file() and 
            file_path.suffix.lower() in audio_extensions and
            not file_path.name.startswith('.') and
            file_path.name != '.gitkeep'):
            
            dest_path = downloads_dir / file_path.name
            print(f"📥 Moving {file_path.name} -> downloads/")
            shutil.move(str(file_path), str(dest_path))
            moved_count += 1
    
    print(f"\n✅ Organization complete! Moved {moved_count} files.")
    print(f"📁 Processed files: {len(list(processed_dir.glob('*')))} files")
    print(f"📥 Downloaded files: {len(list(downloads_dir.glob('*')))} files")

if __name__ == "__main__":
    organize_output_files()
