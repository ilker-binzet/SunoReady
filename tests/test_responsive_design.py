#!/usr/bin/env python3
"""
Responsive Design Test
Test different screen sizes for SunoReady
"""

import customtkinter as ctk
import tkinter as tk
from pathlib import Path

# Simulate different screen sizes
SCREEN_SIZES = [
    ("Small Laptop", 1366, 768),
    ("HD Monitor", 1920, 1080), 
    ("Large Monitor", 2560, 1440),
    ("Ultra-wide", 3440, 1440),
    ("Small Tablet", 1024, 768)
]

def test_responsive_window_sizing():
    """Test responsive window sizing logic"""
    
    def calculate_window_size(screen_width, screen_height):
        """Calculate optimal window size"""
        if screen_width <= 1366 and screen_height <= 768:
            # Small monitors
            window_width = min(950, int(screen_width * 0.9))
            window_height = min(650, int(screen_height * 0.85))
            compact_mode = True
        elif screen_width <= 1920 and screen_height <= 1080:
            # Standard monitors
            window_width = min(1000, int(screen_width * 0.8))
            window_height = min(850, int(screen_height * 0.8))
            compact_mode = False
        else:
            # Large monitors
            window_width = min(1200, int(screen_width * 0.7))
            window_height = min(1000, int(screen_height * 0.75))
            compact_mode = False
            
        return window_width, window_height, compact_mode
    
    print("🖥️ Responsive Design Test Results:")
    print("=" * 50)
    
    for name, width, height in SCREEN_SIZES:
        w_width, w_height, compact = calculate_window_size(width, height)
        mode = "Compact" if compact else "Standard"
        usage = f"{(w_width/width)*100:.1f}% x {(w_height/height)*100:.1f}%"
        
        print(f"{name:15} ({width}x{height})")
        print(f"  → Window: {w_width}x{w_height} | {mode} Mode | Usage: {usage}")
        print()

def create_responsive_demo():
    """Create a demo window showing responsive design"""
    
    root = ctk.CTk()
    root.title("SunoReady - Responsive Design Demo")
    
    # Get actual screen size
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Apply responsive sizing
    if screen_width <= 1366 and screen_height <= 768:
        window_width = min(950, int(screen_width * 0.9))
        window_height = min(650, int(screen_height * 0.85))
        compact_mode = True
    elif screen_width <= 1920 and screen_height <= 1080:
        window_width = min(1000, int(screen_width * 0.8))
        window_height = min(850, int(screen_height * 0.8))
        compact_mode = False
    else:
        window_width = min(1200, int(screen_width * 0.7))
        window_height = min(1000, int(screen_height * 0.75))
        compact_mode = False
    
    # Center window
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.minsize(700, 500)
    
    # Demo content
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(fill="both", expand=True, padx=15, pady=15)
    
    # Title
    title = ctk.CTkLabel(
        main_frame,
        text="SunoReady - Responsive Design Demo",
        font=ctk.CTkFont(size=24, weight="bold")
    )
    title.pack(pady=20)
    
    # Info display
    info_frame = ctk.CTkFrame(main_frame)
    info_frame.pack(fill="x", padx=20, pady=10)
    
    mode_text = "COMPACT MODE" if compact_mode else "STANDARD MODE"
    mode_color = "#FF6B35" if compact_mode else "#27AE60"
    
    info_text = f"""
Screen Resolution: {screen_width} x {screen_height}
Window Size: {window_width} x {window_height}
Mode: {mode_text}
Usage: {(window_width/screen_width)*100:.1f}% x {(window_height/screen_height)*100:.1f}%
    """
    
    info_label = ctk.CTkLabel(
        info_frame,
        text=info_text,
        font=ctk.CTkFont(size=12),
        justify="left"
    )
    info_label.pack(pady=15)
    
    # Mode indicator
    mode_label = ctk.CTkLabel(
        main_frame,
        text=mode_text,
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color=mode_color
    )
    mode_label.pack(pady=10)
    
    # Feature list
    features_frame = ctk.CTkFrame(main_frame)
    features_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    if compact_mode:
        features_text = """
🔹 Compact padding and margins
🔹 Reduced text box heights  
🔹 Scrollable content area
🔹 Collapsible status details
🔹 Smaller button sizes
🔹 Live preview disabled
🔹 Optimized for 1366x768+
        """
    else:
        features_text = """
🔹 Standard padding and spacing
🔹 Full-height content areas
🔹 All features enabled
🔹 Live audio preview available
🔹 Standard button sizes
🔹 Rich status displays
🔹 Optimized for 1920x1080+
        """
    
    features_label = ctk.CTkLabel(
        features_frame,
        text=features_text,
        font=ctk.CTkFont(size=11),
        justify="left"
    )
    features_label.pack(pady=15)
    
    # Close button
    close_btn = ctk.CTkButton(
        main_frame,
        text="Close Demo",
        command=root.destroy,
        width=200,
        height=35
    )
    close_btn.pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    print("🧪 Running responsive design tests...\n")
    test_responsive_window_sizing()
    
    print("\n🖥️ Starting interactive demo...")
    print("Close the demo window to continue...")
    create_responsive_demo()
    
    print("✅ Responsive design test completed!")
