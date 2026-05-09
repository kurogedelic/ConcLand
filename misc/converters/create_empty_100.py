#!/usr/bin/env python3
"""
Create a completely empty 100x100 map with NO buildings, NO roads, NOTHING
Just terrain (land and water)
"""

import pickle

MAP_SIZE = 100

def create_empty_map():
    """Create completely empty 100x100 map"""
    
    # Create grid - all empty land (0 = empty land, 1 = water)
    grid = []
    for y in range(MAP_SIZE):
        row = []
        for x in range(MAP_SIZE):
            # All empty land - no water
            row.append(0)  # Empty = 0 in CellType enum
        grid.append(row)
    
    # No coastline map for simplicity
    coastline_map = {}
    
    # Count statistics
    water_count = sum(1 for row in grid for cell in row if cell == 8)  # Water = 8
    land_count = sum(1 for row in grid for cell in row if cell == 0)  # Empty = 0
    
    print(f"Created empty 100x100 map:")
    print(f"  Land tiles: {land_count}")
    print(f"  Water tiles: {water_count}")
    print(f"  Total: {MAP_SIZE}x{MAP_SIZE} = {MAP_SIZE*MAP_SIZE} tiles")
    
    # Save as terrain_100.dat
    save_data = {
        'terrain': grid,
        'coastline_map': coastline_map,
        'map_size': MAP_SIZE
    }
    
    with open('terrain_100.dat', 'wb') as f:
        pickle.dump(save_data, f)
    
    print("\n✅ Empty map saved to terrain_100.dat")
    print("\nThis map has:")
    print("- NO buildings")
    print("- NO roads")
    print("- NO infrastructure")
    print("- Just empty land with water border")

if __name__ == "__main__":
    create_empty_map()