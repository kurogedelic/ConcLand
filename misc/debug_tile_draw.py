#!/usr/bin/env python3
"""
Debug tile drawing in ConcLand Mini style
"""

import pyxel
import os
from concland_tile_system import ConcLandTileManager

def debug_tile_drawing():
    pyxel.init(320, 288, title="Tile Draw Debug")
    
    # Initialize tile manager exactly like ConcLand Mini
    tile_manager = ConcLandTileManager()
    use_graphics = False
    
    # Try to load tilemap
    tilemap_paths = [
        'assets/concland_tiles_16x16.png',
        'assets/tiles_16x16.png',
        'assets/tilemap_generated.png'
    ]
    
    for path in tilemap_paths:
        if os.path.exists(path):
            try:
                if tile_manager.load_tilemap(path):
                    use_graphics = True
                    print(f"SUCCESS: Loaded tilemap: {path}")
                    break
            except Exception as e:
                print(f"ERROR loading {path}: {e}")
    
    print(f"Graphics enabled: {use_graphics}")
    print(f"Available tiles: {list(tile_manager.tiles.keys())[:10]}")
    
    def update():
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
    
    def draw():
        pyxel.cls(0)  # Black background like ConcLand Mini
        
        if use_graphics:
            # Test the exact same drawing logic as ConcLand Mini
            screen_x, screen_y = 10, 10
            
            # Test with correct parameter order: tile_id, x, y
            print("Drawing grass tile...")
            tile_manager.draw_tile('grass', screen_x, screen_y)
            
            # Test 2: Draw water
            tile_manager.draw_tile('water', screen_x + 20, screen_y)
            
            # Test 3: Draw road horizontal  
            tile_manager.draw_tile('road_horizontal', screen_x + 40, screen_y)
            
            # Test 4: Draw residential building
            tile_manager.draw_tile('residential_1', screen_x, screen_y + 20)
            
            # Test 5: Direct pyxel.blt call (bypass tile_manager)
            print("Drawing direct pyxel.blt calls...")
            pyxel.blt(screen_x + 20, screen_y + 20, 0, 16, 0, 16, 16, 0)  # Direct grass
            pyxel.blt(screen_x + 40, screen_y + 20, 0, 16, 64, 16, 16, 0)  # Direct road
            
            # Test 6: Check if image bank 0 has data
            print("Testing image bank 0 existence...")
            # Try to draw from different positions in the image bank
            for i in range(4):
                pyxel.blt(screen_x + i*20, screen_y + 40, 0, i*16, 0, 16, 16, 0)
            
            pyxel.text(10, 50, "Using tile_manager.draw_tile():", 7)
            pyxel.text(10, 60, "Should see: grass, water, road, residential", 7)
            pyxel.text(10, 80, "Using direct pyxel.blt():", 7)
            pyxel.text(10, 90, "Should see: grass, road", 7)
            
        else:
            pyxel.text(10, 50, "Graphics NOT loaded!", 8)
        
        pyxel.text(10, 110, "Press Q to quit", 7)
    
    pyxel.run(update, draw)

if __name__ == "__main__":
    debug_tile_drawing()