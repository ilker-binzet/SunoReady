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
        self.yt_downloader = YouTubeDownloader(log_callback=self.log_to_terminal)
        self.metadata_utils = MetadataUtils(log_callback=self.log_to_terminal)
        
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
    
    def paste_from_clipboard(self):
        """Paste text from clipboard to YouTube input field"""
        try:
            # Get text from clipboard
            clipboard_text = self.root.clipboard_get()
            
            # Clear current input and insert clipboard text
            self.yt_input.delete(0, 'end')
            self.yt_input.insert(0, clipboard_text.strip())
            
            # Log the action
            self.log_to_terminal(f"📋 Pasted from clipboard: {clipboard_text[:50]}...", "info")
            
        except tk.TclError:
            # Clipboard is empty or contains non-text data
            messagebox.showwarning("Clipboard Error", "Clipboard is empty or contains non-text data.")
            self.log_to_terminal("❌ Clipboard paste failed - no text data", "warning")
        except Exception as e:
            messagebox.showerror("Paste Error", f"Failed to paste from clipboard: {str(e)}")
            self.log_to_terminal(f"❌ Clipboard paste error: {str(e)}", "error")
    
    def on_quality_change(self, selected_quality):
        """Called when quality dropdown changes"""
        # Auto-uncheck the default checkbox when quality changes
        self.set_default_var.set(False)
        
        # Log quality change
        self.log_to_terminal(f"🎵 Quality changed to: {selected_quality} kbps", "info")
    
    def save_default_quality(self):
        """Save current quality as default when checkbox is checked"""
        if self.set_default_var.get():
            current_quality = self.quality_var.get()
            
            # Update config
            self.config["youtube_quality"] = current_quality
            self.save_config()
            
            # Show confirmation
            self.log_to_terminal(f"📌 Default quality set to: {current_quality} kbps", "success")
            messagebox.showinfo(
                "Default Quality Set", 
                f"Audio quality {current_quality} kbps has been set as default.\n\nThis will be used for all future downloads."
            )
            
            # Uncheck after saving
            self.root.after(1000, lambda: self.set_default_var.set(False))
        else:
            self.log_to_terminal("📌 Default quality setting cancelled", "info")
    
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
        """Setup YouTube downloader tab with sub-tabs"""
        yt_tab = self.notebook.add("YouTube Downloader")
        
        # Create a notebook for YouTube sub-tabs
        self.yt_notebook = ctk.CTkTabview(yt_tab)
        self.yt_notebook.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create Download tab
        self.setup_download_tab()
        
        # Create Terminal tab
        self.setup_terminal_tab()
        
        # Initialize loading animation variables
        self.loading_animation_active = False
        
    def setup_download_tab(self):
        """Setup the download tab within YouTube section"""
        download_tab = self.yt_notebook.add("İndirme")
        
        # Download section
        download_frame = ctk.CTkFrame(download_tab)
        download_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(download_frame, text="YouTube Audio Downloader", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        
        # URL input
        input_frame = ctk.CTkFrame(download_frame)
        input_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(input_frame, text="YouTube URL:").pack(anchor="w", padx=10, pady=(10, 5))
        
        # Input and paste button row
        input_row = ctk.CTkFrame(input_frame)
        input_row.pack(fill="x", padx=10, pady=(0, 10))
        
        self.yt_input = ctk.CTkEntry(input_row, placeholder_text="Paste YouTube URL here...")
        self.yt_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Paste from clipboard button
        ctk.CTkButton(
            input_row,
            text="📋 Paste",
            command=self.paste_from_clipboard,
            width=80,
            height=32,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#0095af",
            hover_color="#006b66"
        ).pack(side="right")
        
        # Quality selection
        quality_frame = ctk.CTkFrame(input_frame)
        quality_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(quality_frame, text="Audio Quality (kbps):").pack(side="left", padx=(0, 10))
        
        # Get default quality from config
        default_quality = self.config.get("youtube_quality", "192")
        self.quality_var = ctk.StringVar(value=default_quality)
        self.quality_dropdown = ctk.CTkOptionMenu(
            quality_frame,
            values=["64", "128", "192", "256", "320"],
            variable=self.quality_var,
            width=100,
            font=ctk.CTkFont(size=11, weight="bold"),
            dropdown_font=ctk.CTkFont(size=11),
            command=self.on_quality_change
        )
        self.quality_dropdown.pack(side="left", padx=(0, 15))
        
        # Set as default checkbox
        self.set_default_var = ctk.BooleanVar()
        self.default_checkbox = ctk.CTkCheckBox(
            quality_frame,
            text="📌 Set as Default",
            variable=self.set_default_var,
            font=ctk.CTkFont(size=11),
            text_color="#94a3b8",
            hover_color="#0ea5e9",
            command=self.save_default_quality
        )
        self.default_checkbox.pack(side="left")
        
        # Download button (centered)
        button_frame = ctk.CTkFrame(download_frame)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(
            button_frame, 
            text="⬇️ Download Audio", 
            command=self.download_youtube,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#50fa7b",
            hover_color="#6de876"
        ).pack(pady=10)
        
        # Download status section - Modern and clean design
        status_frame = ctk.CTkFrame(download_tab, fg_color="transparent")
        status_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
        # Status header with icon
        status_header = ctk.CTkFrame(status_frame, fg_color="#2d3748", corner_radius=8)
        status_header.pack(fill="x", pady=(0, 10))
        
        header_content = ctk.CTkFrame(status_header, fg_color="transparent")
        header_content.pack(fill="x", padx=15, pady=10)
        
        # Status icon and title
        ctk.CTkLabel(
            header_content, 
            text="📥 Download Status", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#e2e8f0"
        ).pack(side="left")
        
        # Loading animation (right side)
        self.loading_label = ctk.CTkLabel(
            header_content, 
            text="", 
            font=ctk.CTkFont(size=11),
            text_color="#94a3b8"
        )
        self.loading_label.pack(side="right")
        
        # Progress bar - sleek design
        progress_container = ctk.CTkFrame(status_frame, fg_color="transparent")
        progress_container.pack(fill="x", pady=(0, 10))
        
        self.download_progress = ctk.CTkProgressBar(
            progress_container,
            height=8,
            corner_radius=4,
            progress_color="#10b981",
            fg_color="#374151"
        )
        self.download_progress.pack(fill="x", padx=5)
        self.download_progress.set(0)
        
        # Status display - compact and modern
        self.status_text = ctk.CTkTextbox(
            status_frame, 
            height=120,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            corner_radius=8,
            fg_color="#1e293b",
            text_color="#f1f5f9",
            scrollbar_button_color="#475569",
            scrollbar_button_hover_color="#64748b"
        )
        self.status_text.pack(fill="both", expand=True)
        self.status_text.insert("1.0", "✨ Ready to download\n\nPaste a YouTube URL above and click Download Audio to get started.")
        
    def setup_terminal_tab(self):
        """Setup the terminal tab within YouTube section"""
        terminal_tab = self.yt_notebook.add("Terminal")
        
        # Terminal header
        terminal_header = ctk.CTkFrame(terminal_tab, fg_color="#313244")
        terminal_header.pack(fill="x", padx=20, pady=(20, 0))
        
        ctk.CTkLabel(
            terminal_header, 
            text="🖥️ yt-dlp Console", 
            font=ctk.CTkFont(size=14, weight="bold"), 
            text_color="#cdd6f4"
        ).pack(side="left", padx=15, pady=10)
        
        # Clear terminal button
        ctk.CTkButton(
            terminal_header, 
            text="🗑️ Clear", 
            command=self.clear_terminal,
            width=80,
            height=30,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#f38ba8",
            hover_color="#f2d5cf"
        ).pack(side="right", padx=15, pady=5)
        
        # Terminal console with Dracula theme colors
        self.terminal_text = ctk.CTkTextbox(
            terminal_tab, 
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#f8f8f2",  # Dracula foreground
            fg_color="#282a36",    # Dracula background
            scrollbar_button_color="#44475a",  # Dracula selection
            scrollbar_button_hover_color="#6272a4"  # Dracula comment
        )
        self.terminal_text.pack(fill="both", expand=True, padx=20, pady=(5, 20))
        self.loading_dots = 0
    
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
    

    
    def start_loading_animation(self, text="Loading"):
        """Start the loading animation"""
        self.loading_animation_active = True
        self.loading_dots = 0
        self._animate_loading(text)
    
    def stop_loading_animation(self):
        """Stop the loading animation"""
        self.loading_animation_active = False
        self.loading_label.configure(text="")
    
    def _animate_loading(self, base_text):
        """Animate loading dots"""
        if not self.loading_animation_active:
            return
        
        dots = "." * (self.loading_dots % 4)
        self.loading_label.configure(text=f"{base_text}{dots}")
        self.loading_dots += 1
        
        # Schedule next animation frame
        self.root.after(300, lambda: self._animate_loading(base_text))
    
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
    
    def download_youtube(self):
        """Download YouTube video as MP3"""
        url = self.yt_input.get().strip()
        if not url:
            messagebox.showwarning("No URL", "Please enter a YouTube URL.")
            return
        
        # Get selected quality
        selected_quality = self.quality_var.get()
        
        # Start loading animation for download
        self.start_loading_animation("Downloading")
        self.update_status("Downloading from YouTube...")
        
        # Show download progress
        self.download_progress.pack(fill="x", padx=20, pady=(0, 5))
        self.update_download_progress(0.1)
        
        # Update status display
        self.status_text.delete("1.0", "end")
        self.status_text.insert("1.0", f"🚀 Starting download...\n\n🔗 URL: {url}\n📊 Quality: {selected_quality} kbps\n\n⏳ Please wait...")
        
        # Start download in separate thread
        thread = threading.Thread(target=self._download_youtube_thread, args=(url,))
        thread.daemon = True
        thread.start()
    
    def _download_youtube_thread(self, url):
        """Download YouTube video in separate thread"""
        try:
            self.log_to_terminal("=" * 50, "info")
            self.log_to_terminal("🎵 SunoReady - YouTube Downloader", "info")
            self.log_to_terminal("=" * 50, "info")
            
            # Get selected quality
            selected_quality = self.quality_var.get()
            self.log_to_terminal(f"🎵 Audio quality: {selected_quality} kbps", "info")
            
            # Update status display with modern styling
            self.status_text.delete("1.0", "end")
            self.status_text.insert("1.0", f"⚡ Processing download...\n\n📊 Quality: {selected_quality} kbps\n🎥 Extracting video information...\n\n⏳ This may take a moment...")
            
            # Simulate download progress steps
            self.update_download_progress(0.3)
            self.root.after(500, lambda: self.update_download_progress(0.6))
            
            output_path = self.yt_downloader.download_audio(url, quality=selected_quality)
            
            self.update_download_progress(0.9)
            
            if output_path:
                # Clean metadata with progress indication
                self.log_to_terminal("Cleaning metadata...", "info")
                self.root.after(200, lambda: self.loading_label.configure(text="Cleaning metadata..."))
                self.status_text.insert("end", "\n\n🧹 Cleaning metadata...")
                self.metadata_utils.clean_metadata(output_path)
                self.log_to_terminal("Metadata cleaned successfully!", "success")
                
                # Complete the animation
                self.root.after(300, lambda: [
                    self.update_download_progress(1.0),
                    self.stop_loading_animation(),
                    self.update_status("Download completed successfully!"),
                    self.log_to_terminal("✅ Download process completed!", "success"),
                    self.status_text.delete("1.0", "end"),
                    self.status_text.insert("1.0", f"✅ Download completed successfully!\n\n📁 File saved to:\n{output_path}\n\n🎉 Ready for your next download!"),
                    messagebox.showinfo("Success", f"Downloaded to: {output_path}")
                ])
            else:
                self.stop_loading_animation()
                self.update_download_progress(0)
                self.update_status("Download failed")
                self.log_to_terminal("❌ Download failed - file not found", "error")
                self.status_text.delete("1.0", "end")
                self.status_text.insert("1.0", "❌ Download failed - file not found\n\n🔍 Please check the URL and try again.\n💡 Make sure the video is public and accessible.")
                messagebox.showerror("Error", "Failed to download the video.")
                
        except Exception as e:
            self.stop_loading_animation()
            self.update_download_progress(0)
            self.update_status("Download failed")
            self.log_to_terminal(f"❌ Download failed: {str(e)}", "error")
            self.status_text.delete("1.0", "end")
            self.status_text.insert("1.0", f"❌ Download failed!\n\n🚨 Error: {str(e)}\n\n💡 Please check the URL and try again.\n🔧 If issue persists, check your internet connection.")
            messagebox.showerror("Download Error", f"Failed to download: {str(e)}")
    
    def update_download_progress(self, value):
        """Update download progress bar"""
        if hasattr(self, 'download_progress'):
            self.download_progress.set(value)
            self.root.update_idletasks()
    
    def clear_terminal(self):
        """Clear terminal console"""
        self.terminal_text.delete("1.0", "end")
        self.log_to_terminal("Terminal cleared.", "info")
    
    def log_to_terminal(self, message, msg_type="normal"):
        """Log message to terminal with color coding"""
        timestamp = threading.current_thread().name
        
        # Color coding based on message type
        if msg_type == "info":
            color = "#8be9fd"  # Dracula cyan
            prefix = "[INFO]"
        elif msg_type == "warning":
            color = "#ffb86c"  # Dracula orange  
            prefix = "[WARN]"
        elif msg_type == "error":
            color = "#ff5555"  # Dracula red
            prefix = "[ERROR]"
        elif msg_type == "success":
            color = "#50fa7b"  # Dracula green
            prefix = "[SUCCESS]"
        elif msg_type == "youtube":
            color = "#ff79c6"  # Dracula pink
            prefix = "[YOUTUBE]"
        elif msg_type == "download":
            color = "#bd93f9"  # Dracula purple
            prefix = "[DOWNLOAD]"
        else:
            color = "#f8f8f2"  # Dracula foreground
            prefix = ""
        
        # Insert message with timestamp
        current_time = threading.current_thread().name if hasattr(threading.current_thread(), 'name') else "Main"
        
        # Check if terminal exists and add message
        if hasattr(self, 'terminal_text'):
            self.terminal_text.insert("end", f"{prefix} {message}\n")
            self.terminal_text.see("end")
            
            # Auto-switch to terminal tab for important messages
            if msg_type in ["error", "download", "youtube"] and hasattr(self, 'yt_notebook'):
                try:
                    self.yt_notebook.set("Terminal")
                except:
                    pass  # Ignore if tab switching fails
                    
            self.root.update_idletasks()

    def run(self):
        """Start the application"""
        # Add startup logs to terminal
        self.log_to_terminal("🎵 SunoReady - Audio Processing Tool", "info")
        self.log_to_terminal("Ready for audio processing and YouTube downloads.", "info")
        self.log_to_terminal("Terminal tab shows processing logs in real-time.", "info")
        self.log_to_terminal("=" * 50, "info")
        
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
