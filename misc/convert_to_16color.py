#!/usr/bin/env python3
"""
Convert PNG images to Pyxel's 16-color palette
"""
from PIL import Image
import numpy as np
import sys

# Pyxel's 16 colors
pyxel_colors = [
    (0x00, 0x00, 0x00),  # 0: Black
    (0x2B, 0x33, 0x5F),  # 1: Dark Blue
    (0x7E, 0x20, 0x72),  # 2: Dark Purple
    (0x19, 0x95, 0x9C),  # 3: Dark Cyan
    (0x8B, 0x48, 0x52),  # 4: Brown
    (0x39, 0x5C, 0x98),  # 5: Dark Blue
    (0xA9, 0xC1, 0xFF),  # 6: Light Blue
    (0xEE, 0xEE, 0xEE),  # 7: Light Gray
    (0xD4, 0x18, 0x6C),  # 8: Red
    (0xD3, 0x84, 0x41),  # 9: Orange
    (0xE9, 0xC3, 0x5B),  # 10: Yellow
    (0x70, 0xC6, 0xA9),  # 11: Light Green
    (0x76, 0x96, 0xDE),  # 12: Light Blue
    (0xA3, 0xA3, 0xA3),  # 13: Gray
    (0xFF, 0x97, 0x98),  # 14: Pink
    (0xED, 0xC7, 0xB0),  # 15: Peach
]

def find_closest_color(rgb):
    """Find the closest Pyxel color index for an RGB value"""
    min_dist = float('inf')
    best_index = 0
    
    for i, pyxel_rgb in enumerate(pyxel_colors):
        # Calculate color distance
        dist = sum((c1 - c2) ** 2 for c1, c2 in zip(rgb, pyxel_rgb))
        
        if dist < min_dist:
            min_dist = dist
            best_index = i
    
    return best_index

def convert_to_pyxel_palette(input_path, output_path):
    """Convert image to use Pyxel's 16-color palette"""
    
    # Open image
    img = Image.open(input_path)
    
    # Convert to RGB if needed
    if img.mode != 'RGB':
        if img.mode == 'RGBA':
            # Create new RGB image with white background
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3] if len(img.split()) > 3 else None)
            img = rgb_img
        else:
            img = img.convert('RGB')
    
    # Get pixel data
    pixels = img.load()
    width, height = img.size
    
    # Create new indexed image
    new_img = Image.new('P', (width, height))
    
    # Set up Pyxel palette for the image
    palette = []
    for r, g, b in pyxel_colors:
        palette.extend([r, g, b])
    
    # Pad palette to 256 colors (PIL requirement)
    while len(palette) < 768:  # 256 * 3
        palette.extend([0, 0, 0])
    
    new_img.putpalette(palette)
    
    # Convert each pixel
    new_pixels = new_img.load()
    color_usage = {}
    
    for y in range(height):
        for x in range(width):
            rgb = pixels[x, y]
            
            # Find closest Pyxel color
            color_index = find_closest_color(rgb)
            new_pixels[x, y] = color_index
            
            # Track color usage
            color_usage[color_index] = color_usage.get(color_index, 0) + 1
    
    # Save
    new_img.save(output_path)
    print(f"✅ Converted {input_path} -> {output_path}")
    
    # Report color usage
    print(f"   Color indices used: {sorted(color_usage.keys())}")
    print(f"   Total colors: {len(color_usage)}")
    
    return new_img

# Process files
files_to_convert = [
    'assets/map_kind.png',
    'assets/window_9slice.png',  # Convert this too if needed
]

print("Converting images to Pyxel 16-color palette...")
print()

for filepath in files_to_convert:
    try:
        # Create backup
        backup_path = filepath.replace('.png', '_original.png')
        
        # Check if file exists
        import os
        if not os.path.exists(filepath):
            print(f"⚠️  File not found: {filepath}")
            continue
            
        # Create backup if doesn't exist
        if not os.path.exists(backup_path):
            img = Image.open(filepath)
            img.save(backup_path)
            print(f"📁 Backup created: {backup_path}")
        
        # Convert to 16-color
        output_path = filepath.replace('.png', '_16color.png')
        convert_to_pyxel_palette(filepath, output_path)
        
        # Option to replace original
        print(f"   To use: rename {output_path} to {filepath}")
        
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")

print("\n✅ Conversion complete!")