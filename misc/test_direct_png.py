#!/usr/bin/env python3
"""Direct test of PNG loading into Pyxel"""

import pyxel
import os

def test():
    pyxel.init(320, 288, title="Direct PNG Test")
    
    # Test loading PNG files directly
    test_files = [
        ('assets/tiles/power/coal.png', 0, 0, "Coal 32x32"),
        ('assets/tiles/power/nuclear.png', 40, 0, "Nuclear 32x32"),
        ('assets/tiles/public/police.png', 80, 0, "Police 24x24"),
    ]
    
    # Load each PNG
    for file_path, x, y, label in test_files:
        if os.path.exists(file_path):
            print(f"Loading {file_path} to ({x},{y})")
            pyxel.images[0].load(x, y, file_path)
        else:
            print(f"File not found: {file_path}")
    
    def update():
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
    
    def draw():
        pyxel.cls(0)
        
        # Draw title
        pyxel.text(10, 10, "Direct PNG Load Test", 7)
        
        # Try to draw the loaded images with different sizes
        y_pos = 40
        
        # Coal - should be 32x32
        pyxel.text(10, y_pos - 10, "Coal 32x32:", 7)
        pyxel.blt(10, y_pos, 0, 0, 0, 32, 32)  # Draw 32x32
        pyxel.rectb(10, y_pos, 32, 32, 14)  # Pink border
        
        # Also try 8x8 for comparison
        pyxel.text(50, y_pos - 10, "Coal 8x8:", 7)
        pyxel.blt(50, y_pos, 0, 0, 0, 8, 8)  # Draw only 8x8
        pyxel.rectb(50, y_pos, 8, 8, 14)
        
        # Nuclear - should be 32x32
        y_pos = 80
        pyxel.text(10, y_pos - 10, "Nuclear 32x32:", 7)
        pyxel.blt(10, y_pos, 0, 40, 0, 32, 32)  # Draw 32x32
        pyxel.rectb(10, y_pos, 32, 32, 14)
        
        # Police - should be 24x24
        y_pos = 120
        pyxel.text(10, y_pos - 10, "Police 24x24:", 7)
        pyxel.blt(10, y_pos, 0, 80, 0, 24, 24)  # Draw 24x24
        pyxel.rectb(10, y_pos, 24, 24, 14)
        
        pyxel.text(10, 260, "ESC to exit", 7)
    
    pyxel.run(update, draw)

if __name__ == "__main__":
    test()