#!/usr/bin/env python3
"""Convert car overlay images to 16-color format with black transparency"""

from PIL import Image
import os

def convert_to_16color(input_file, output_file):
    """Convert image to 16-color indexed format with black (index 0) as transparent"""
    
    # Load the image
    img = Image.open(input_file)
    print(f"Original image: {img.size}, mode: {img.mode}")
    
    # Convert to RGBA if not already
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Create 16-color indexed image
    width, height = img.size
    indexed_img = Image.new('P', (width, height))
    
    # Create basic 16-color palette (matching Pyxel's default colors)
    palette = [
        # Index 0: Black (transparent)
        0, 0, 0,
        # Index 1-15: Standard colors
        29, 43, 83,      # 1: Dark blue
        126, 37, 83,     # 2: Dark purple  
        0, 135, 81,      # 3: Dark green
        171, 82, 54,     # 4: Brown
        95, 87, 79,      # 5: Dark gray
        194, 195, 199,   # 6: Light gray
        255, 241, 232,   # 7: White
        255, 0, 77,      # 8: Red
        255, 163, 0,     # 9: Orange
        255, 236, 39,    # 10: Yellow
        0, 228, 54,      # 11: Green
        41, 173, 255,    # 12: Blue
        131, 118, 156,   # 13: Indigo
        255, 119, 168,   # 14: Pink
        255, 204, 170    # 15: Peach
    ]
    
    # Extend palette to 256 colors (required for PNG)
    while len(palette) < 768:  # 256 * 3
        palette.append(0)
    
    indexed_img.putpalette(palette)
    
    # Convert pixels
    pixels = indexed_img.load()
    img_pixels = img.load()
    
    for y in range(height):
        for x in range(width):
            if img.mode == 'RGBA':
                r, g, b, a = img_pixels[x, y]
            else:
                r, g, b = img_pixels[x, y][:3]
                a = 255
            
            # Map to 16-color palette
            if a < 128:  # Transparent pixel
                pixels[x, y] = 0  # Black (will be transparent)
            elif r < 50 and g < 50 and b < 50:
                pixels[x, y] = 0  # Black
            elif r > 200 and g > 200 and b > 200:
                pixels[x, y] = 7  # White
            elif r > 150 and g > 150 and b > 150:
                pixels[x, y] = 6  # Light gray
            elif r > 100 and g > 100 and b > 100:
                pixels[x, y] = 5  # Dark gray
            elif r > 200 and g < 100 and b < 100:
                pixels[x, y] = 8  # Red
            elif r > 200 and g > 150 and b < 100:
                pixels[x, y] = 9  # Orange
            elif r > 200 and g > 200 and b < 100:
                pixels[x, y] = 10 # Yellow
            elif r < 100 and g > 150 and b < 100:
                pixels[x, y] = 11 # Green
            elif r < 100 and g < 100 and b > 200:
                pixels[x, y] = 12 # Blue
            elif r > 150 and g < 100 and b > 150:
                pixels[x, y] = 14 # Pink
            else:
                pixels[x, y] = 5  # Default to dark gray
    
    # Save as PNG
    indexed_img.save(output_file, 'PNG')
    print(f"✅ Converted {input_file} -> {output_file}")
    print(f"   Size: {width}x{height}, 16-color indexed with black transparency")

# Convert the files
if __name__ == "__main__":
    files_to_convert = [
        ('assets/tiles/overlay/cars_horizontal.png', 'assets/tiles/overlay/cars_horizontal_16color.png'),
        ('assets/tiles/overlay/cars_vertical.png', 'assets/tiles/overlay/cars_vertical_16color.png')
    ]
    
    for input_file, output_file in files_to_convert:
        if os.path.exists(input_file):
            convert_to_16color(input_file, output_file)
        else:
            print(f"❌ File not found: {input_file}")