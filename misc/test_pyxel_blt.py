#!/usr/bin/env python3
"""Simple test of Pyxel's image loading and blt"""

import pyxel

class SimpleTest:
    def __init__(self):
        pyxel.init(320, 240, title="Pyxel BLT Test")
        
        # Load images directly
        print("Loading coal.png at (0,0)")
        pyxel.images[0].load(0, 0, "assets/tiles/power/coal.png")
        
        print("Loading nuclear.png at (40,0)")
        pyxel.images[0].load(40, 0, "assets/tiles/power/nuclear.png")
        
        print("Loading police.png at (80,0)")
        pyxel.images[0].load(80, 0, "assets/tiles/public/police.png")
        
        pyxel.run(self.update, self.draw)
    
    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
    
    def draw(self):
        pyxel.cls(0)
        
        # Test 1: Draw with explicit size
        pyxel.text(10, 10, "Test 1: Explicit sizes", 7)
        
        # Coal - try different sizes
        y = 30
        pyxel.text(10, y, "Coal:", 7)
        
        # 8x8
        pyxel.blt(50, y, 0, 0, 0, 8, 8)
        pyxel.rectb(50, y, 8, 8, 8)
        pyxel.text(50, y+10, "8x8", 6)
        
        # 16x16
        pyxel.blt(70, y, 0, 0, 0, 16, 16)
        pyxel.rectb(70, y, 16, 16, 9)
        pyxel.text(70, y+18, "16x16", 6)
        
        # 32x32
        pyxel.blt(100, y, 0, 0, 0, 32, 32)
        pyxel.rectb(100, y, 32, 32, 10)
        pyxel.text(100, y+34, "32x32", 6)
        
        # Test 2: What happens with negative width/height (auto-detect)
        y = 80
        pyxel.text(10, y, "Test 2: Auto size (-w, -h)", 7)
        
        # Coal with auto size
        pyxel.blt(50, y, 0, 0, 0, -32, -32)
        pyxel.rectb(50, y, 32, 32, 11)
        
        # Test 3: Nuclear
        y = 130
        pyxel.text(10, y, "Nuclear:", 7)
        pyxel.blt(50, y, 0, 40, 0, 32, 32)
        pyxel.rectb(50, y, 32, 32, 12)
        
        # Test 4: Police (24x24)
        y = 170
        pyxel.text(10, y, "Police:", 7)
        pyxel.blt(50, y, 0, 80, 0, 24, 24)
        pyxel.rectb(50, y, 24, 24, 13)
        
        pyxel.text(10, 220, "ESC to exit", 7)

if __name__ == "__main__":
    test = SimpleTest()