#!/usr/bin/env python3
"""Direct test of Pyxel image loading and blt"""

import pyxel

# Initialize Pyxel
pyxel.init(320, 240)

# Load a 32x32 PNG directly
print("Loading coal.png...")
pyxel.images[0].load(10, 10, "assets/tiles/power/coal.png")

print("Loading nuclear.png...")
pyxel.images[0].load(50, 10, "assets/tiles/power/nuclear.png")

def update():
    if pyxel.btnp(pyxel.KEY_ESCAPE):
        pyxel.quit()

def draw():
    pyxel.cls(0)
    
    pyxel.text(10, 5, "Direct BLT Test", 7)
    
    # Test 1: Draw 8x8 from coal position
    pyxel.text(10, 60, "8x8:", 7)
    pyxel.blt(40, 60, 0, 10, 10, 8, 8)
    pyxel.rectb(40, 60, 8, 8, 8)
    
    # Test 2: Draw 32x32 from coal position  
    pyxel.text(10, 80, "32x32:", 7)
    pyxel.blt(40, 80, 0, 10, 10, 32, 32)
    pyxel.rectb(40, 80, 32, 32, 10)
    
    # Test 3: Draw 32x32 from nuclear position
    pyxel.text(10, 120, "Nuclear 32x32:", 7)
    pyxel.blt(80, 120, 0, 50, 10, 32, 32)
    pyxel.rectb(80, 120, 32, 32, 11)

pyxel.run(update, draw)