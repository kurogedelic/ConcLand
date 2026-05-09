#!/usr/bin/env python3
"""
Generate 100x100 terrain with Voronoi-based ocean/lakes
"""

import random
import pickle
import math
from typing import List, Tuple

MAP_SIZE = 100

class VoronoiPoint:
    def __init__(self, x: float, y: float, terrain_type: int):
        self.x = x
        self.y = y
        self.terrain_type = terrain_type  # 0 = land, 8 = water

def generate_voronoi_terrain():
    """Generate terrain using Voronoi diagram"""
    
    # Initialize with all land
    grid = [[0 for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
    
    # Create Voronoi seed points
    voronoi_points = []
    
    # Add water seed points (20-30% of area should be water)
    num_water_seeds = random.randint(8, 15)
    for _ in range(num_water_seeds):
        x = random.uniform(0, MAP_SIZE)
        y = random.uniform(0, MAP_SIZE)
        voronoi_points.append(VoronoiPoint(x, y, 8))  # Water
    
    # Add land seed points
    num_land_seeds = random.randint(20, 30)
    for _ in range(num_land_seeds):
        x = random.uniform(0, MAP_SIZE)
        y = random.uniform(0, MAP_SIZE)
        voronoi_points.append(VoronoiPoint(x, y, 0))  # Land
    
    print(f"Generating Voronoi terrain with {num_water_seeds} water seeds and {num_land_seeds} land seeds...")
    
    # Assign each cell to nearest Voronoi point
    for y in range(MAP_SIZE):
        for x in range(MAP_SIZE):
            min_dist = float('inf')
            nearest_type = 0
            
            # Find nearest Voronoi point
            for point in voronoi_points:
                dist = math.sqrt((x - point.x)**2 + (y - point.y)**2)
                if dist < min_dist:
                    min_dist = dist
                    nearest_type = point.terrain_type
            
            grid[y][x] = nearest_type
    
    # Apply smoothing for more natural coastlines
    grid = smooth_terrain(grid, iterations=2)
    
    # Generate coastline map
    coastline_map = generate_coastlines(grid)
    
    return grid, coastline_map

def smooth_terrain(grid: List[List[int]], iterations: int = 2) -> List[List[int]]:
    """Smooth terrain to create more natural shapes"""
    
    for _ in range(iterations):
        new_grid = [[0 for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
        
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                # Count neighbors
                water_count = 0
                total_count = 0
                
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < MAP_SIZE and 0 <= nx < MAP_SIZE:
                            if grid[ny][nx] == 8:  # Water
                                water_count += 1
                            total_count += 1
                
                # Majority rule
                if water_count > total_count / 2:
                    new_grid[y][x] = 8  # Water
                else:
                    new_grid[y][x] = 0  # Land
        
        grid = new_grid
    
    return grid

def generate_coastlines(grid: List[List[int]]) -> dict:
    """Generate coastline tiles for water edges including diagonals"""
    coastline_map = {}
    
    for y in range(MAP_SIZE):
        for x in range(MAP_SIZE):
            if grid[y][x] == 0:  # Land tile
                # Check cardinal directions (N, E, S, W)
                north = y > 0 and grid[y-1][x] == 8
                south = y < MAP_SIZE-1 and grid[y+1][x] == 8
                east = x < MAP_SIZE-1 and grid[y][x+1] == 8
                west = x > 0 and grid[y][x-1] == 8
                
                # Check diagonal directions (NE, SE, SW, NW)
                ne = y > 0 and x < MAP_SIZE-1 and grid[y-1][x+1] == 8
                se = y < MAP_SIZE-1 and x < MAP_SIZE-1 and grid[y+1][x+1] == 8
                sw = y < MAP_SIZE-1 and x > 0 and grid[y+1][x-1] == 8
                nw = y > 0 and x > 0 and grid[y-1][x-1] == 8
                
                # First check for diagonal coastlines (corner cases)
                # These are land tiles with water only at diagonal corners
                if not north and not south and not east and not west:
                    # No cardinal water neighbors, check for diagonal patterns
                    if ne and not se and not sw and not nw:
                        coastline_map[(x, y)] = 'coastline_diagonal_ne'
                    elif not ne and se and not sw and not nw:
                        coastline_map[(x, y)] = 'coastline_diagonal_se'
                    elif not ne and not se and sw and not nw:
                        coastline_map[(x, y)] = 'coastline_diagonal_sw'
                    elif not ne and not se and not sw and nw:
                        coastline_map[(x, y)] = 'coastline_diagonal_nw'
                    # Multiple diagonal corners - use special patterns
                    elif ne and se and not sw and not nw:
                        coastline_map[(x, y)] = 'coastline_0100'  # East side
                    elif not ne and se and sw and not nw:
                        coastline_map[(x, y)] = 'coastline_0010'  # South side
                    elif not ne and not se and sw and nw:
                        coastline_map[(x, y)] = 'coastline_0001'  # West side
                    elif ne and not se and not sw and nw:
                        coastline_map[(x, y)] = 'coastline_1000'  # North side
                
                # Standard cardinal coastlines
                elif north or south or east or west:
                    # This is a regular coastline
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
    
    return coastline_map

def save_terrain():
    """Generate and save Voronoi terrain"""
    grid, coastline_map = generate_voronoi_terrain()
    
    # Count statistics
    water_count = sum(1 for row in grid for cell in row if cell == 8)
    land_count = sum(1 for row in grid for cell in row if cell == 0)
    coast_count = len(coastline_map)
    
    # Count diagonal coastlines
    diagonal_count = sum(1 for tile in coastline_map.values() if 'diagonal' in tile)
    
    print(f"\nGenerated 100x100 Voronoi terrain:")
    print(f"  Land tiles: {land_count} ({land_count*100//10000}%)")
    print(f"  Water tiles: {water_count} ({water_count*100//10000}%)")
    print(f"  Coastline tiles: {coast_count}")
    print(f"    - Regular coastlines: {coast_count - diagonal_count}")
    print(f"    - Diagonal coastlines: {diagonal_count}")
    
    # Save terrain
    save_data = {
        'terrain': grid,
        'coastline_map': coastline_map,
        'map_size': MAP_SIZE
    }
    
    with open('terrain_voronoi_100.dat', 'wb') as f:
        pickle.dump(save_data, f)
    
    print(f"\n✅ Voronoi terrain saved to terrain_voronoi_100.dat")
    
    # Also save as the main terrain file
    with open('terrain_100.dat', 'wb') as f:
        pickle.dump(save_data, f)
    
    print(f"✅ Also saved as terrain_100.dat for immediate use")
    
    return grid, coastline_map

def visualize_terrain(grid):
    """Simple ASCII visualization of terrain"""
    print("\nTerrain preview (. = land, ~ = water):")
    
    # Show a 50x25 sample from center
    start_x = 25
    start_y = 37
    
    for y in range(start_y, min(start_y + 25, MAP_SIZE)):
        line = ""
        for x in range(start_x, min(start_x + 50, MAP_SIZE)):
            if grid[y][x] == 8:
                line += "~"
            else:
                line += "."
        print(line)

if __name__ == "__main__":
    grid, _ = save_terrain()
    visualize_terrain(grid)
    
    print("\nTo use this terrain:")
    print("1. Run: python3 concland_mini.py")
    print("2. The game will automatically load terrain_100.dat")