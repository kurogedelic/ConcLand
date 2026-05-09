#!/usr/bin/env python3
"""Convert car overlay images to indexed color with magenta transparency"""

from PIL import Image
import os

def convert_to_indexed_with_transparency(input_file, output_file):
    """Convert image to indexed color with magenta (255,0,255) as transparent at index 255"""
    
    # Load the image
    img = Image.open(input_file)
    
    # If already indexed, convert to RGBA first to process
    if img.mode == 'P':
        img = img.convert('RGBA')
    
    # Create new indexed image
    width, height = img.size
    indexed_img = Image.new('P', (width, height))
    
    # Create a palette with 256 colors
    # Use a simple palette, reserving index 255 for magenta
    palette = []
    
    # Add some basic colors (0-254)
    for i in range(255):
        if i < 16:  # First 16 colors - basic palette
            r = (i & 1) * 255
            g = ((i >> 1) & 1) * 255
            b = ((i >> 2) & 1) * 255
            palette.extend([r, g, b])
        else:
            # Grayscale for the rest
            gray = (i - 16) * 255 // 238
            palette.extend([gray, gray, gray])
    
    # Index 255 is magenta (transparent)
    palette.extend([255, 0, 255])
    
    # Apply palette
    indexed_img.putpalette(palette)
    
    # Process pixels
    pixels = indexed_img.load()
    img_pixels = img.load()
    
    for y in range(height):
        for x in range(width):
            if img.mode == 'RGBA':
                r, g, b, a = img_pixels[x, y]
            else:
                r, g, b = img_pixels[x, y][:3]
                a = 255
            
            # Check if it's magenta
            if r > 250 and g < 5 and b > 250:
                pixels[x, y] = 255  # Transparent
            elif r < 50 and g < 50 and b < 50:
                pixels[x, y] = 0  # Black
            elif r > 200 and g > 200 and b > 200:
                pixels[x, y] = 15  # White
            elif r > 100 and g > 100 and b > 100:
                pixels[x, y] = 7  # Gray
            elif r > 200 and g < 100 and b < 100:
                pixels[x, y] = 8  # Red
            elif r < 100 and g > 200 and b < 100:
                pixels[x, y] = 10  # Green
            elif r < 100 and g < 100 and b > 200:
                pixels[x, y] = 12  # Blue
            elif r > 200 and g > 200 and b < 100:
                pixels[x, y] = 14  # Yellow
            else:
                # Find closest color
                pixels[x, y] = 7  # Default to gray
    
    # Save with transparency
    indexed_img.info['transparency'] = 255
    indexed_img.save(output_file, 'PNG', transparency=255)
    print(f"✅ Converted {input_file} -> {output_file}")
    print(f"   Size: {width}x{height}, Transparent index: 255")

# Convert the files
if __name__ == "__main__":
    files_to_convert = [
        ('assets/tiles/overlay/cars_horizontal.png', 'assets/tiles/overlay/cars_horizontal_indexed.png'),
        ('assets/tiles/overlay/cars_vertical.png', 'assets/tiles/overlay/cars_vertical_indexed.png')
    ]
    
    for input_file, output_file in files_to_convert:
        if os.path.exists(input_file):
            convert_to_indexed_with_transparency(input_file, output_file)
        else:
            print(f"❌ File not found: {input_file}")