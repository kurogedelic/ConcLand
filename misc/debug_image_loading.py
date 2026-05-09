#!/usr/bin/env python3
"""
Debug image loading issues in ConcLand Mini
"""
import pyxel
import os
from concland_tile_system import ConcLandTileManager

def test_image_loading():
    print("🔍 ConcLand Image Loading Debug")
    print("="*50)
    
    # Initialize pyxel
    pyxel.init(320, 288, title="Image Loading Test")
    
    # Test different image files
    image_files = [
        "assets/concland_tiles_indexed.png",
        "assets/concland_tiles_rgb.png", 
        "assets/concland_tiles_16x16.png",
        "assets/tiles_16x16.png",
        "assets/tilemap_generated.png"
    ]
    
    print("\n📁 File Existence Check:")
    for filepath in image_files:
        exists = os.path.exists(filepath)
        size = os.path.getsize(filepath) if exists else 0
        print(f"  {filepath:<35} {'✅' if exists else '❌'} ({size} bytes)")
    
    print("\n🖼️  Direct Pyxel Loading Test:")
    for i, filepath in enumerate(image_files):
        if not os.path.exists(filepath):
            continue
            
        try:
            # Try loading to different image banks
            bank = i % 4
            pyxel.images[bank].load(0, 0, filepath)
            
            # Check image dimensions and some pixel data
            width = pyxel.images[bank].width
            height = pyxel.images[bank].height
            
            # Sample some pixels
            sample_pixels = []
            for y in range(min(3, height)):
                for x in range(min(3, width)):
                    pixel = pyxel.images[bank].pget(x, y)
                    sample_pixels.append(pixel)
            
            non_zero_pixels = [p for p in sample_pixels if p != 0]
            
            print(f"  Bank {bank}: {filepath}")
            print(f"    Size: {width}x{height}")
            print(f"    Sample pixels: {sample_pixels[:9]}")
            print(f"    Non-zero pixels: {len(non_zero_pixels)}/9")
            print(f"    Status: {'✅ Has data' if non_zero_pixels else '⚠️  All black'}")
            
        except Exception as e:
            print(f"  ❌ Error loading {filepath}: {e}")
    
    print("\n🛠️  ConcLandTileManager Test:")
    tile_manager = ConcLandTileManager()
    
    for filepath in image_files[:3]:  # Test first 3 files
        if os.path.exists(filepath):
            print(f"\n  Testing {filepath}:")
            success = tile_manager.load_tilemap(filepath)
            print(f"    Result: {'✅ Success' if success else '❌ Failed'}")
            
            if success:
                # Test drawing a tile
                try:
                    if 'grass' in tile_manager.tiles:
                        grass_pos = tile_manager.tiles['grass']  
                        print(f"    Grass tile position: {grass_pos}")
                        tile_manager.draw_tile('grass', 10, 10)
                        print(f"    ✅ Successfully drew grass tile")
                except Exception as e:
                    print(f"    ⚠️  Error drawing tile: {e}")
                break
    
    print("\n💡 Recommendations:")
    print("  - Check if images have correct color depth")
    print("  - Verify PNG format compatibility") 
    print("  - Consider converting to .pyxres format")

def test_pyxres_creation():
    print(f"\n🔧 Testing .pyxres Creation:")
    
    # Create a simple test resource
    pyxel.init(160, 120, title="Pyxres Test")
    
    # Draw some test patterns
    pyxel.images[0].cls(0)
    for i in range(16):
        pyxel.images[0].rect(i*8, 0, 8, 8, i)
        pyxel.images[0].rect(i*8, 8, 8, 8, (i+8) % 16)
    
    # Try to save as pyxres
    try:
        pyxel.save("test_assets.pyxres")
        print("  ✅ Successfully created test_assets.pyxres")
        
        # Try loading it back
        pyxel.load("test_assets.pyxres")
        print("  ✅ Successfully loaded test_assets.pyxres")
        
        return True
    except Exception as e:
        print(f"  ❌ Error with pyxres: {e}")
        return False

if __name__ == "__main__":
    test_image_loading()
    
    if test_pyxres_creation():
        print(f"\n🎯 .pyxres format works! Consider converting assets.")
    else:
        print(f"\n⚠️  .pyxres format issues detected.")