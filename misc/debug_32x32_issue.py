#!/usr/bin/env python3
"""Debug why 32x32 only shows 8x8"""

import pyxel

pyxel.init(320, 240)

# Test 1: Load and draw directly
print("Test 1: Direct load and draw")
pyxel.images[1].load(0, 0, "assets/tiles/power/coal.png")

# Check what actually got loaded
print("Checking loaded pixels in bank 1 at (0,0)...")
non_zero = 0
for y in range(32):
    for x in range(32):
        if pyxel.images[1].pget(x, y) != 0:
            non_zero += 1

print(f"Non-zero pixels: {non_zero}/1024")

# Test drawing
def update():
    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

def draw():
    pyxel.cls(0)
    
    # Try different drawing methods
    pyxel.text(10, 10, "32x32 Drawing Debug", 7)
    
    # Method 1: Standard blt with 32x32
    pyxel.text(10, 30, "blt(10,50,1,0,0,32,32):", 7)
    pyxel.blt(10, 50, 1, 0, 0, 32, 32)
    pyxel.rectb(10, 50, 32, 32, 8)
    
    # Method 2: Draw in parts
    pyxel.text(50, 30, "4 parts:", 7)
    pyxel.blt(50, 50, 1, 0, 0, 16, 16)  # Top-left
    pyxel.blt(66, 50, 1, 16, 0, 16, 16)  # Top-right
    pyxel.blt(50, 66, 1, 0, 16, 16, 16)  # Bottom-left
    pyxel.blt(66, 66, 1, 16, 16, 16, 16)  # Bottom-right
    pyxel.rectb(50, 50, 32, 32, 11)
    
    # Method 3: Using wrong size on purpose
    pyxel.text(90, 30, "8x8 only:", 7)
    pyxel.blt(90, 50, 1, 0, 0, 8, 8)
    pyxel.rectb(90, 50, 8, 8, 12)
    
    # Show actual pixel data
    pyxel.text(10, 100, f"Pixels at (0,0): {pyxel.images[1].pget(0,0)}", 7)
    pyxel.text(10, 110, f"Pixels at (31,31): {pyxel.images[1].pget(31,31)}", 7)
    
    pyxel.text(10, 200, "Q to quit", 7)

pyxel.run(update, draw)