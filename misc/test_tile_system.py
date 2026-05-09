#!/usr/bin/env python3
"""Test tile system loading and drawing"""

import pyxel
from individual_tile_system import IndividualTileSystem

def main():
    pyxel.init(320, 240)
    
    # Initialize tile system
    tile_system = IndividualTileSystem()
    tile_system.initialize()
    
    frame_count = 0
    
    def update():
        nonlocal frame_count
        frame_count += 1
        
        if pyxel.btnp(pyxel.KEY_ESCAPE) or frame_count > 60:
            pyxel.quit()
    
    def draw():
        pyxel.cls(0)
        
        # Try to draw a coal plant
        print(f"\n=== Frame {frame_count} ===")
        print("Drawing coal_plant at (10, 10)")
        tile_system.draw_tile('coal_plant', 10, 10)
        
        # Draw border to show expected size
        pyxel.rectb(10, 10, 32, 32, 8)  # Red border for expected size
        
        pyxel.text(10, 50, "Coal Plant Test", 7)
        pyxel.text(10, 60, "Red box = expected 32x32", 8)
    
    pyxel.run(update, draw)

if __name__ == "__main__":
    main()