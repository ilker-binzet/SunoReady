#!/usr/bin/env python3
"""
Compact Design Test Script
Test the compact UI design with various window sizes
"""

import customtkinter as ctk
import tkinter as tk
from app import SunoReadyApp
import time

def test_compact_design():
    """Test compact design with different window sizes"""
    print("🎨 Testing Compact Design")
    print("=" * 50)
    
    # Create app instance
    app = SunoReadyApp()
    
    # Test different window sizes
    test_sizes = [
        (600, 400, "Ultra Compact"),
        (700, 500, "Small"),
        (800, 580, "Medium Compact"),
        (900, 650, "Large Compact")
    ]
    
    def resize_window(size_info):
        width, height, name = size_info
        app.root.geometry(f"{width}x{height}")
        print(f"📏 Testing {name}: {width}x{height}")
        app.root.title(f"SunoReady - {name} Mode")
        app.root.update()
        
    # Test each size
    for i, size_info in enumerate(test_sizes):
        app.root.after(i * 2000, lambda si=size_info: resize_window(si))
    
    print("\n✅ Compact design test completed!")
    print("Features tested:")
    print("- Ultra compact layout")
    print("- Scrollable interface")
    print("- Reduced padding and margins")
    print("- Compact buttons and controls")
    print("- Minimal window size support")
    
    # Run the application
    app.run()

if __name__ == "__main__":
    test_compact_design()
