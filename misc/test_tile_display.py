#!/usr/bin/env python3
"""
Test PNG tile display functionality
"""
import pyxel
import os
from concland_tile_system import ConcLandTileManager

def test_tile_display():
    print("🎨 Testing PNG Tile Display")
    print("="*40)
    
    # Initialize pyxel
    pyxel.init(320, 288, title="Tile Display Test")
    
    # Create tile manager
    tile_manager = ConcLandTileManager()
    
    # Test loading tilemap
    tilemap_files = [
        'assets/concland_tiles_indexed.png',
        'assets/concland_tiles_16x16.png',
        'assets/tilemap_generated.png'
    ]
    
    loaded_tilemap = None
    for tilemap_file in tilemap_files:
        if os.path.exists(tilemap_file):
            print(f"📁 Testing {tilemap_file}...")
            if tile_manager.load_tilemap(tilemap_file):
                loaded_tilemap = tilemap_file
                print(f"✅ Successfully loaded: {tilemap_file}")
                break
            else:
                print(f"❌ Failed to load: {tilemap_file}")
    
    if not loaded_tilemap:
        print("❌ No tilemap could be loaded!")
        return
    
    print(f"\n🎯 Using tilemap: {loaded_tilemap}")
    print(f"📊 Available tiles: {len(tile_manager.tiles)}")
    
    # Test drawing different tiles
    test_tiles = [
        'empty', 'grass', 'water',
        'residential_1', 'commercial_1', 'industrial_1',
        'road_alone', 'road_horizontal', 'road_vertical',
        'rail_alone', 'wire', 'park',
        'coal_plant', 'police'
    ]
    
    def draw_test():
        pyxel.cls(0)
        
        # Draw title
        pyxel.text(10, 10, "PNG Tile Display Test", 7)
        pyxel.text(10, 20, f"Loaded: {os.path.basename(loaded_tilemap)}", 6)
        
        # Draw test tiles in a grid
        start_x, start_y = 10, 40
        cols = 8
        
        for i, tile_name in enumerate(test_tiles):
            col = i % cols
            row = i // cols
            x = start_x + col * 20
            y = start_y + row * 20
            
            # Draw tile
            if tile_name in tile_manager.tiles:
                tile_manager.draw_tile(tile_name, x, y)
                # Label
                pyxel.text(x, y + 16, tile_name[:4], 7)
            else:
                # Missing tile indicator
                pyxel.rect(x, y, 16, 16, 8)
                pyxel.text(x + 2, y + 6, "?", 7)
                pyxel.text(x, y + 16, "MISS", 8)
        
        # Instructions
        pyxel.text(10, 200, "ESC: Exit test", 7)
        
        # Show image bank info
        try:
            width = pyxel.images[tile_manager.image_bank].width
            height = pyxel.images[tile_manager.image_bank].height
            pyxel.text(10, 220, f"Image bank {tile_manager.image_bank}: {width}x{height}", 6)
            
            # Sample a few pixels to verify image data
            sample_pixels = []
            for y_pos in range(min(3, height)):
                for x_pos in range(min(3, width)):
                    pixel = pyxel.images[tile_manager.image_bank].pget(x_pos, y_pos)
                    sample_pixels.append(pixel)
            
            pyxel.text(10, 230, f"Sample pixels: {sample_pixels[:6]}", 6)
            
        except Exception as e:
            pyxel.text(10, 220, f"Error reading image: {e}", 8)
    
    def update_test():
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
    
    print("\n🎮 Starting interactive tile display test...")
    print("   Press ESC to exit")
    
    pyxel.run(update_test, draw_test)

if __name__ == "__main__":
    test_tile_display()