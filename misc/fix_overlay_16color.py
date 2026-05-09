#!/usr/bin/env python3
"""
Fix overlay PNGs to use Pyxel's 16-color palette with transparency
"""
from PIL import Image
import numpy as np

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

def find_closest_color(rgb, exclude_index=None):
    """Find the closest Pyxel color index for an RGB value"""
    min_dist = float('inf')
    best_index = 0
    
    for i, pyxel_rgb in enumerate(pyxel_colors):
        if exclude_index is not None and i == exclude_index:
            continue
        
        # Calculate color distance
        dist = sum((c1 - c2) ** 2 for c1, c2 in zip(rgb, pyxel_rgb))
        
        if dist < min_dist:
            min_dist = dist
            best_index = i
    
    return best_index

def convert_to_pyxel_palette(input_path, output_path, transparent_color_index=0):
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
    for y in range(height):
        for x in range(width):
            rgb = pixels[x, y]
            
            # Check if this is magenta (transparent)
            if rgb[0] >= 250 and rgb[1] <= 10 and rgb[2] >= 250:
                # Use transparent color index
                new_pixels[x, y] = transparent_color_index
            else:
                # Find closest Pyxel color, excluding transparent index
                new_pixels[x, y] = find_closest_color(rgb, exclude_index=transparent_color_index)
    
    # Save
    new_img.save(output_path)
    print(f"Converted {input_path} -> {output_path}")
    
    # Report pixel usage
    unique_colors = set()
    for y in range(height):
        for x in range(width):
            unique_colors.add(new_pixels[x, y])
    
    print(f"  Uses color indices: {sorted(unique_colors)}")
    
    return new_img

# Process overlay files
overlay_files = [
    'power.png',
    'fire.png',
    'water.png', 
    'nuclear.png',
    'cars.png'
]

print("Converting overlay files to Pyxel 16-color palette...")
print("Using color 0 (black) as transparent")
print()

for filename in overlay_files:
    input_path = f'/Users/kurogedelic/ConcLand/assets/tiles/overlay/{filename}'
    output_path = input_path.replace('.png', '_16color.png')
    
    try:
        convert_to_pyxel_palette(input_path, output_path, transparent_color_index=0)
    except Exception as e:
        print(f"Error processing {filename}: {e}")

print("\nDone! Use color index 0 as transparent in pyxel.blt()")