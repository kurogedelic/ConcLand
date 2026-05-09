#!/usr/bin/env python3
"""Test program to debug large tile loading and display"""

import pyxel
from individual_tile_system import IndividualTileSystem

class LargeTileTest:
    def __init__(self):
        self.tile_system = IndividualTileSystem()
        
    def run(self):
        pyxel.init(320, 288, title="Large Tile Debug Test")
        
        # Initialize tile system
        self.tile_system.initialize()
        
        pyxel.run(self.update, self.draw)
    
    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
    
    def draw(self):
        pyxel.cls(0)
        
        # Title
        pyxel.text(10, 10, "Large Tile Debug Test", 7)
        
        # Test drawing large tiles
        test_tiles = [
            ('coal_plant', 10, 40, "Coal Plant (32x32)"),
            ('nuclear_plant', 50, 40, "Nuclear (32x32)"),
            ('police', 90, 40, "Police (24x24)"),
            ('fire', 120, 40, "Fire (24x24)"),
            ('hospital', 150, 40, "Hospital (24x24)")
        ]
        
        for tile_id, x, y, label in test_tiles:
            # Draw tile
            print(f"Drawing {tile_id} at ({x},{y})")
            self.tile_system.draw_tile(tile_id, x, y)
            
            # Draw border to show expected size
            if tile_id in self.tile_system.large_tiles:
                size = self.tile_system.large_tiles[tile_id]
                pyxel.rectb(x, y, size, size, 14)  # Pink border
                print(f"  Expected size: {size}x{size}")
                
            # Label
            pyxel.text(x, y + 40, label[:8], 7)
            
            # Show tile info if loaded
            if tile_id in self.tile_system.loaded_tiles:
                info = self.tile_system.loaded_tiles[tile_id]
                if len(info) == 5:
                    bank, src_x, src_y, w, h = info
                    pyxel.text(x, y + 48, f"B{bank} {w}x{h}", 6)
        
        # Instructions
        pyxel.text(10, 260, "Pink borders show expected sizes", 14)
        pyxel.text(10, 270, "ESC to exit", 7)

if __name__ == "__main__":
    test = LargeTileTest()
    test.run()