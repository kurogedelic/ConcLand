#!/usr/bin/env python3
"""
Correct PNG loading test using pyxel.image().load()
"""

import pyxel
import os

def test_correct_png_loading():
    pyxel.init(320, 240, title="Correct PNG Test")
    
    # Test PNG loading with correct method
    png_files = [
        "assets/concland_tiles_16x16.png",
        "assets/tiles_16x16.png", 
        "assets/tilemap_generated.png"
    ]
    
    loaded_file = None
    for png_file in png_files:
        if os.path.exists(png_file):
            try:
                print(f"Attempting to load: {png_file}")
                pyxel.image(0).load(0, 0, png_file)
                print(f"SUCCESS: Loaded {png_file}")
                loaded_file = png_file
                break
            except Exception as e:
                print(f"FAILED to load {png_file}: {e}")
    
    if not loaded_file:
        print("No PNG file could be loaded!")
        return
    
    def update():
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
    
    def draw():
        pyxel.cls(1)  # Dark blue background
        
        if loaded_file:
            # Draw individual 16x16 tiles from the loaded tilemap
            
            # Row 0: Basic terrain (empty, grass, water)
            pyxel.blt(10, 10, 0, 0, 0, 16, 16, 0)    # Empty tile
            pyxel.blt(30, 10, 0, 16, 0, 16, 16, 0)   # Grass tile  
            pyxel.blt(50, 10, 0, 32, 0, 16, 16, 0)   # Water tile
            
            # Row 1: Residential buildings
            pyxel.blt(10, 30, 0, 0, 16, 16, 16, 0)   # Residential 1
            pyxel.blt(30, 30, 0, 16, 16, 16, 16, 0)  # Residential 2
            pyxel.blt(50, 30, 0, 32, 16, 16, 16, 0)  # Residential 3
            
            # Row 4: Roads
            pyxel.blt(10, 50, 0, 0, 64, 16, 16, 0)   # Road alone
            pyxel.blt(30, 50, 0, 16, 64, 16, 16, 0)  # Road horizontal
            pyxel.blt(50, 50, 0, 32, 64, 16, 16, 0)  # Road vertical
            pyxel.blt(70, 50, 0, 112, 64, 16, 16, 0) # Road cross
            
            pyxel.text(10, 80, f"Loaded: {loaded_file}", 7)
            pyxel.text(10, 90, "Tiles shown: empty, grass, water", 7)
            pyxel.text(10, 100, "Buildings: res1, res2, res3", 7)
            pyxel.text(10, 110, "Roads: alone, horiz, vert, cross", 7)
        else:
            pyxel.text(10, 50, "No tilemap loaded", 8)
        
        pyxel.text(10, 130, "Press Q to quit", 7)
    
    pyxel.run(update, draw)

if __name__ == "__main__":
    test_correct_png_loading()