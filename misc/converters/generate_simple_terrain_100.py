#!/usr/bin/env python3
"""
Generate simple terrain for 100x100 ConcLand map without CellType dependency
"""

import random
import pickle
import json

MAP_SIZE = 100

def generate_simple_terrain():
    """Generate terrain using simple integers (0=land, 1=water)"""
    
    # Initialize grid with all land (0)
    grid = [[0 for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
    
    # Add some water bodies (lakes/ocean)
    # Create several water regions
    num_water_regions = random.randint(8, 15)
    
    for _ in range(num_water_regions):
        # Random center for water region
        cx = random.randint(5, MAP_SIZE - 5)
        cy = random.randint(5, MAP_SIZE - 5)
        
        # Random size
        size = random.randint(5, 20)
        
        # Create water region with organic shape
        for y in range(max(0, cy - size), min(MAP_SIZE, cy + size)):
            for x in range(max(0, cx - size), min(MAP_SIZE, cx + size)):
                # Use distance and randomness for organic shape
                dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if dist < size * (0.5 + random.random() * 0.5):
                    grid[y][x] = 1  # Water
    
    # Apply smoothing for more natural coastlines
    for _ in range(3):
        new_grid = [[0 for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                water_count = 0
                total_count = 0
                
                # Check neighbors
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < MAP_SIZE and 0 <= nx < MAP_SIZE:
                            if grid[ny][nx] == 1:  # Water
                                water_count += 1
                            total_count += 1
                
                # If majority is water, make this water
                if water_count > total_count * 0.5:
                    new_grid[y][x] = 1
                else:
                    new_grid[y][x] = 0
        grid = new_grid
    
    # Generate coastline map
    coastline_map = {}
    for y in range(MAP_SIZE):
        for x in range(MAP_SIZE):
            if grid[y][x] == 0:  # Land
                # Check if adjacent to water
                is_coast = False
                north = y > 0 and grid[y-1][x] == 1
                south = y < MAP_SIZE-1 and grid[y+1][x] == 1
                east = x < MAP_SIZE-1 and grid[y][x+1] == 1
                west = x > 0 and grid[y][x-1] == 1
                
                if north or south or east or west:
                    is_coast = True
                    # Create pattern for coastline type
                    pattern = (north << 3) | (east << 2) | (south << 1) | west
                    
                    coastline_tiles = {
                        0b0001: 'coastline_0001', 0b0010: 'coastline_0010',
                        0b0011: 'coastline_0011', 0b0100: 'coastline_0100',
                        0b0101: 'coastline_0101', 0b0110: 'coastline_0110',
                        0b0111: 'coastline_0111', 0b1000: 'coastline_1000',
                        0b1001: 'coastline_1001', 0b1010: 'coastline_1010',
                        0b1011: 'coastline_1011', 0b1100: 'coastline_1100',
                        0b1101: 'coastline_1101', 0b1110: 'coastline_1110',
                        0b1111: 'coastline_1111'
                    }
                    
                    if pattern in coastline_tiles:
                        coastline_map[(x, y)] = coastline_tiles[pattern]
    
    return grid, coastline_map

def save_terrain():
    """Generate and save terrain in simple format"""
    grid, coastline_map = generate_simple_terrain()
    
    # Count statistics
    water_count = sum(1 for row in grid for cell in row if cell == 1)
    land_count = sum(1 for row in grid for cell in row if cell == 0)
    coast_count = len(coastline_map)
    
    print(f"Generated 100x100 terrain:")
    print(f"  Land tiles: {land_count}")
    print(f"  Water tiles: {water_count} ({water_count*100//(MAP_SIZE*MAP_SIZE)}%)")
    print(f"  Coastline tiles: {coast_count}")
    
    # Save in format that game expects
    save_data = {
        'terrain': grid,  # Simple integer grid
        'coastline_map': coastline_map,
        'map_size': MAP_SIZE
    }
    
    with open('terrain_100.dat', 'wb') as f:
        pickle.dump(save_data, f)
    
    print(f"Terrain saved to terrain_100.dat")
    
    # Also save as JSON for debugging
    debug_data = {
        'terrain': grid,
        'coastline_map': {str(k): v for k, v in coastline_map.items()},
        'map_size': MAP_SIZE,
        'stats': {
            'land': land_count,
            'water': water_count,
            'coastline': coast_count
        }
    }
    
    with open('terrain_100_debug.json', 'w') as f:
        json.dump(debug_data, f, indent=2)
    
    print("Debug info saved to terrain_100_debug.json")

if __name__ == "__main__":
    save_terrain()
    print("\nTo use this terrain in ConcLand:")
    print("1. Run: python3 concland_mini.py")
    print("2. The game will automatically load terrain_100.dat")