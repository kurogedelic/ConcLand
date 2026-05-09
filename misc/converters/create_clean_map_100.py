#!/usr/bin/env python3
"""
Create a completely clean 100x100 map with only terrain (no buildings)
"""

import pickle
import random

MAP_SIZE = 100

def create_clean_map():
    """Create a clean map with only terrain"""
    
    # Create empty land grid (0 = empty land)
    grid = [[0 for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
    
    # Add ocean on edges and some water bodies
    # Create ocean on edges
    for y in range(MAP_SIZE):
        for x in range(MAP_SIZE):
            # Ocean on edges (10 tiles from edge)
            if x < 10 or x >= MAP_SIZE - 10 or y < 10 or y >= MAP_SIZE - 10:
                if random.random() < 0.7:  # 70% chance for water on edges
                    grid[y][x] = 1  # Water
    
    # Add some lakes in the middle
    for _ in range(5):
        cx = random.randint(20, MAP_SIZE - 20)
        cy = random.randint(20, MAP_SIZE - 20)
        radius = random.randint(3, 8)
        
        for y in range(max(0, cy - radius), min(MAP_SIZE, cy + radius)):
            for x in range(max(0, cx - radius), min(MAP_SIZE, cx + radius)):
                dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if dist <= radius:
                    grid[y][x] = 1  # Water
    
    # Calculate coastlines
    coastline_map = {}
    for y in range(MAP_SIZE):
        for x in range(MAP_SIZE):
            if grid[y][x] == 0:  # Land
                # Check if adjacent to water
                north = y > 0 and grid[y-1][x] == 1
                south = y < MAP_SIZE-1 and grid[y+1][x] == 1
                east = x < MAP_SIZE-1 and grid[y][x+1] == 1
                west = x > 0 and grid[y][x-1] == 1
                
                if north or south or east or west:
                    # Create pattern for coastline
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
    
    # Count statistics
    water_count = sum(1 for row in grid for cell in row if cell == 1)
    land_count = sum(1 for row in grid for cell in row if cell == 0)
    
    print(f"Created clean 100x100 map:")
    print(f"  Land tiles: {land_count}")
    print(f"  Water tiles: {water_count} ({water_count*100//(MAP_SIZE*MAP_SIZE)}%)")
    print(f"  Coastline tiles: {len(coastline_map)}")
    
    # Save terrain data
    save_data = {
        'terrain': grid,
        'coastline_map': coastline_map,
        'map_size': MAP_SIZE
    }
    
    # Save as terrain_100.dat
    with open('terrain_100.dat', 'wb') as f:
        pickle.dump(save_data, f)
    
    print("✅ Clean map saved to terrain_100.dat")
    
    # Also create a full save file with empty sim_data
    # This is for loading with 'I' key
    full_save = {
        'grid': grid,
        'sim_data': [[{
            'population': 0,
            'pollution': 0,
            'land_value': 128,
            'power': False,
            'water': False,
            'traffic': 0,
            'density': 0,
            'building_variant': 0,
            'under_construction': 0,
            'building_id': 0,
            'crime': 0,
            'fire_risk': 0,
            'original_terrain': None,
            'has_road': False,
            'has_rail': False,
            'has_wire': False
        } for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)],
        'coastline_map': coastline_map,
        'funds': 10000,
        'population': 0,
        'year': 2025,
        'month': 1,
        'day': 1,
        'total_population': 0
    }
    
    with open('savegame_clean.dat', 'wb') as f:
        pickle.dump(full_save, f)
    
    print("✅ Clean save file created as savegame_clean.dat")
    print("\nUsage:")
    print("1. Start game: python3 concland_mini.py")
    print("2. Game will auto-load terrain_100.dat")
    print("3. Or press 'I' to load savegame_clean.dat")

if __name__ == "__main__":
    create_clean_map()