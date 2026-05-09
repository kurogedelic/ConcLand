#!/usr/bin/env python3
"""Check what's actually loaded in the image bank"""

import pyxel
from individual_tile_system import IndividualTileSystem

pyxel.init(320, 240)
tile_system = IndividualTileSystem()
tile_system.initialize()

# Check coal plant
if 'coal_plant' in tile_system.loaded_tiles:
    bank, x, y, w, h = tile_system.loaded_tiles['coal_plant']
    print(f"\nCoal plant stored info: bank={bank}, pos=({x},{y}), size={w}x{h}")
    
    # Check what's actually in the image bank at that position
    print(f"\nChecking pixels in bank {bank} at position ({x},{y}):")
    
    # Sample some pixels across the expected 32x32 area
    for dy in [0, 8, 16, 24, 31]:
        for dx in [0, 8, 16, 24, 31]:
            px = x + dx
            py = y + dy
            if px < 256 and py < 256:
                color = pyxel.images[bank].pget(px, py)
                if color != 0:  # Non-black pixel
                    print(f"  Pixel at ({px},{py}): color {color}")
    
    # Count non-zero pixels in the area
    non_zero_count = 0
    for dy in range(32):
        for dx in range(32):
            px = x + dx
            py = y + dy
            if px < 256 and py < 256:
                if pyxel.images[bank].pget(px, py) != 0:
                    non_zero_count += 1
    
    print(f"\nNon-zero pixels in 32x32 area: {non_zero_count} out of 1024")
    
    # Check if coal.png file is actually 32x32
    import os
    if os.path.exists('assets/tiles/power/coal.png'):
        print("\nCoal.png file exists")
        # Try loading it directly to a fresh position
        test_x, test_y = 100, 100
        pyxel.images[2].load(test_x, test_y, 'assets/tiles/power/coal.png')
        
        # Check what got loaded
        non_zero_test = 0
        for dy in range(32):
            for dx in range(32):
                if pyxel.images[2].pget(test_x + dx, test_y + dy) != 0:
                    non_zero_test += 1
        print(f"Test load at (100,100): {non_zero_test} non-zero pixels")