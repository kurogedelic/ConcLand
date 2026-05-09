#!/usr/bin/env python3
"""Debug ConcLand Mini graphics loading"""

import os
from concland_tile_system import ConcLandTileManager

def debug_graphics():
    print("=== ConcLand Mini Graphics Debug ===")
    
    # Check file existence
    tilemap_paths = [
        'assets/concland_tiles_16x16.png',
        'assets/tiles_16x16.png', 
        'assets/tilemap_generated.png'
    ]
    
    print("\nTilemap files:")
    for path in tilemap_paths:
        exists = os.path.exists(path)
        size = os.path.getsize(path) if exists else 0
        print(f"  {path}: {'EXISTS' if exists else 'MISSING'} ({size} bytes)")
    
    # Test tile manager
    print("\nTile Manager Test:")
    tile_manager = ConcLandTileManager()
    
    print(f"  Tiles defined: {len(tile_manager.tiles)}")
    print(f"  Sample tiles: {list(tile_manager.tiles.keys())[:10]}")
    
    # Test loading
    print("\nLoading Test:")
    for path in tilemap_paths:
        if os.path.exists(path):
            try:
                success = tile_manager.load_tilemap(path)
                print(f"  {path}: {'SUCCESS' if success else 'FAILED'}")
                if success:
                    break
            except Exception as e:
                print(f"  {path}: ERROR - {e}")
    
    # Check specific tiles used in game
    print("\nRequired tiles check:")
    required_tiles = ['grass', 'water', 'road_horizontal', 'residential_1', 'commercial_1']
    for tile in required_tiles:
        exists = tile in tile_manager.tiles
        print(f"  {tile}: {'OK' if exists else 'MISSING'}")

if __name__ == "__main__":
    debug_graphics()