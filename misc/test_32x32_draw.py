#!/usr/bin/env python3
"""Test drawing 32x32 tiles"""

import pyxel
from individual_tile_system import IndividualTileSystem

class Test32x32:
    def __init__(self):
        pyxel.init(320, 240)
        self.tile_system = IndividualTileSystem()
        self.tile_system.initialize()
        pyxel.run(self.update, self.draw)
    
    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
    
    def draw(self):
        pyxel.cls(0)
        
        # Draw title
        pyxel.text(10, 10, "32x32 Tile Test", 7)
        
        # Test drawing coal plant at different positions
        pyxel.text(10, 30, "Coal Plant (should be 32x32):", 7)
        
        # Method 1: Using our draw_tile function
        self.tile_system.draw_tile('coal_plant', 10, 50)
        
        # Method 2: Direct blt with known values
        if 'coal_plant' in self.tile_system.loaded_tiles:
            bank, x, y, w, h = self.tile_system.loaded_tiles['coal_plant']
            pyxel.text(10, 90, f"Direct blt: bank={bank}, pos=({x},{y}), size={w}x{h}", 7)
            pyxel.blt(10, 100, bank, x, y, w, h)
            
            # Draw a red border to show expected size
            pyxel.rectb(10, 100, 32, 32, 8)
        
        # Also test an 8x8 tile for comparison
        pyxel.text(60, 30, "8x8 Road tile:", 7)
        self.tile_system.draw_tile('road_horizontal', 60, 50)
        pyxel.rectb(60, 50, 8, 8, 11)
        
        pyxel.text(10, 200, "Press Q to quit", 7)

if __name__ == "__main__":
    Test32x32()