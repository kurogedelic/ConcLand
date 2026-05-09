#!/usr/bin/env python3
"""
Simple PNG viewer to confirm tiles are visible
"""

import pyxel

def view_png():
    pyxel.init(320, 240, title="Tile Viewer")
    
    # Load the PNG
    try:
        pyxel.images[0].load(0, 0, "assets/concland_tiles_16x16.png")
        print("PNG loaded successfully")
    except Exception as e:
        print(f"Failed to load PNG: {e}")
        return
    
    def update():
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
    
    def draw():
        pyxel.cls(0)
        
        # Draw the entire tilemap scaled down
        pyxel.blt(10, 10, 0, 0, 0, 256, 256, 0)  # Full tilemap
        
        # Draw individual tiles at actual size
        x, y = 10, 270
        
        # Row 0: Basic terrain
        pyxel.blt(x, y, 0, 0, 0, 16, 16, 0)      # Empty (should be dark)
        pyxel.blt(x+20, y, 0, 16, 0, 16, 16, 0)  # Grass (should be green)
        pyxel.blt(x+40, y, 0, 32, 0, 16, 16, 0)  # Water (should be blue)
        
        # Row 4: Roads  
        pyxel.blt(x+80, y, 0, 16, 64, 16, 16, 0)  # Horizontal road
        pyxel.blt(x+100, y, 0, 32, 64, 16, 16, 0) # Vertical road
        pyxel.blt(x+120, y, 0, 112, 64, 16, 16, 0) # Cross road
        
        pyxel.text(10, 280, "Full tilemap above, individual tiles below", 7)
        pyxel.text(10, 290, "Press Q to quit", 7)
    
    pyxel.run(update, draw)

if __name__ == "__main__":
    view_png()