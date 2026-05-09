#!/usr/bin/env python3
"""
Convert RGBA PNG to Pyxel-compatible format
"""

from PIL import Image
import numpy as np

def convert_to_pyxel_format():
    """Convert RGBA PNG to Pyxel's expected format"""
    
    # Load the original PNG
    img = Image.open('assets/concland_tiles_16x16.png')
    print(f"Original: {img.size}, {img.mode}")
    
    # Convert to RGB (remove alpha)
    if img.mode == 'RGBA':
        # Create a white background
        background = Image.new('RGB', img.size, (0, 0, 0))  # Black background
        background.paste(img, mask=img.split()[-1])  # Use alpha as mask
        img = background
    
    # Convert to Pyxel's 16-color palette
    # Pyxel default colors (approximation)
    pyxel_colors = [
        (0, 0, 0),       # 0: Black
        (29, 43, 83),    # 1: Dark Blue  
        (126, 37, 83),   # 2: Dark Purple
        (0, 135, 81),    # 3: Dark Green
        (171, 82, 54),   # 4: Brown
        (95, 87, 79),    # 5: Dark Gray
        (194, 195, 199), # 6: Light Gray
        (255, 241, 232), # 7: White
        (255, 0, 77),    # 8: Red
        (255, 163, 0),   # 9: Orange
        (255, 236, 39),  # 10: Yellow
        (0, 228, 54),    # 11: Green
        (41, 173, 255),  # 12: Blue
        (131, 118, 156), # 13: Indigo
        (255, 119, 168), # 14: Pink
        (255, 204, 170)  # 15: Peach
    ]
    
    # Create palette image
    palette_img = Image.new('P', (1, 1))
    palette = []
    for color in pyxel_colors:
        palette.extend(color)
    # Pad to 256 colors
    palette.extend([0, 0, 0] * (256 - len(pyxel_colors)))
    palette_img.putpalette(palette)
    
    # Convert image to use this palette
    img_p = img.quantize(palette=palette_img, dither=Image.NONE)
    
    # Save as indexed PNG
    output_path = 'assets/concland_tiles_indexed.png'
    img_p.save(output_path)
    print(f"Converted to indexed PNG: {output_path}")
    
    # Also save as simple RGB
    img_rgb = img.convert('RGB')
    output_rgb_path = 'assets/concland_tiles_rgb.png'
    img_rgb.save(output_rgb_path)
    print(f"Converted to RGB PNG: {output_rgb_path}")
    
    return output_path, output_rgb_path

if __name__ == "__main__":
    convert_to_pyxel_format()