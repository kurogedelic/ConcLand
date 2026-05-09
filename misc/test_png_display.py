#!/usr/bin/env python3
"""
Test PNG tile display
"""

import pyxel
import os
from concland_tile_system import ConcLandTileManager

class PNGTest:
    def __init__(self):
        pyxel.init(320, 240, title="PNG Test")
        
        # Initialize tile manager
        self.tile_manager = ConcLandTileManager()
        
        # Try to load tilemap
        if os.path.exists('assets/concland_tiles_16x16.png'):
            success = self.tile_manager.load_tilemap('assets/concland_tiles_16x16.png')
            print(f"Tilemap loading: {'SUCCESS' if success else 'FAILED'}")
        else:
            print("Tilemap file not found!")
            
        pyxel.run(self.update, self.draw)
    
    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
    
    def draw(self):
        pyxel.cls(1)  # Dark blue background
        
        # Draw test tiles
        x, y = 10, 10
        
        # Test basic tiles
        self.tile_manager.draw_tile(x, y, 'grass')
        self.tile_manager.draw_tile(x + 20, y, 'water')
        self.tile_manager.draw_tile(x + 40, y, 'road_horizontal')
        self.tile_manager.draw_tile(x + 60, y, 'road_vertical')
        self.tile_manager.draw_tile(x + 80, y, 'road_cross')
        
        # Test building tiles
        self.tile_manager.draw_tile(x, y + 20, 'residential_1')
        self.tile_manager.draw_tile(x + 20, y + 20, 'commercial_1')
        self.tile_manager.draw_tile(x + 40, y + 20, 'industrial_1')
        
        # Test if tiles exist in the tile system
        pyxel.text(10, 60, "Tiles in system:", 7)
        tile_count = len(self.tile_manager.tiles)
        pyxel.text(10, 70, f"Total tiles: {tile_count}", 7)
        
        # Show some tile names
        y_pos = 80
        for i, tile_name in enumerate(list(self.tile_manager.tiles.keys())[:10]):
            pyxel.text(10, y_pos + i * 8, tile_name, 7)

if __name__ == "__main__":
    PNGTest()