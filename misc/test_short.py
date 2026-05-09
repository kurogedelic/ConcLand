#!/usr/bin/env python3
"""
Short test of ConcLand Mini to check if PNG loading works
"""

import pyxel
import os
from concland_tile_system import ConcLandTileManager

# Test just the tile loading
def test_loading():
    print("=== PNG Loading Test ===")
    
    # Initialize pyxel first
    pyxel.init(160, 144)
    
    # Create tile manager
    tile_manager = ConcLandTileManager()
    print(f"Tile manager created with {len(tile_manager.tiles)} tiles")
    
    # Test loading
    tilemap_paths = [
        'assets/concland_tiles_16x16.png',
        'assets/tiles_16x16.png',
        'assets/tilemap_generated.png'
    ]
    
    use_graphics = False
    for path in tilemap_paths:
        if os.path.exists(path):
            print(f"Trying to load: {path}")
            try:
                if tile_manager.load_tilemap(path):
                    use_graphics = True
                    print(f"SUCCESS: Loaded tilemap: {path}")
                    break
                else:
                    print(f"FAILED: Could not load {path}")
            except Exception as e:
                print(f"ERROR loading {path}: {e}")
    
    if not use_graphics:
        print("WARNING: Could not load any tile graphics")
    else:
        print("SUCCESS: Graphics loaded!")
        
        # Test drawing a single tile
        pyxel.cls(1)
        tile_manager.draw_tile(10, 10, 'grass')
        tile_manager.draw_tile(30, 10, 'road_horizontal')
        pyxel.show()  # Show static frame
        
    print("Test complete.")

if __name__ == "__main__":
    test_loading()