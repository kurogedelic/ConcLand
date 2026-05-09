#!/usr/bin/env python3
"""
Analyze ConcLand palette files in detail
"""
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

import os

def analyze_palette_file(filepath):
    print(f"\n=== Analyzing {filepath} ===")
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    if not PIL_AVAILABLE:
        print("⚠️  PIL not available, cannot analyze palette details")
        return
    
    try:
        img = Image.open(filepath)
        print(f"📏 Image size: {img.width}x{img.height}")
        print(f"🎨 Mode: {img.mode}")
        
        # Get all unique colors
        colors = img.getcolors(maxcolors=256*256)
        if colors:
            print(f"🌈 Unique colors found: {len(colors)}")
            
            # Show first 16 colors (main palette)
            print(f"\n🎯 First 16 colors:")
            pixel_data = list(img.convert('RGB').getdata())
            for i in range(min(16, len(pixel_data))):
                r, g, b = pixel_data[i]
                hex_color = f"#{r:02X}{g:02X}{b:02X}"
                print(f"  Color {i:2d}: RGB({r:3d},{g:3d},{b:3d}) = {hex_color}")
        else:
            print("⚠️  Could not extract color information")
            
    except Exception as e:
        print(f"❌ Error analyzing {filepath}: {e}")

def main():
    print("🎨 ConcLand Palette Analysis")
    
    palette_files = [
        "assets/palette256.png",
        "assets/palette256_large.png"
    ]
    
    for palette_file in palette_files:
        analyze_palette_file(palette_file)
    
    # Check what colors are actually used in game code
    print(f"\n=== Colors Used in Game Code ===")
    with open("concland_mini.py", "r") as f:
        content = f.read()
        
    # Find color usage patterns
    import re
    color_patterns = re.findall(r'pyxel\.\w+\([^)]*,\s*(\d+)\)', content)
    used_colors = sorted(set(int(c) for c in color_patterns if c.isdigit() and int(c) <= 15))
    
    print(f"🎯 Colors used in game code: {used_colors}")
    for color in used_colors:
        print(f"  Color {color}: Used in UI/graphics")

if __name__ == "__main__":
    main()