#!/usr/bin/env python3
"""
Force Compact Mode Test - Simulate small screen
"""

import customtkinter as ctk
import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import the app but force compact mode
def force_compact_mode_test():
    """Test app in forced compact mode"""
    
    # Monkey patch the responsive window function
    original_setup = None
    
    try:
        from app import SunoReadyApp
        
        # Save original method
        original_setup = SunoReadyApp.setup_responsive_window
        
        def force_compact_responsive_window(self):
            """Force compact mode regardless of screen size"""
            # Force small window size
            window_width = 800
            window_height = 500
            self.compact_mode = True
            
            # Center on screen
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            
            self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            print(f"FORCED: Window: {window_width}x{window_height}")
            print(f"FORCED: Compact mode: {self.compact_mode}")
            
        # Replace method
        SunoReadyApp.setup_responsive_window = force_compact_responsive_window
        
        # Start app
        print("🧪 Starting SunoReady in FORCED COMPACT MODE...")
        print("Window will be 800x500 regardless of screen size")
        print("This simulates a small laptop screen")
        
        app = SunoReadyApp()
        app.root.mainloop()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Restore original method
        if original_setup:
            SunoReadyApp.setup_responsive_window = original_setup

if __name__ == "__main__":
    force_compact_mode_test()
