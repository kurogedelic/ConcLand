#!/usr/bin/env python3
"""
Fix for large tiles - split them into 8x8 chunks for Pyxel
"""

from PIL import Image
import os

def split_large_png(input_path, output_dir, tile_size=8):
    """Split a large PNG into 8x8 tiles"""
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Open the image
    img = Image.open(input_path)
    width, height = img.size
    
    print(f"Splitting {input_path}: {width}x{height}")
    
    # Calculate number of tiles
    tiles_x = width // tile_size
    tiles_y = height // tile_size
    
    # Extract base name
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    
    # Split into tiles
    for y in range(tiles_y):
        for x in range(tiles_x):
            # Crop the tile
            left = x * tile_size
            top = y * tile_size
            right = left + tile_size
            bottom = top + tile_size
            
            tile = img.crop((left, top, right, bottom))
            
            # Save the tile
            output_path = os.path.join(output_dir, f"{base_name}_{y}_{x}.png")
            tile.save(output_path)
            print(f"  Saved tile ({x},{y}) to {output_path}")

# Process the large tiles
large_tiles = [
    ('assets/tiles/power/coal.png', 'assets/tiles/power/coal_split'),
    ('assets/tiles/power/nuclear.png', 'assets/tiles/power/nuclear_split'),
    ('assets/tiles/public/police.png', 'assets/tiles/public/police_split'),
    ('assets/tiles/public/fire.png', 'assets/tiles/public/fire_split'),
    ('assets/tiles/public/hospital.png', 'assets/tiles/public/hospital_split'),
]

for input_file, output_dir in large_tiles:
    if os.path.exists(input_file):
        split_large_png(input_file, output_dir)
    else:
        print(f"File not found: {input_file}")

print("\nDone! Large tiles have been split into 8x8 chunks.")