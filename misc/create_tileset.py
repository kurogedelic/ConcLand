#!/usr/bin/env python3
"""Create a proper tileset with large tiles included"""

from PIL import Image
import os

# Create a 256x256 tileset image
tileset = Image.new('RGBA', (256, 256), (0, 0, 0, 0))

# List of tiles to include with their positions
tiles_to_add = [
    # Row 0: Large power plants (32x32)
    ('assets/tiles/power/coal.png', 0, 0),      # Coal plant at (0,0)
    ('assets/tiles/power/nuclear.png', 32, 0),  # Nuclear at (32,0)
    ('assets/tiles/power/gas.png', 64, 0),      # Gas/Oil at (64,0) 
    
    # Row 1: Public buildings (24x24)
    ('assets/tiles/public/police.png', 0, 32),  # Police at (0,32)
    ('assets/tiles/public/fire.png', 24, 32),   # Fire at (24,32)
    ('assets/tiles/public/hospital.png', 48, 32), # Hospital at (48,32)
    
    # Keep all tiles organized
]

for file_path, x, y in tiles_to_add:
    if os.path.exists(file_path):
        img = Image.open(file_path)
        # Convert to RGBA if needed
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        tileset.paste(img, (x, y))
        print(f"Added {file_path} at ({x},{y}), size: {img.size}")
    else:
        print(f"File not found: {file_path}")

# Save the tileset
tileset.save('assets/combined_tileset.png')
print("\nSaved combined tileset to assets/combined_tileset.png")