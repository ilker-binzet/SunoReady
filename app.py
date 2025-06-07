"""
SunoReady - Audio Processing Application
Main GUI application using customtkinter for Windows 11
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import threading
from pathlib import Path
import subprocess
import sys

from audio_utils import AudioProcessor
from yt_downloader import YouTubeDownloader
from metadata_utils import MetadataUtils

# Set appearance and theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SunoReadyApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("SunoReady - Audio Processing Tool")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Initialize utilities
        self.audio_processor = AudioProcessor()
        self.yt_downloader = YouTubeDownloader()
        self.metadata_utils = MetadataUtils()
        
        # Load configuration
        self.config = self.load_config()
        
        # Create output directory
        os.makedirs("output", exist_ok=True)
        
        # Initialize UI
        self.setup_ui()
        
        # Current files list
        self.selected_files = []
        
    def load_config(self):
        """Load configuration from config.json"""
        try:
            with open("config.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Default configuration
            default_config = {
                "pitch_shift": 0,
                "tempo_change": 100,
                "trim_duration": 90,
                "normalize_volume": True,
                "add_noise": False,
                "apply_highpass": False,
                "output_format": "mp3"
            }
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config=None):
        """Save configuration to config.json"""
        if config is None:
            config = self.config
        with open("config.json", "w") as f:
            json.dump(config, indent=2, fp=f)
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="SunoReady Audio Processor", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Create notebook for tabs
        self.notebook = ctk.CTkTabview(main_frame)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Audio Processing Tab
        self.setup_audio_tab()
        
        # YouTube Downloader Tab
        self.setup_youtube_tab()
        
        # Status and Progress
        self.setup_status_section(main_frame)
    
    def setup_audio_tab(self):
        """Setup audio processing tab"""
        audio_tab = self.notebook.add("Audio Processing")
        
        # File selection section
        file_frame = ctk.CTkFrame(audio_tab)
        file_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(file_frame, text="Audio Files", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        
        # File selection buttons
        button_frame = ctk.CTkFrame(file_frame)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(
            button_frame, 
            text="Select Files", 
            command=self.select_files,
            width=120
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            button_frame, 
            text="Clear All", 
            command=self.clear_files,
            width=120
        ).pack(side="left")
        
        # Selected files display
        self.files_text = ctk.CTkTextbox(file_frame, height=100)
        self.files_text.pack(fill="x", padx=20, pady=(10, 20))
        
        # Processing options
        options_frame = ctk.CTkFrame(audio_tab)
        options_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(options_frame, text="Processing Options", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        
        # Options grid
        grid_frame = ctk.CTkFrame(options_frame)
        grid_frame.pack(fill="x", padx=20, pady=10)
        
        # Pitch shift
        ctk.CTkLabel(grid_frame, text="Pitch Shift (semitones):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.pitch_var = ctk.StringVar(value=str(self.config["pitch_shift"]))
        self.pitch_entry = ctk.CTkEntry(grid_frame, textvariable=self.pitch_var, width=100)
        self.pitch_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Tempo change
        ctk.CTkLabel(grid_frame, text="Tempo Change (%):").grid(row=0, column=2, sticky="w", padx=10, pady=5)
        self.tempo_var = ctk.StringVar(value=str(self.config["tempo_change"]))
        self.tempo_entry = ctk.CTkEntry(grid_frame, textvariable=self.tempo_var, width=100)
        self.tempo_entry.grid(row=0, column=3, padx=10, pady=5)
        
        # Trim duration
        ctk.CTkLabel(grid_frame, text="Trim Duration (seconds):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.trim_var = ctk.StringVar(value=str(self.config["trim_duration"]))
        self.trim_entry = ctk.CTkEntry(grid_frame, textvariable=self.trim_var, width=100)
        self.trim_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Checkboxes
        checkbox_frame = ctk.CTkFrame(options_frame)
        checkbox_frame.pack(fill="x", padx=20, pady=10)
        
        self.normalize_var = ctk.BooleanVar(value=self.config["normalize_volume"])
        ctk.CTkCheckBox(checkbox_frame, text="Normalize Volume", variable=self.normalize_var).pack(side="left", padx=10)
        
        self.noise_var = ctk.BooleanVar(value=self.config["add_noise"])
        ctk.CTkCheckBox(checkbox_frame, text="Add Light Noise", variable=self.noise_var).pack(side="left", padx=10)
        
        self.highpass_var = ctk.BooleanVar(value=self.config["apply_highpass"])
        ctk.CTkCheckBox(checkbox_frame, text="Apply Highpass Filter", variable=self.highpass_var).pack(side="left", padx=10)
        
        # Process button
        process_frame = ctk.CTkFrame(audio_tab)
        process_frame.pack(fill="x", padx=20, pady=20)
        
        self.process_btn = ctk.CTkButton(
            process_frame, 
            text="Process Audio Files", 
            command=self.process_audio_files,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.process_btn.pack(pady=20)
    
    def setup_youtube_tab(self):
        """Setup YouTube downloader tab"""
        yt_tab = self.notebook.add("YouTube Downloader")
        
        # Search section
        search_frame = ctk.CTkFrame(yt_tab)
        search_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(search_frame, text="YouTube Search & Download", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        
        # URL/Search input
        input_frame = ctk.CTkFrame(search_frame)
        input_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(input_frame, text="YouTube URL or Search Query:").pack(anchor="w", padx=10, pady=(10, 5))
        self.yt_input = ctk.CTkEntry(input_frame, placeholder_text="Enter YouTube URL or search terms...")
        self.yt_input.pack(fill="x", padx=10, pady=(0, 10))
        
        # Search and download buttons
        button_frame = ctk.CTkFrame(search_frame)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(
            button_frame, 
            text="Search", 
            command=self.search_youtube,
            width=120
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            button_frame, 
            text="Download", 
            command=self.download_youtube,
            width=120
        ).pack(side="left")
        
        # Search results
        results_frame = ctk.CTkFrame(yt_tab)
        results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(results_frame, text="Search Results", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        self.results_text = ctk.CTkTextbox(results_frame, height=200)
        self.results_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    def setup_status_section(self, parent):
        """Setup status and progress section"""
        status_frame = ctk.CTkFrame(parent)
        status_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(status_frame)
        self.progress.pack(fill="x", padx=20, pady=10)
        self.progress.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(status_frame, text="Ready", font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=(0, 10))
    
    def select_files(self):
        """Open file dialog to select audio files"""
        filetypes = [
            ("Audio Files", "*.mp3 *.wav *.flac *.m4a *.aac *.ogg"),
            ("MP3 Files", "*.mp3"),
            ("WAV Files", "*.wav"),
            ("FLAC Files", "*.flac"),
            ("All Files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=filetypes
        )
        
        if files:
            self.selected_files.extend(files)
            self.update_files_display()
    
    def clear_files(self):
        """Clear selected files"""
        self.selected_files = []
        self.update_files_display()
    
    def update_files_display(self):
        """Update the files display text box"""
        self.files_text.delete("1.0", "end")
        if self.selected_files:
            for i, file_path in enumerate(self.selected_files, 1):
                filename = os.path.basename(file_path)
                self.files_text.insert("end", f"{i}. {filename}\n")
        else:
            self.files_text.insert("1.0", "No files selected")
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.configure(text=message)
        self.root.update_idletasks()
    
    def update_progress(self, value):
        """Update progress bar"""
        self.progress.set(value)
        self.root.update_idletasks()
    
    def process_audio_files(self):
        """Process selected audio files"""
        if not self.selected_files:
            messagebox.showwarning("No Files", "Please select audio files to process.")
            return
        
        # Update config with current values
        try:
            self.config["pitch_shift"] = float(self.pitch_var.get())
            self.config["tempo_change"] = float(self.tempo_var.get())
            self.config["trim_duration"] = float(self.trim_var.get())
            self.config["normalize_volume"] = self.normalize_var.get()
            self.config["add_noise"] = self.noise_var.get()
            self.config["apply_highpass"] = self.highpass_var.get()
            self.save_config()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values.")
            return
        
        # Disable process button
        self.process_btn.configure(state="disabled")
        
        # Start processing in separate thread
        thread = threading.Thread(target=self._process_files_thread)
        thread.daemon = True
        thread.start()
    
    def _process_files_thread(self):
        """Process files in separate thread"""
        try:
            total_files = len(self.selected_files)
            
            for i, file_path in enumerate(self.selected_files):
                self.update_status(f"Processing {os.path.basename(file_path)}...")
                
                # Process the file
                output_path = self.audio_processor.process_audio(
                    file_path,
                    pitch_shift=self.config["pitch_shift"],
                    tempo_change=self.config["tempo_change"] / 100.0,
                    trim_duration=self.config["trim_duration"],
                    normalize=self.config["normalize_volume"],
                    add_noise=self.config["add_noise"],
                    apply_highpass=self.config["apply_highpass"]
                )
                
                # Clean metadata
                self.metadata_utils.clean_metadata(output_path)
                
                # Update progress
                progress = (i + 1) / total_files
                self.update_progress(progress)
            
            self.update_status(f"Successfully processed {total_files} files!")
            messagebox.showinfo("Success", f"Processed {total_files} files. Check the 'output' folder.")
            
        except Exception as e:
            self.update_status("Error occurred during processing")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        finally:
            # Re-enable process button
            self.process_btn.configure(state="normal")
            self.update_progress(0)
    
    def search_youtube(self):
        """Search YouTube for videos"""
        query = self.yt_input.get().strip()
        if not query:
            messagebox.showwarning("No Query", "Please enter a search query or YouTube URL.")
            return
        
        self.update_status("Searching YouTube...")
        
        # Start search in separate thread
        thread = threading.Thread(target=self._search_youtube_thread, args=(query,))
        thread.daemon = True
        thread.start()
    
    def _search_youtube_thread(self, query):
        """Search YouTube in separate thread"""
        try:
            results = self.yt_downloader.search_youtube(query)
            
            # Update results display
            self.results_text.delete("1.0", "end")
            if results:
                for i, result in enumerate(results[:10], 1):  # Show top 10 results
                    self.results_text.insert("end", f"{i}. {result['title']}\n")
                    self.results_text.insert("end", f"   Duration: {result['duration']} | Views: {result['views']}\n")
                    self.results_text.insert("end", f"   URL: {result['url']}\n\n")
            else:
                self.results_text.insert("1.0", "No results found.")
            
            self.update_status("Search completed")
            
        except Exception as e:
            self.update_status("Search failed")
            messagebox.showerror("Search Error", f"Failed to search YouTube: {str(e)}")
    
    def download_youtube(self):
        """Download YouTube video as MP3"""
        url = self.yt_input.get().strip()
        if not url:
            messagebox.showwarning("No URL", "Please enter a YouTube URL.")
            return
        
        self.update_status("Downloading from YouTube...")
        
        # Start download in separate thread
        thread = threading.Thread(target=self._download_youtube_thread, args=(url,))
        thread.daemon = True
        thread.start()
    
    def _download_youtube_thread(self, url):
        """Download YouTube video in separate thread"""
        try:
            output_path = self.yt_downloader.download_audio(url)
            
            if output_path:
                # Clean metadata
                self.metadata_utils.clean_metadata(output_path)
                
                self.update_status("Download completed successfully!")
                messagebox.showinfo("Success", f"Downloaded to: {output_path}")
            else:
                self.update_status("Download failed")
                messagebox.showerror("Error", "Failed to download the video.")
                
        except Exception as e:
            self.update_status("Download failed")
            messagebox.showerror("Download Error", f"Failed to download: {str(e)}")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        app = SunoReadyApp()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Startup Error", f"Failed to start application: {str(e)}")

if __name__ == "__main__":
    main()
