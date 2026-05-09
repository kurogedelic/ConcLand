#!/usr/bin/env python3
"""Test Pyxel's image loading directly"""

import pyxel

pyxel.init(320, 240)

print("\n=== Testing Pyxel Image Loading ===")

# Clear image bank 1
pyxel.images[1].cls(0)

# Load coal.png at (0,0)
print("\n1. Loading coal.png (32x32) at position (0,0)")
pyxel.images[1].load(0, 0, "assets/tiles/power/coal.png")

# Check what got loaded
print("\nChecking loaded pixels:")
# Sample corners and center of expected 32x32 area
test_points = [
    (0, 0, "Top-left"),
    (7, 0, "Top-right of 8x8"),
    (8, 0, "Beyond 8x8 horizontally"),
    (0, 8, "Beyond 8x8 vertically"),
    (8, 8, "Beyond 8x8 both"),
    (15, 15, "Center of 32x32"),
    (31, 31, "Bottom-right of 32x32")
]

for x, y, label in test_points:
    color = pyxel.images[1].pget(x, y)
    print(f"  ({x:2d},{y:2d}) {label:25s}: color={color}")

# Count non-zero pixels in different areas
areas = [
    (8, 8, "8x8"),
    (16, 16, "16x16"),
    (24, 24, "24x24"),
    (32, 32, "32x32")
]

print("\nNon-zero pixel counts:")
for w, h, label in areas:
    count = 0
    for y in range(min(h, 256)):
        for x in range(min(w, 256)):
            if pyxel.images[1].pget(x, y) != 0:
                count += 1
    total = w * h
    print(f"  {label:5s} area: {count}/{total} pixels ({count*100//total}%)")

# Test loading at different position
print("\n2. Loading coal.png at position (100,100)")
pyxel.images[1].load(100, 100, "assets/tiles/power/coal.png")

# Check that position
count_at_100 = 0
for y in range(32):
    for x in range(32):
        if pyxel.images[1].pget(100+x, 100+y) != 0:
            count_at_100 += 1
print(f"  Non-zero pixels at (100,100): {count_at_100}/1024")

# Test loading smaller image
print("\n3. Loading grass.png (8x8) at position (50,50)")
pyxel.images[1].load(50, 50, "assets/tiles/terrain/grass.png")

count_grass = 0
for y in range(8):
    for x in range(8):
        if pyxel.images[1].pget(50+x, 50+y) != 0:
            count_grass += 1
print(f"  Non-zero pixels at (50,50): {count_grass}/64")

def update():
    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

def draw():
    pyxel.cls(0)
    
    pyxel.text(10, 10, "Pyxel Load Test", 7)
    
    # Draw what's at (0,0) with different sizes
    pyxel.text(10, 30, "8x8:", 7)
    pyxel.blt(10, 45, 1, 0, 0, 8, 8)
    pyxel.rectb(10, 45, 8, 8, 8)
    
    pyxel.text(50, 30, "16x16:", 7)
    pyxel.blt(50, 45, 1, 0, 0, 16, 16)
    pyxel.rectb(50, 45, 16, 16, 9)
    
    pyxel.text(100, 30, "32x32:", 7)
    pyxel.blt(100, 45, 1, 0, 0, 32, 32)
    pyxel.rectb(100, 45, 32, 32, 10)
    
    # Draw what's at (100,100)
    pyxel.text(150, 30, "From (100,100):", 7)
    pyxel.blt(150, 45, 1, 100, 100, 32, 32)
    pyxel.rectb(150, 45, 32, 32, 11)
    
    # Draw grass at (50,50)
    pyxel.text(200, 30, "Grass:", 7)
    pyxel.blt(200, 45, 1, 50, 50, 8, 8)
    pyxel.rectb(200, 45, 8, 8, 12)
    
    pyxel.text(10, 200, "Q to quit", 7)

pyxel.run(update, draw)