#!/usr/bin/env python3
"""Test if 32x32 sprites are loading correctly"""

import pyxel

class TestSpriteLoading:
    def __init__(self):
        pyxel.init(320, 240)
        
        # Test loading coal.png directly
        print("\n=== Testing Sprite Loading ===")
        
        # Load coal.png at different positions
        pyxel.images[1].load(0, 0, "assets/tiles/power/coal.png")
        print("Loaded coal.png to bank 1 at (0,0)")
        
        # Check what actually got loaded
        print("\nChecking pixels in bank 1:")
        non_zero_8x8 = 0
        non_zero_32x32 = 0
        
        # Check 8x8 area
        for y in range(8):
            for x in range(8):
                if pyxel.images[1].pget(x, y) != 0:
                    non_zero_8x8 += 1
        
        # Check 32x32 area
        for y in range(32):
            for x in range(32):
                if pyxel.images[1].pget(x, y) != 0:
                    non_zero_32x32 += 1
        
        print(f"Non-zero pixels in 8x8 area: {non_zero_8x8}/64")
        print(f"Non-zero pixels in 32x32 area: {non_zero_32x32}/1024")
        
        if non_zero_32x32 > non_zero_8x8:
            print("✓ Full 32x32 sprite is loaded")
        else:
            print("✗ Only 8x8 portion is loaded")
        
        pyxel.run(self.update, self.draw)
    
    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
    
    def draw(self):
        pyxel.cls(0)
        
        pyxel.text(10, 10, "Sprite Loading Test", 7)
        
        # Test 1: Draw with 8x8
        pyxel.text(10, 30, "blt 8x8:", 7)
        pyxel.blt(10, 50, 1, 0, 0, 8, 8)
        pyxel.rectb(10, 50, 8, 8, 8)
        
        # Test 2: Draw with 32x32
        pyxel.text(60, 30, "blt 32x32:", 7)
        pyxel.blt(60, 50, 1, 0, 0, 32, 32)
        pyxel.rectb(60, 50, 32, 32, 11)
        
        # Test 3: Draw 4 times 8x8 to reconstruct
        pyxel.text(120, 30, "4x 8x8 tiles:", 7)
        for dy in range(4):
            for dx in range(4):
                pyxel.blt(120 + dx*8, 50 + dy*8, 1, dx*8, dy*8, 8, 8)
        pyxel.rectb(120, 50, 32, 32, 14)
        
        # Test 4: Direct pixel check
        pyxel.text(10, 100, "Pixel colors at key positions:", 7)
        positions = [(0,0), (7,7), (8,8), (15,15), (31,31)]
        y_offset = 115
        for px, py in positions:
            color = pyxel.images[1].pget(px, py)
            pyxel.text(10, y_offset, f"({px},{py}): color {color}", 7)
            y_offset += 10
        
        pyxel.text(10, 200, "Q to quit", 7)

if __name__ == "__main__":
    TestSpriteLoading()