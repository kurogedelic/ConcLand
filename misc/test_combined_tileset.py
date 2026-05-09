#!/usr/bin/env python3
"""Test combined tileset"""

import pyxel

pyxel.init(320, 240)

# Load the entire tileset at once
print("Loading combined tileset...")
pyxel.images[0].load(0, 0, "assets/combined_tileset.png")

def update():
    if pyxel.btnp(pyxel.KEY_ESCAPE):
        pyxel.quit()

def draw():
    pyxel.cls(0)
    
    pyxel.text(10, 10, "Combined Tileset Test", 7)
    
    # Draw coal plant (32x32 at 0,0 in tileset)
    pyxel.text(10, 30, "Coal (32x32):", 7)
    pyxel.blt(10, 40, 0, 0, 0, 32, 32)
    pyxel.rectb(10, 40, 32, 32, 10)
    
    # Draw nuclear (32x32 at 32,0 in tileset)
    pyxel.text(50, 30, "Nuclear (32x32):", 7)
    pyxel.blt(50, 40, 0, 32, 0, 32, 32)
    pyxel.rectb(50, 40, 32, 32, 11)
    
    # Draw police (24x24 at 64,0 in tileset)
    pyxel.text(90, 30, "Police (24x24):", 7)
    pyxel.blt(90, 40, 0, 64, 0, 24, 24)
    pyxel.rectb(90, 40, 24, 24, 12)
    
    pyxel.text(10, 220, "If images show correctly, the issue is with individual tile loading", 7)

pyxel.run(update, draw)