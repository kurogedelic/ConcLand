#!/usr/bin/env python3
"""Fix car overlay transparency - convert magenta background to black transparent"""

from PIL import Image
import os

def convert_magenta_to_black_transparent(input_file, output_file):
    """Convert image with magenta background to black transparent (like power/water overlays)"""
    
    # Load the image
    img = Image.open(input_file)
    print(f"Original: {img.size}, mode: {img.mode}")
    
    # Convert to RGBA for processing
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Process pixels
    width, height = img.size
    pixels = img.load()
    
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            
            # If it's magenta background (bright magenta), make it black
            if r > 200 and g < 50 and b > 200:
                pixels[x, y] = (0, 0, 0, 255)  # Black
            # Keep other colors as-is but ensure they're not magenta-ish
            elif r > 150 and g < 100 and b > 150:
                # Convert pinkish colors to gray to avoid confusion
                gray = int((r + g + b) / 3)
                pixels[x, y] = (gray, gray, gray, 255)
    
    # Convert to palette mode for smaller file size (like power_16color.png)
    img_palette = img.convert('P', palette=Image.ADAPTIVE, colors=16)
    
    # Save as PNG
    img_palette.save(output_file, 'PNG')
    print(f"✅ Converted {input_file} -> {output_file}")
    print(f"   Magenta -> Black, 16-color palette")

# Convert the files
if __name__ == "__main__":
    files_to_convert = [
        ('assets/tiles/overlay/cars_horizontal.png', 'assets/tiles/overlay/cars_horizontal_fixed.png'),
        ('assets/tiles/overlay/cars_vertical.png', 'assets/tiles/overlay/cars_vertical_fixed.png')
    ]
    
    for input_file, output_file in files_to_convert:
        if os.path.exists(input_file):
            convert_magenta_to_black_transparent(input_file, output_file)
        else:
            print(f"❌ File not found: {input_file}")