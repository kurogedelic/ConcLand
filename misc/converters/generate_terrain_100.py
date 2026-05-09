#!/usr/bin/env python3
"""
Generate terrain for 100x100 ConcLand map
"""

import random
import pickle
from enum import IntEnum
from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np
from scipy.spatial import Voronoi
import os

# Constants for 100x100 map
MAP_SIZE = 100

class CellType(IntEnum):
    EMPTY = 0       # Empty land
    WATER = 1       # Water/Ocean

@dataclass  
class SimData:
    """Minimal simulation data for terrain generation"""
    population: int = 0
    pollution: int = 0
    land_value: int = 128
    power: bool = False
    water: bool = False
    traffic: int = 0
    density: int = 0
    building_variant: int = 0
    under_construction: int = 0
    building_id: int = 0
    crime: int = 0
    fire_risk: int = 0
    original_terrain: Optional['CellType'] = None
    has_road: bool = False
    has_rail: bool = False
    has_wire: bool = False

def generate_terrain_voronoi(size: int = MAP_SIZE, num_regions: int = 30, water_percentage: float = 0.30) -> Tuple[List[List[CellType]], dict]:
    """Generate terrain using Voronoi diagrams for 100x100 map"""
    
    # Initialize grid
    grid = [[CellType.EMPTY for _ in range(size)] for _ in range(size)]
    
    # Generate random points for Voronoi regions (more points for 100x100)
    points = []
    for _ in range(num_regions):
        x = random.uniform(0, size)
        y = random.uniform(0, size)
        points.append([x, y])
    
    # Add boundary points to ensure proper Voronoi diagram
    for i in range(10):
        points.append([-10, i * size / 9])
        points.append([size + 10, i * size / 9])
        points.append([i * size / 9, -10])
        points.append([i * size / 9, size + 10])
    
    points = np.array(points)
    
    # Create Voronoi diagram
    vor = Voronoi(points)
    
    # Assign terrain types to regions (first num_regions are the actual regions)
    region_types = []
    for i in range(num_regions):
        # 30% chance for water
        if random.random() < water_percentage:
            region_types.append(CellType.WATER)
        else:
            region_types.append(CellType.EMPTY)
    
    # Fill grid based on Voronoi regions
    for y in range(size):
        for x in range(size):
            # Find closest point
            distances = np.sqrt((points[:num_regions, 0] - x)**2 + (points[:num_regions, 1] - y)**2)
            closest_point = np.argmin(distances)
            grid[y][x] = region_types[closest_point]
    
    # Apply smoothing to make more natural coastlines
    for _ in range(2):
        new_grid = [[CellType.EMPTY for _ in range(size)] for _ in range(size)]
        for y in range(size):
            for x in range(size):
                water_count = 0
                total_count = 0
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < size and 0 <= nx < size:
                            if grid[ny][nx] == CellType.WATER:
                                water_count += 1
                            total_count += 1
                
                if water_count >= total_count / 2:
                    new_grid[y][x] = CellType.WATER
                else:
                    new_grid[y][x] = CellType.EMPTY
        grid = new_grid
    
    # Add some islands and lakes for variety
    for _ in range(5):
        cx = random.randint(10, size - 10)
        cy = random.randint(10, size - 10)
        radius = random.randint(3, 8)
        terrain_type = random.choice([CellType.WATER, CellType.EMPTY])
        
        for y in range(max(0, cy - radius), min(size, cy + radius)):
            for x in range(max(0, cx - radius), min(size, cx + radius)):
                if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                    grid[y][x] = terrain_type
    
    # Calculate coastlines
    coastline_map = {}
    for y in range(size):
        for x in range(size):
            if grid[y][x] == CellType.EMPTY:
                # Check if adjacent to water
                is_coast = False
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dy == 0 and dx == 0:
                            continue
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < size and 0 <= nx < size:
                            if grid[ny][nx] == CellType.WATER:
                                is_coast = True
                                break
                    if is_coast:
                        break
                
                if is_coast:
                    # Determine coastline type
                    north = y > 0 and grid[y-1][x] == CellType.WATER
                    south = y < size-1 and grid[y+1][x] == CellType.WATER
                    east = x < size-1 and grid[y][x+1] == CellType.WATER
                    west = x > 0 and grid[y][x-1] == CellType.WATER
                    
                    # Create binary pattern
                    pattern = (north << 3) | (east << 2) | (south << 1) | west
                    
                    # Map to coastline tile
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
    
    # Count terrain statistics
    water_count = sum(1 for row in grid for cell in row if cell == CellType.WATER)
    land_count = size * size - water_count
    coast_count = len(coastline_map)
    
    print(f"Generated 100x100 terrain:")
    print(f"  Land tiles: {land_count}")
    print(f"  Water tiles: {water_count} ({water_count*100//(size*size)}%)")
    print(f"  Coastline tiles: {coast_count}")
    
    return grid, coastline_map

def save_terrain(filename: str = "terrain_100.dat"):
    """Generate and save terrain for 100x100 map"""
    # Generate terrain
    grid, coastline_map = generate_terrain_voronoi(MAP_SIZE, num_regions=30, water_percentage=0.30)
    
    # Create sim_data grid
    sim_data = [[SimData() for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
    
    # Save to file
    save_data = {
        'grid': grid,
        'sim_data': sim_data,
        'coastline_map': coastline_map,
        'map_size': MAP_SIZE
    }
    
    with open(filename, 'wb') as f:
        pickle.dump(save_data, f)
    
    print(f"Terrain saved to {filename}")
    return grid, coastline_map

if __name__ == "__main__":
    # Check if scipy is installed
    try:
        from scipy.spatial import Voronoi
    except ImportError:
        print("Error: scipy is required for terrain generation")
        print("Install with: pip install scipy")
        exit(1)
    
    # Generate and save terrain
    save_terrain("terrain_100.dat")
    print("\nTo use this terrain in ConcLand:")
    print("1. The game will automatically load terrain_100.dat on startup")
    print("2. Or press 'I' in game to load the terrain")