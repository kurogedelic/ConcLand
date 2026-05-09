#!/usr/bin/env python3
"""Direct test of 32x32 drawing without tile system"""

import pyxel

class DirectTest:
    def __init__(self):
        pyxel.init(320, 240)
        
        # Load coal.png directly at position 0,0 in bank 1
        pyxel.images[1].load(0, 0, "assets/tiles/power/coal.png")
        
        # Load it again at 100,100 for comparison
        pyxel.images[1].load(100, 100, "assets/tiles/power/coal.png")
        
        pyxel.run(self.update, self.draw)
    
    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
    
    def draw(self):
        pyxel.cls(0)
        
        pyxel.text(10, 10, "Direct 32x32 Test", 7)
        
        # Test 1: Draw with explicit 32x32 size
        pyxel.text(10, 30, "blt with 32x32:", 7)
        pyxel.blt(10, 50, 1, 0, 0, 32, 32)
        pyxel.rectb(10, 50, 32, 32, 8)  # Red border to show expected size
        
        # Test 2: Draw with 8x8 size for comparison
        pyxel.text(60, 30, "blt with 8x8:", 7)
        pyxel.blt(60, 50, 1, 0, 0, 8, 8)
        pyxel.rectb(60, 50, 8, 8, 11)  # Green border
        
        # Test 3: Draw from second position
        pyxel.text(100, 30, "From (100,100):", 7)
        pyxel.blt(100, 50, 1, 100, 100, 32, 32)
        pyxel.rectb(100, 50, 32, 32, 12)  # Blue border
        
        # Test 4: Draw in 4 separate 8x8 chunks
        pyxel.text(150, 30, "4x 8x8 chunks:", 7)
        for dy in range(4):
            for dx in range(4):
                pyxel.blt(150 + dx*8, 50 + dy*8, 1, dx*8, dy*8, 8, 8)
        pyxel.rectb(150, 50, 32, 32, 14)  # Pink border
        
        pyxel.text(10, 200, "Q to quit", 7)

if __name__ == "__main__":
    DirectTest()