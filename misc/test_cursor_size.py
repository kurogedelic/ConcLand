#!/usr/bin/env python3
"""Test cursor size for coal plant"""

import pyxel

# Constants from concland_mini.py
TILE_SIZE = 8
COAL_PLANT = 8  # Key 8

class TestCursor:
    def __init__(self):
        pyxel.init(320, 240)
        self.cursor_x = 10
        self.cursor_y = 10
        pyxel.run(self.update, self.draw)
    
    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
    
    def draw(self):
        pyxel.cls(0)
        
        pyxel.text(10, 10, "Cursor Size Test", 7)
        
        # Test 3x3 cursor
        pyxel.text(10, 30, "3x3 cursor (24x24 pixels):", 7)
        cursor_3x3 = TILE_SIZE * 3
        pyxel.rectb(10, 50, cursor_3x3, cursor_3x3, 8)
        pyxel.text(10, 80, f"Size: {cursor_3x3}x{cursor_3x3}", 7)
        
        # Test 4x4 cursor
        pyxel.text(100, 30, "4x4 cursor (32x32 pixels):", 7)
        cursor_4x4 = TILE_SIZE * 4
        pyxel.rectb(100, 50, cursor_4x4, cursor_4x4, 11)
        pyxel.text(100, 80, f"Size: {cursor_4x4}x{cursor_4x4}", 7)
        
        # Show TILE_SIZE
        pyxel.text(10, 100, f"TILE_SIZE = {TILE_SIZE}", 7)
        pyxel.text(10, 110, f"3x3 = {TILE_SIZE * 3} pixels", 7)
        pyxel.text(10, 120, f"4x4 = {TILE_SIZE * 4} pixels", 7)
        
        pyxel.text(10, 200, "Q to quit", 7)

if __name__ == "__main__":
    TestCursor()