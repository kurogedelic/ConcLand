#!/usr/bin/env python3
"""Simple Pyxel test"""

import pyxel

def test():
    print("Pyxel imported successfully!")
    pyxel.init(160, 120, title="Test")
    print("Pyxel initialized successfully!")
    
    def update():
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
    
    def draw():
        pyxel.cls(0)
        pyxel.text(10, 10, "Pyxel working!", 7)
    
    print("Starting Pyxel...")
    pyxel.run(update, draw)

if __name__ == "__main__":
    test()