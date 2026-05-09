#!/usr/bin/env python3
"""
Test converting PNG assets to .pyxres format
"""
import pyxel
import os

def create_concland_pyxres():
    print("🔧 Creating ConcLand.pyxres from PNG assets")
    print("="*50)
    
    # Initialize pyxel
    pyxel.init(320, 288, title="Asset Converter")
    
    # Load existing images into different banks
    image_files = [
        ("assets/concland_tiles_indexed.png", 0),  # Main tileset
        ("assets/palette256.png", 1),              # Palette
        ("assets/tool_icons.png", 2),              # Tool icons  
        ("assets/ui_icons.png", 3)                # UI icons (if exists)
    ]
    
    loaded_count = 0
    for filepath, bank in image_files:
        if os.path.exists(filepath):
            try:
                pyxel.images[bank].load(0, 0, filepath)
                print(f"✅ Loaded {filepath} into bank {bank}")
                
                # Show some info about the loaded image
                width = pyxel.images[bank].width
                height = pyxel.images[bank].height
                print(f"   Size: {width}x{height}")
                
                loaded_count += 1
            except Exception as e:
                print(f"❌ Failed to load {filepath}: {e}")
        else:
            print(f"⚠️  File not found: {filepath}")
    
    print(f"\n📊 Successfully loaded {loaded_count} assets")
    
    # Create a simple tilemap for testing
    print(f"\n🗺️  Creating test tilemap...")
    # Set individual tiles (u, v) coordinates in tilemap
    for y in range(3):
        for x in range(3):
            tile_id = x + y * 3 + 1
            u = (tile_id % 16) * 16  # Tile U coordinate
            v = (tile_id // 16) * 16  # Tile V coordinate
            pyxel.tilemaps[0].pset(x, y, (u, v))
    
    # Save as .pyxres file
    output_file = "concland_assets.pyxres"
    try:
        pyxel.save(output_file)
        print(f"✅ Successfully saved {output_file}")
        
        # Check file size
        size = os.path.getsize(output_file)
        print(f"   File size: {size} bytes")
        
        return True
    except Exception as e:
        print(f"❌ Failed to save pyxres: {e}")
        return False

def test_pyxres_loading():
    print(f"\n🧪 Testing .pyxres loading...")
    
    if not os.path.exists("concland_assets.pyxres"):
        print("❌ concland_assets.pyxres not found")
        return False
    
    try:
        # Initialize fresh pyxel instance would be needed, but we can't re-init
        # So we'll test loading into a different set of resources
        pyxel.load("concland_assets.pyxres")
        print("✅ Successfully loaded concland_assets.pyxres")
        
        # Test accessing the loaded data
        try:
            # Check if tilemap was loaded
            tile_data = pyxel.tilemaps[0].pget(0, 0)
            print(f"   Tilemap test: First tile = {tile_data}")
            
            # Check image data
            pixel = pyxel.images[0].pget(0, 0)
            print(f"   Image test: First pixel = {pixel}")
            
        except Exception as e:
            print(f"⚠️  Error accessing loaded data: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to load pyxres: {e}")
        return False

def compare_formats():
    print(f"\n📊 PNG vs .pyxres Comparison:")
    
    png_files = [
        "assets/concland_tiles_indexed.png",
        "assets/concland_tiles_16x16.png", 
        "assets/tool_icons.png"
    ]
    
    total_png_size = 0
    for filepath in png_files:
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            total_png_size += size
            print(f"  {os.path.basename(filepath):<30} {size:>6} bytes")
    
    pyxres_size = 0
    if os.path.exists("concland_assets.pyxres"):
        pyxres_size = os.path.getsize("concland_assets.pyxres")
        print(f"  {'concland_assets.pyxres':<30} {pyxres_size:>6} bytes")
    
    print(f"\n📈 Summary:")
    print(f"  Total PNG size: {total_png_size} bytes")
    print(f"  Pyxres size:    {pyxres_size} bytes")
    
    if pyxres_size > 0:
        ratio = pyxres_size / total_png_size
        print(f"  Size ratio:     {ratio:.2f}x")
        print(f"  Advantage:      {'Pyxres' if ratio < 1 else 'PNG'} is smaller")

def main():
    success = create_concland_pyxres()
    
    if success:
        test_pyxres_loading()
        compare_formats()
        
        print(f"\n💡 Recommendation:")
        if success:
            print("  ✅ .pyxres format works well for ConcLand!")
            print("  🔄 Consider updating concland_mini.py to use .pyxres")
            print("  📦 Single file contains all assets")
            print("  ⚡ Potentially faster loading")
        else:
            print("  ⚠️  Stick with PNG files for now")
    
    # Cleanup
    if os.path.exists("concland_assets.pyxres"):
        print(f"\n🧹 Cleanup: Keeping concland_assets.pyxres for testing")

if __name__ == "__main__":
    main()