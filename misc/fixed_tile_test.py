#!/usr/bin/env python3
"""
Test proper PNG loading with Pyxel
"""

import pyxel
import os

def test_pyxel_png():
    pyxel.init(320, 240, title="PNG Test")
    
    # Test different loading methods
    print("Testing PNG loading methods...")
    
    # Method 1: Direct image load
    try:
        pyxel.images[0].load(0, 0, "assets/concland_tiles_16x16.png")
        print("SUCCESS: Direct image load worked")
        loaded = True
    except Exception as e:
        print(f"FAILED: Direct image load: {e}")
        loaded = False
    
    if loaded:
        # Test drawing
        def update():
            if pyxel.btnp(pyxel.KEY_Q):
                pyxel.quit()
        
        def draw():
            pyxel.cls(1)
            
            # Draw some tiles directly from loaded image
            # Grass tile at (16, 0)
            pyxel.blt(10, 10, 0, 16, 0, 16, 16, 0)
            
            # Water tile at (32, 0)  
            pyxel.blt(30, 10, 0, 32, 0, 16, 16, 0)
            
            # Road horizontal at (16, 64)
            pyxel.blt(50, 10, 0, 16, 64, 16, 16, 0)
            
            # Road vertical at (32, 64)
            pyxel.blt(70, 10, 0, 32, 64, 16, 16, 0)
            
            pyxel.text(10, 50, "PNG tiles loaded - Press Q to quit", 7)
        
        pyxel.run(update, draw)
    else:
        print("Could not load PNG")

if __name__ == "__main__":
    test_pyxel_png()