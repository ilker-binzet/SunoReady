"""
SunoReady - Audio Processing Application for Suno AI
Advanced audio processing tool with copyright bypass capabilities
Developer: Ilker Binzet (https://www.linkedin.com/in/binzet-me)
Main GUI application using customtkinter for cross-platform compatibility
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
import platform

from audio_utils import AudioProcessor
from yt_downloader import YouTubeDownloader
from metadata_utils import MetadataUtils
from version import __version__, get_version_string, get_build_info

# Fast processor import
try:
    from fast_processor import FastAudioProcessor
    fast_processor_available = True
except ImportError:
    fast_processor_available = False

# Lightning processor import
try:
    from lightning_processor import LightningProcessor
    lightning_processor_available = True
except ImportError:
    lightning_processor_available = False

# Set appearance and theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Modern theme colors
THEME_COLORS = {
    "bg_primary": "#2C3E50",      # Dark blue-grey background
    "bg_secondary": "#34495E",    # Slightly lighter background
    "accent": "#FF6B35",          # Orange accent color
    "accent_hover": "#E85A2F",    # Darker orange for hover
    "text_primary": "#FFFFFF",    # White text
    "text_secondary": "#BDC3C7",  # Light grey text
    "border": "#5D6D7E",          # Border color
    "success": "#27AE60",         # Green for success
    "warning": "#F39C12",         # Orange for warnings
    "error": "#E74C3C"            # Red for errors
}

def load_noto_sans_font():
    """Load Noto Sans font from the assets/fonts directory"""
    try:
        font_dir = Path("assets/fonts/Noto_Sans")
        
        # Check if font directory exists
        if not font_dir.exists():
            print("Warning: Noto Sans font directory not found. Using system default.")
            return "Segoe UI"
        
        # Try to find the regular font file
        font_files = [
            "NotoSans-VariableFont_wdth,wght.ttf",
            "static/NotoSans_Condensed-Regular.ttf",
            "static/NotoSans_ExtraCondensed-Regular.ttf"
        ]
        
        for font_file in font_files:
            font_path = font_dir / font_file
            if font_path.exists():
                # On Windows, we can register the font with the system temporarily
                if platform.system() == "Windows":
                    try:
                        import ctypes
                        from ctypes import wintypes
                        
                        # Add font resource
                        font_resource = ctypes.windll.gdi32.AddFontResourceW(str(font_path))
                        if font_resource:
                            print(f"Successfully loaded Noto Sans font from: {font_path}")
                            return "Noto Sans"
                    except Exception as e:
                        print(f"Could not register font: {e}")
                        
                # Fallback: try to use the font file directly (limited support in tkinter)
                print(f"Found Noto Sans font at: {font_path}")
                return str(font_path)
        
        print("Warning: Noto Sans font files not found. Using system default.")
        return "Segoe UI"
        
    except Exception as e:
        print(f"Error loading Noto Sans font: {e}")
        return "Segoe UI"

# Load Noto Sans font
FONT_FAMILY = load_noto_sans_font()

class SunoReadyApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("SunoReady - Audio Processing Tool")
        
        # Responsive window sizing for different screen sizes
        self.setup_responsive_window()
        
        # Make window resizable and set compact minimum size
        self.root.minsize(600, 400)  # Ultra compact minimum size
        self.root.resizable(True, True)
        
        # Apply modern theme colors
        self.apply_modern_theme()
        
        # Load configuration first
        self.config = self.load_config()
        
        # Initialize utilities with config
        self.audio_processor = AudioProcessor(config=self.config)
        
        # Initialize lightning processor (preferred)
        if lightning_processor_available:
            self.lightning_processor = LightningProcessor(config=self.config)
            self.log_to_terminal("⚡ Lightning processor ready!", "info")
        else:
            self.lightning_processor = None
        
        # Initialize fast processor if available and enabled
        if fast_processor_available and self.config.get('use_fast_processing', True):
            self.fast_processor = FastAudioProcessor(config=self.config)
            self.log_to_terminal("🚀 Fast processing mode enabled", "info")
        else:
            self.fast_processor = None
            if not lightning_processor_available:
                self.log_to_terminal("🐢 Standard processing mode (librosa)", "info")
        
        self.yt_downloader = YouTubeDownloader(log_callback=self.log_to_terminal, config=self.config)
        self.metadata_utils = MetadataUtils(log_callback=self.log_to_terminal)
        
        # Create output directories
        os.makedirs(self.config.get('processed_output_folder', 'output/processed'), exist_ok=True)
        os.makedirs(self.config.get('downloaded_output_folder', 'output/downloads'), exist_ok=True)
        
        # Check DLL performance status
        self.check_dll_performance_status()
        
        # Initialize UI
        self.setup_ui()
        
        # Synchronize UI with loaded configuration
        self.sync_ui_with_config()
        
        # Current files list
        self.selected_files = []
    
    def apply_modern_theme(self):
        """Apply modern theme with custom colors and fonts"""
        # Set window background
        self.root.configure(fg_color=THEME_COLORS["bg_primary"])
        
        # Configure default fonts
        self.font_small = ctk.CTkFont(family=FONT_FAMILY, size=10)
        self.font_regular = ctk.CTkFont(family=FONT_FAMILY, size=12)
        self.font_medium = ctk.CTkFont(family=FONT_FAMILY, size=14)
        self.font_large = ctk.CTkFont(family=FONT_FAMILY, size=16)
        self.font_title = ctk.CTkFont(family=FONT_FAMILY, size=24, weight="bold")
        self.font_heading = ctk.CTkFont(family=FONT_FAMILY, size=18, weight="bold")
        
        print(f"Applied modern theme with font family: {FONT_FAMILY}")
    
    def create_modern_button(self, parent, text, command=None, **kwargs):
        """Create a modern styled button with consistent theming"""
        default_kwargs = {
            "font": self.font_regular,
            "corner_radius": 8,
            "height": 36,
            "fg_color": THEME_COLORS["accent"],
            "hover_color": THEME_COLORS["accent_hover"],
            "text_color": THEME_COLORS["text_primary"],
            "border_width": 0
        }
        default_kwargs.update(kwargs)
        
        button = ctk.CTkButton(parent, text=text, command=command, **default_kwargs)
        return button
    
    def create_modern_frame(self, parent, **kwargs):
        """Create a modern styled frame with consistent theming"""
        default_kwargs = {
            "corner_radius": 8,
            "fg_color": THEME_COLORS["bg_secondary"],
            "border_width": 1,
            "border_color": THEME_COLORS["border"]
        }
        default_kwargs.update(kwargs)
        
        frame = ctk.CTkFrame(parent, **default_kwargs)
        return frame
    
    def create_modern_label(self, parent, text, **kwargs):
        """Create a modern styled label with consistent theming"""
        default_kwargs = {
            "font": self.font_regular,
            "text_color": THEME_COLORS["text_primary"]
        }
        default_kwargs.update(kwargs)
        
        label = ctk.CTkLabel(parent, text=text, **default_kwargs)
        return label
    
    def create_modern_entry(self, parent, **kwargs):
        """Create a modern styled entry with consistent theming"""
        default_kwargs = {
            "font": self.font_regular,
            "corner_radius": 8,
            "height": 36,
            "fg_color": THEME_COLORS["bg_primary"],
            "border_color": THEME_COLORS["border"],
            "text_color": THEME_COLORS["text_primary"]
        }
        default_kwargs.update(kwargs)
        
        entry = ctk.CTkEntry(parent, **default_kwargs)
        return entry
    
    def create_modern_combobox(self, parent, **kwargs):
        """Create a modern styled combobox with consistent theming"""
        default_kwargs = {
            "font": self.font_regular,
            "corner_radius": 8,
            "height": 36,
            "fg_color": THEME_COLORS["bg_primary"],
            "border_color": THEME_COLORS["border"],
            "text_color": THEME_COLORS["text_primary"],
            "dropdown_fg_color": THEME_COLORS["bg_secondary"],
            "dropdown_text_color": THEME_COLORS["text_primary"]
        }
        default_kwargs.update(kwargs)
        
        combobox = ctk.CTkComboBox(parent, **default_kwargs)
        return combobox
        
    def load_config(self):
        """Load configuration from config/config.json"""
        try:
            config_path = Path("config/config.json")
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Simplified default configuration
            default_config = {
                "tempo_change": 100,
                "normalize_volume": True,
                "add_noise": False,
                "reduce_noise": False,
                "apply_highpass": False,
                "output_format": "mp3",
                "clean_metadata": False,
                "pitch_semitones": 0
            }
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config=None):
        """Save configuration to config/config.json"""
        if config is None:
            config = self.config
        config_path = Path("config/config.json")
        config_path.parent.mkdir(exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(config, indent=2, fp=f)
    
    def sync_ui_with_config(self):
        """Synchronize UI state with loaded configuration values"""
        # Ensure pitch variable is set to the stored configuration value
        if hasattr(self, 'pitch_var'):
            self.pitch_var.set(self.config["pitch_semitones"])
            # Update the pitch display label to reflect the loaded value
            if hasattr(self, 'pitch_value_label'):
                self.update_pitch_display(self.config["pitch_semitones"])
        
        # Also sync other UI elements that might have been initialized before config loading
        if hasattr(self, 'tempo_var'):
            self.tempo_var.set(self.config["tempo_change"])
            if hasattr(self, 'tempo_value_label'):
                self.update_tempo_display(self.config["tempo_change"])
    
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
        """Setup the main user interface with compact responsive design"""
        # Main container with minimal padding
        main_frame = self.create_modern_frame(self.root)
        padding = 8 if getattr(self, 'compact_mode', False) else 12
        main_frame.pack(fill="both", expand=True, padx=padding, pady=padding)
        
        # Always use scrollable container for better space management
        self.setup_scrollable_ui(main_frame)
            
    def setup_scrollable_ui(self, parent):
        """Setup compact scrollable UI"""
        # Create compact scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(
            parent,
            corner_radius=4,
            fg_color=THEME_COLORS["bg_secondary"],
            scrollbar_button_color=THEME_COLORS["border"],
            scrollbar_button_hover_color=THEME_COLORS["accent"]
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Setup UI elements in scrollable frame
        self.setup_ui_elements(self.scrollable_frame)
        
    def setup_standard_ui(self, parent):
        """Setup standard UI for normal mode"""
        self.setup_ui_elements(parent)
        
    def setup_ui_elements(self, parent):
        """Setup compact UI elements"""
        # Compact title
        title_padding = (5, 8)
        title_font = self.font_medium
            
        title_label = self.create_modern_label(
            parent, 
            text="SunoReady Audio Processor",
            font=title_font
        )
        title_label.pack(pady=title_padding)
        
        # Create compact notebook for tabs
        self.notebook = ctk.CTkTabview(
            parent,
            corner_radius=4,
            fg_color=THEME_COLORS["bg_secondary"],
            segmented_button_fg_color=THEME_COLORS["bg_primary"],
            segmented_button_selected_color=THEME_COLORS["accent"],
            segmented_button_selected_hover_color=THEME_COLORS["accent_hover"],
            text_color=THEME_COLORS["text_primary"],
            segmented_button_unselected_color=THEME_COLORS["bg_primary"],
            segmented_button_unselected_hover_color=THEME_COLORS["border"]
        )
        self.notebook.pack(fill="both", expand=True, padx=3, pady=(0, 5))
        
        # Audio Processing Tab
        self.setup_audio_tab()
        
        # YouTube Downloader Tab
        self.setup_youtube_tab()
    
    def setup_audio_tab(self):
        """Setup compact audio processing tab"""
        audio_tab = self.notebook.add("Audio Processing")
        
        # Compact padding throughout
        pad_x = 10
        pad_y = 8
        
        # File selection section with compact styling
        file_frame = self.create_modern_frame(audio_tab)
        file_frame.pack(fill="x", padx=pad_x, pady=pad_y)
        
        # Compact section title
        self.create_modern_label(
            file_frame, 
            text="Audio Files", 
            font=self.font_heading
        ).pack(pady=(8, 5))
        
        # Compact file selection buttons
        button_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=pad_x, pady=5)
        
        self.create_modern_button(
            button_frame, 
            text="Select Files", 
            command=self.select_files,
            width=110
        ).pack(side="left", padx=(0, 8))
        
        self.create_modern_button(
            button_frame, 
            text="Clear All", 
            command=self.clear_files,
            width=110,
            fg_color=THEME_COLORS["warning"],
            hover_color="#E67E22"
        ).pack(side="left")
        
        # Compact files display
        self.files_text = ctk.CTkTextbox(
            file_frame, 
            height=60,
            corner_radius=6,
            font=self.font_small,
            fg_color=THEME_COLORS["bg_primary"],
            border_color=THEME_COLORS["border"],
            text_color=THEME_COLORS["text_primary"]
        )
        self.files_text.pack(fill="x", padx=pad_x, pady=(5, 8))
        
        # Compact processing options
        options_frame = self.create_modern_frame(audio_tab)
        options_frame.pack(fill="x", padx=pad_x, pady=(0, 8))
        
        self.create_modern_label(
            options_frame, 
            text="Processing Options", 
            font=self.font_heading
        ).pack(pady=(8, 5))
        
        # Compact tempo control
        tempo_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        tempo_frame.pack(fill="x", padx=12, pady=8)
        
        self.create_modern_label(tempo_frame, text="Tempo Change (%):").pack(anchor="w", padx=5, pady=(5, 2))
        
        # Compact tempo slider
        self.tempo_var = ctk.DoubleVar(value=self.config["tempo_change"])
        self.tempo_slider = ctk.CTkSlider(
            tempo_frame,
            from_=50,
            to=200,
            number_of_steps=150,
            variable=self.tempo_var,
            width=300,
            height=20,
            fg_color=THEME_COLORS["border"],
            progress_color=THEME_COLORS["accent"],
            button_color=THEME_COLORS["accent"],
            button_hover_color=THEME_COLORS["accent_hover"]
        )
        self.tempo_slider.pack(padx=10, pady=(0, 2))
        
        # Compact tempo value display
        self.tempo_value_label = self.create_modern_label(
            tempo_frame, 
            text=f"Current: {self.tempo_var.get():.0f}%",
            font=self.font_small,
            text_color=THEME_COLORS["text_secondary"]
        )
        self.tempo_value_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Bind slider to update display
        self.tempo_slider.configure(command=self.update_tempo_display)
        
        # Compact pitch control
        pitch_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        pitch_frame.pack(fill="x", padx=12, pady=8)
        
        # Create a frame for the pitch label and range info
        pitch_label_frame = ctk.CTkFrame(pitch_frame, fg_color="transparent")
        pitch_label_frame.pack(fill="x", padx=5, pady=(5, 2))
        
        self.create_modern_label(pitch_label_frame, text="Pitch Shift (semitones):").pack(side="left")
        self.create_modern_label(
            pitch_label_frame, 
            text="(Range: −12 … +12)", 
            font=self.font_small,
            text_color=THEME_COLORS["text_secondary"]
        ).pack(side="left", padx=(5, 0))
        
        # Compact pitch slider
        self.pitch_var = ctk.DoubleVar(value=self.config["pitch_semitones"])
        self.pitch_slider = ctk.CTkSlider(
            pitch_frame,
            from_=-12,
            to=12,
            number_of_steps=24,
            variable=self.pitch_var,
            width=300,
            height=20,
            fg_color=THEME_COLORS["border"],
            progress_color=THEME_COLORS["accent"],
            button_color=THEME_COLORS["accent"],
            button_hover_color=THEME_COLORS["accent_hover"]
        )
        self.pitch_slider.pack(padx=10, pady=(0, 2))
        
        # Compact pitch value display
        self.pitch_value_label = self.create_modern_label(
            pitch_frame, 
            text=f"Current: {self.pitch_var.get():.0f} st",
            font=self.font_small,
            text_color=THEME_COLORS["text_secondary"]
        )
        self.pitch_value_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Bind slider to update display
        self.pitch_slider.configure(command=self.update_pitch_display)
        
        # Compact checkboxes
        checkbox_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        checkbox_frame.pack(fill="x", padx=pad_x, pady=5)
        
        # Single compact row of checkboxes
        checkbox_row = ctk.CTkFrame(checkbox_frame, fg_color="transparent")
        checkbox_row.pack(fill="x")
        
        self.normalize_var = ctk.BooleanVar(value=self.config["normalize_volume"])
        normalize_cb = ctk.CTkCheckBox(
            checkbox_row, 
            text="Normalize", 
            variable=self.normalize_var,
            font=self.font_regular,
            text_color=THEME_COLORS["text_primary"],
            fg_color=THEME_COLORS["accent"],
            hover_color=THEME_COLORS["accent_hover"]
        )
        normalize_cb.pack(side="left", padx=(10, 20))
        
        self.noise_var = ctk.BooleanVar(value=self.config["add_noise"])
        noise_cb = ctk.CTkCheckBox(
            checkbox_row, 
            text="Add Light Noise", 
            variable=self.noise_var,
            font=self.font_regular,
            text_color=THEME_COLORS["text_primary"],
            fg_color=THEME_COLORS["accent"],
            hover_color=THEME_COLORS["accent_hover"]
        )
        normalize_cb.pack(side="left", padx=8)
        
        self.noise_var = ctk.BooleanVar(value=self.config["add_noise"])
        noise_cb = ctk.CTkCheckBox(
            checkbox_row, 
            text="Add Noise", 
            variable=self.noise_var,
            font=self.font_regular,
            text_color=THEME_COLORS["text_primary"],
            fg_color=THEME_COLORS["accent"],
            hover_color=THEME_COLORS["accent_hover"]
        )
        noise_cb.pack(side="left", padx=8)
        
        self.highpass_var = ctk.BooleanVar(value=self.config["apply_highpass"])
        highpass_cb = ctk.CTkCheckBox(
            checkbox_row, 
            text="Highpass", 
            variable=self.highpass_var,
            font=self.font_regular,
            text_color=THEME_COLORS["text_primary"],
            fg_color=THEME_COLORS["accent"],
            hover_color=THEME_COLORS["accent_hover"]
        )
        highpass_cb.pack(side="left", padx=8)
        
        self.clean_metadata_var = ctk.BooleanVar(value=self.config.get("clean_metadata", False))
        clean_metadata_cb = ctk.CTkCheckBox(
            checkbox_row, 
            text="Clean Meta", 
            variable=self.clean_metadata_var,
            font=self.font_regular,
            text_color=THEME_COLORS["text_primary"],
            fg_color=THEME_COLORS["accent"],
            hover_color=THEME_COLORS["accent_hover"]
        )
        clean_metadata_cb.pack(side="left", padx=8)
        
        # Compact process button
        process_frame = ctk.CTkFrame(audio_tab, fg_color="transparent")
        process_frame.pack(fill="x", padx=pad_x, pady=(5, 8))
        
        self.process_btn = self.create_modern_button(
            process_frame, 
            text="🎵 Process Files", 
            command=self.process_audio_files,
            height=32,
            font=self.font_regular,
            width=160
        )
        self.process_btn.pack(pady=8)
    
    def setup_youtube_tab(self):
        """Setup compact YouTube downloader tab"""
        yt_tab = self.notebook.add("YouTube Downloader")
        
        # Create compact YouTube sub-tabs
        self.yt_notebook = ctk.CTkTabview(
            yt_tab,
            corner_radius=4,
            fg_color=THEME_COLORS["bg_secondary"],
            segmented_button_fg_color=THEME_COLORS["bg_primary"],
            segmented_button_selected_color=THEME_COLORS["accent"],
            segmented_button_selected_hover_color=THEME_COLORS["accent_hover"],
            text_color=THEME_COLORS["text_primary"]
        )
        self.yt_notebook.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Create Download tab
        self.setup_download_tab()
        
        # Create Terminal tab
        self.setup_terminal_tab()
        
        # Initialize loading animation variables
        self.loading_animation_active = False
    
    def setup_download_tab(self):
        """Setup compact download tab"""
        download_tab = self.yt_notebook.add("İndirme")
        
        # Compact download section
        download_frame = self.create_modern_frame(download_tab)
        download_frame.pack(fill="x", padx=10, pady=8)
        
        self.create_modern_label(
            download_frame, 
            text="YouTube Audio Downloader", 
            font=self.font_heading
        ).pack(pady=(8, 5))
        
        # URL input with modern styling
        input_frame = ctk.CTkFrame(download_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=15)
        
        self.create_modern_label(input_frame, text="YouTube URL:").pack(
            anchor="w", padx=10, pady=(10, 8)
        )
        
        # Input and paste button row
        input_row = ctk.CTkFrame(input_frame, fg_color="transparent")
        input_row.pack(fill="x", padx=10, pady=(0, 15))
        
        self.yt_input = self.create_modern_entry(
            input_row, 
            placeholder_text="Paste YouTube URL here...",
            height=40
        )
        self.yt_input.pack(side="left", fill="x", expand=True, padx=(0, 15))
        
        # Paste from clipboard button with modern styling
        self.create_modern_button(
            input_row,
            text="📋 Paste",
            command=self.paste_from_clipboard,
            width=90,
            height=40,
            font=self.font_small
        ).pack(side="right")
        
        # Quality selection with modern styling
        quality_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        quality_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        self.create_modern_label(quality_frame, text="Audio Quality (kbps):").pack(
            side="left", padx=(0, 15)
        )
        
        # Get default quality from config
        default_quality = self.config.get("youtube_quality", "192")
        self.quality_var = ctk.StringVar(value=default_quality)
        self.quality_dropdown = self.create_modern_combobox(
            quality_frame,
            values=["64", "128", "192", "256", "320"],
            variable=self.quality_var,
            width=120,
            command=self.on_quality_change
        )
        self.quality_dropdown.pack(side="left", padx=(0, 20))
        
        # Set as default checkbox with modern styling
        self.set_default_var = ctk.BooleanVar()
        self.default_checkbox = ctk.CTkCheckBox(
            quality_frame,
            text="📌 Set as Default",
            variable=self.set_default_var,
            font=self.font_small,
            text_color=THEME_COLORS["text_primary"],
            fg_color=THEME_COLORS["accent"],
            hover_color=THEME_COLORS["accent_hover"],
            command=self.save_default_quality
        )
        self.default_checkbox.pack(side="left")
        
        # Download button (centered) with modern styling
        button_frame = ctk.CTkFrame(download_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=15)
        
        self.create_modern_button(
            button_frame, 
            text="⬇️ Download Audio", 
            command=self.download_youtube,
            width=220,
            height=45,
            font=self.font_medium,
            fg_color=THEME_COLORS["success"],
            hover_color="#229954"
        ).pack(pady=15)
        
        # Download status section - Modern and clean design
        status_frame = ctk.CTkFrame(download_tab, fg_color="transparent")
        status_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
        # Status header with modern styling
        status_header = self.create_modern_frame(status_frame)
        status_header.pack(fill="x", pady=(0, 10))
        
        header_content = ctk.CTkFrame(status_header, fg_color="transparent")
        header_content.pack(fill="x", padx=15, pady=12)
        
        # Status icon and title
        self.create_modern_label(
            header_content, 
            text="📥 Download Status", 
            font=self.font_medium
        ).pack(side="left")
        
        # Loading animation (right side)
        self.loading_label = self.create_modern_label(
            header_content, 
            text="", 
            font=self.font_small,
            text_color=THEME_COLORS["text_secondary"]
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
        """Setup compact terminal tab"""
        terminal_tab = self.yt_notebook.add("Terminal")
        
        # Compact terminal header
        terminal_header = self.create_modern_frame(terminal_tab)
        terminal_header.pack(fill="x", padx=8, pady=(8, 0))
        
        header_content = ctk.CTkFrame(terminal_header, fg_color="transparent")
        header_content.pack(fill="x", padx=8, pady=6)
        
        self.create_modern_label(
            header_content, 
            text="🖥️ yt-dlp Console", 
            font=self.font_regular
        ).pack(side="left")
        
        # Compact clear button
        self.create_modern_button(
            header_content, 
            text="🗑️ Clear", 
            command=self.clear_terminal,
            width=70,
            height=32,
            font=self.font_small,
            fg_color=THEME_COLORS["error"],
            hover_color="#C0392B"
        ).pack(side="right")
        
        # Terminal console with modern styling
        self.terminal_text = ctk.CTkTextbox(
            terminal_tab, 
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=THEME_COLORS["text_primary"],
            fg_color="#1E2329",  # Dark terminal background
            corner_radius=8,
            border_width=1,
            border_color=THEME_COLORS["border"]
        )
        self.terminal_text.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        self.loading_dots = 0
    
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
            
            # Auto-detect duration from first file for smart controls
            if files and hasattr(self, 'original_duration_var'):
                self.auto_detect_duration(files[0])
    
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
        """Update status label - thread safe (status section removed)"""
        # Status section has been removed, function kept for compatibility
        pass
    
    def update_progress(self, value):
        """Update progress bar - thread safe (progress section removed)"""
        # Progress section has been removed, function kept for compatibility
        pass
    

    
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
    
    def update_tempo_stretch_label(self, value):
        """Update tempo stretch value label when slider changes"""
        self.tempo_stretch_value_label.configure(text=f"{value:.1f}x")
    
    def update_tempo_display(self, value):
        """Update tempo display and show duration prediction"""
        tempo_percent = value
        self.tempo_value_label.configure(
            text=f"Current: {tempo_percent:.0f}% | Files will be sped up/slowed down based on tempo change"
        )
    
    def update_pitch_display(self, value):
        """Update pitch display label when slider changes"""
        pitch_semitones = value
        self.pitch_value_label.configure(
            text=f"Current: {pitch_semitones:.0f} st"
        )
    

            
    def toggle_lightning_mode(self):
        """Toggle lightning processing mode"""
        lightning_mode = self.lightning_mode_var.get()
        
        if lightning_mode and self.lightning_processor:
            self.log_to_terminal("⚡ Lightning Mode activated - ultra-fast processing!", "info")
        elif lightning_mode and not self.lightning_processor:
            self.log_to_terminal("⚠️ Lightning processor not available, using standard mode", "warning")
            self.lightning_mode_var.set(False)
        else:
            self.log_to_terminal("🐢 Lightning Mode deactivated - using slower processing", "info")
    
    def process_audio_files(self):
        """Process selected audio files"""
        if not self.selected_files:
            messagebox.showwarning("No Files", "Please select audio files to process.")
            return
        
        # Update config with current values
        try:
            self.config["tempo_change"] = float(self.tempo_var.get())
            self.config["pitch_semitones"] = float(self.pitch_var.get())
            self.config["normalize_volume"] = self.normalize_var.get()
            self.config["add_noise"] = self.noise_var.get()
            self.config["apply_highpass"] = self.highpass_var.get()
            self.config["clean_metadata"] = self.clean_metadata_var.get()
            
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
            self.update_status(f"Starting to process {total_files} files...")
            
            for i, file_path in enumerate(self.selected_files):
                base_progress = i / total_files
                self.update_status(f"Processing {os.path.basename(file_path)} ({i+1}/{total_files})...")
                print(f"DEBUG: Processing file: {file_path}")
                
                # Define progress callback for individual file processing
                def file_progress_callback(sub_progress, sub_message=""):
                    overall_progress = base_progress + (sub_progress / total_files)
                    status_msg = f"Processing {os.path.basename(file_path)} ({i+1}/{total_files}): {sub_message}"
                    self.update_status(status_msg)
                    self.update_progress(overall_progress)
                
                # Process the file - always use lightning-fast processing
                if self.lightning_processor:
                    output_path = self.lightning_processor.process_lightning_fast(
                        file_path,
                        progress_callback=file_progress_callback,
                        tempo_change=self.config["tempo_change"],
                        pitch_semitones=self.config["pitch_semitones"],
                        normalize=self.config["normalize_volume"],
                        apply_highpass=self.config["apply_highpass"],
                        clean_metadata=self.config["clean_metadata"]
                    )
                    self.log_to_terminal(f"⚡ Lightning processed: {os.path.basename(file_path)}", "info")
                else:
                    # Fallback to basic processing
                    self.log_to_terminal(f"❌ Lightning processor not available", "error")
                
                print(f"DEBUG: Output file created: {output_path}")
                
                # Update progress to next file
                progress = (i + 1) / total_files
                self.update_progress(progress)
            
            self.update_status(f"Successfully processed {total_files} files!")
            processed_folder = self.config.get('processed_output_folder', 'output/processed')
            messagebox.showinfo("Success", f"Processed {total_files} files. Check the '{processed_folder}' folder.")
            
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            print(f"DEBUG: Error during processing: {error_msg}")
            import traceback
            traceback.print_exc()
            self.update_status("Error occurred during processing")
            messagebox.showerror("Error", error_msg)
        finally:
            # Re-enable the process button - thread safe
            def _enable_button():
                self.process_btn.configure(state="normal")
                self.update_progress(0)  # Reset progress bar
                self.update_status("Ready to process files")
            self.root.after(0, _enable_button)
    
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
        
        # Debug: Log UI mode
        if hasattr(self, 'log_to_terminal'):
            if getattr(self, 'compact_mode', False):
                self.log_to_terminal("📱 COMPACT MODE: Minimal UI, scrollable content", "info")
                self.log_to_terminal("📱 Live preview disabled, ultra-compact status", "info")
            else:
                self.log_to_terminal("🖥️ STANDARD MODE: Full features enabled", "info")
        
        self.root.mainloop()

    def check_dll_performance_status(self):
        """Check and report DLL performance status"""
        try:
            from audio_processor_dll import is_dll_available, get_processor_info
            
            if is_dll_available():
                self.log_to_terminal("🚀 HIGH-PERFORMANCE MODE: DLL loaded successfully!", "success")
                self.log_to_terminal("⚡ Audio processing will be 5-20x faster", "info")
            else:
                self.log_to_terminal("🐍 STANDARD MODE: Using Python fallback", "warning")
                self.log_to_terminal("💡 Compile DLL for maximum performance (setup_dll.bat)", "info")
                
        except ImportError:
            self.log_to_terminal("🐍 STANDARD MODE: DLL wrapper not available", "warning")
        except Exception as e:
            self.log_to_terminal(f"⚠️ DLL check failed: {e}", "warning")

    def setup_responsive_window(self):
        """Setup compact responsive window sizing"""
        try:
            # Get screen dimensions
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # More aggressive compact sizing
            if screen_width <= 1366 and screen_height <= 768:
                # Small monitors - ultra compact
                window_width = min(700, int(screen_width * 0.75))
                window_height = min(500, int(screen_height * 0.65))
                self.compact_mode = True
            elif screen_width <= 1920 and screen_height <= 1080:
                # Standard monitors - still compact
                window_width = min(800, int(screen_width * 0.6))
                window_height = min(580, int(screen_height * 0.55))
                self.compact_mode = True
            else:
                # Large monitors - moderately compact
                window_width = min(900, int(screen_width * 0.5))
                window_height = min(650, int(screen_height * 0.5))
                self.compact_mode = True
            
            # Center window on screen
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            
            self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            # Log screen info
            print(f"Screen: {screen_width}x{screen_height}")
            print(f"Window: {window_width}x{window_height}")
            print(f"Compact mode: {self.compact_mode}")
        
        except Exception as e:
            # Fallback for any errors
            print(f"Error setting up responsive window: {e}")
            self.root.geometry("950x650")
            self.compact_mode = True

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
