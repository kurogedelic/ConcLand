#!/usr/bin/env python3
"""
Test palette loading and color information
"""
import pyxel
import os

def test_palette():
    # Initialize pyxel
    pyxel.init(160, 120, title="Palette Test")
    
    print("=== Pyxel Default Palette ===")
    for i in range(16):
        print(f"Color {i:2d}: 0x{pyxel.colors[i]:06X}")
    
    print("\n=== Loading ConcLand Palette ===")
    palette_path = "assets/palette256.png"
    if os.path.exists(palette_path):
        try:
            pyxel.images[1].load(0, 0, palette_path, incl_colors=True)
            print(f"✅ Successfully loaded: {palette_path}")
            
            # Check if colors changed
            print("\n=== Palette After Loading ===")
            for i in range(16):
                print(f"Color {i:2d}: 0x{pyxel.colors[i]:06X}")
                
        except Exception as e:
            print(f"❌ Failed to load: {e}")
    else:
        print(f"❌ File not found: {palette_path}")
    
    # Check palette256_large.png too
    palette_large_path = "assets/palette256_large.png"
    if os.path.exists(palette_large_path):
        print(f"\n=== Testing Large Palette ===")
        try:
            pyxel.images[2].load(0, 0, palette_large_path, incl_colors=True)
            print(f"✅ Successfully loaded: {palette_large_path}")
            print(f"Image size: {pyxel.images[2].width}x{pyxel.images[2].height}")
        except Exception as e:
            print(f"❌ Failed to load: {e}")

if __name__ == "__main__":
    test_palette()