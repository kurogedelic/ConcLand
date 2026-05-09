#!/usr/bin/env python3
"""
Most basic PNG test - just load and draw raw PNG data
"""

import pyxel

def basic_test():
    pyxel.init(320, 240, title="Basic PNG Test")
    
    # Load PNG into image bank 0
    try:
        print("Loading PNG...")
        pyxel.images[0].load(0, 0, "assets/concland_tiles_16x16.png")
        print("PNG loaded successfully")
        
        # Check if the image bank has data by trying to get pixel colors
        print("Checking image bank 0 data...")
        for y in range(5):
            for x in range(5):
                try:
                    pixel = pyxel.images[0].pget(x, y)
                    print(f"Pixel at ({x},{y}): {pixel}")
                    if pixel != 0:
                        print(f"Found non-zero pixel: {pixel} at ({x},{y})")
                        break
                except:
                    print(f"Error reading pixel at ({x},{y})")
            if pixel != 0:
                break
                
    except Exception as e:
        print(f"Error loading PNG: {e}")
        return
    
    def update():
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
    
    def draw():
        pyxel.cls(1)  # Dark blue background
        
        # Test 1: Draw entire loaded image (small)
        pyxel.blt(10, 10, 0, 0, 0, 64, 64, 0)  # Show 64x64 portion
        
        # Test 2: Draw specific tiles with different transparency
        pyxel.blt(100, 10, 0, 0, 0, 16, 16, 0)    # No transparency
        pyxel.blt(120, 10, 0, 16, 0, 16, 16, -1)  # All colors
        pyxel.blt(140, 10, 0, 32, 0, 16, 16, 1)   # Transparency color 1
        
        # Test 3: Draw with scaling
        pyxel.blt(100, 40, 0, 0, 0, 32, 32, 0)    # 2x scale by drawing 32x32
        
        # Labels
        pyxel.text(10, 80, "64x64 portion of PNG", 7)
        pyxel.text(100, 80, "Individual 16x16 tiles", 7)  
        pyxel.text(100, 110, "Scaled tile", 7)
        pyxel.text(10, 200, "Press Q to quit", 7)

    pyxel.run(update, draw)

if __name__ == "__main__":
    basic_test()