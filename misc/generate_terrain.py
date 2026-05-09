#!/usr/bin/env python3
"""
Generate and save a good terrain for development
"""

import sys
import os
import pickle
from enum import Enum

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from terrain_generator import VoronoiTerrainGenerator, TerrainType
from diagonal_coastline_system import DiagonalCoastlineSystem

MAP_SIZE = 64

class CellType(Enum):
    EMPTY = 0
    WATER = 8

def generate_good_terrain():
    """Generate a nice terrain with good land/water balance"""
    
    print("🌍 Generating terrain...")
    
    # Generate terrain using Voronoi diagrams
    terrain_gen = VoronoiTerrainGenerator(MAP_SIZE, MAP_SIZE)
    terrain_gen.generate_random_seeds(20)  # 20 seed points for good variety
    voronoi_terrain = terrain_gen.generate_terrain()
    terrain_gen.print_terrain_stats(voronoi_terrain)
    
    # Generate detailed coastlines using the same method as the game
    coastlined_terrain, coastline_map = terrain_gen.generate_detailed_coastlines(voronoi_terrain)
    
    print(f"📍 Generated {len(coastline_map)} coastline tiles")
    
    # Convert to grid format
    terrain_data = []
    for y in range(MAP_SIZE):
        row = []
        for x in range(MAP_SIZE):
            terrain_type = coastlined_terrain[y][x]
            if terrain_type == TerrainType.WATER:
                row.append(CellType.WATER.value)
            else:
                row.append(CellType.EMPTY.value)
        terrain_data.append(row)
    
    # Convert coastline_map keys from tuples to strings for pickle compatibility
    coastline_map_serializable = {}
    for (x, y), tile_type in coastline_map.items():
        coastline_map_serializable[(x, y)] = tile_type
    
    # Save both terrain and coastline map
    save_data = {
        'terrain': terrain_data,
        'coastline_map': coastline_map_serializable
    }
    
    with open("terrain.dat", 'wb') as f:
        pickle.dump(save_data, f)
    
    print("✅ Terrain saved to terrain.dat")
    print("📝 This terrain will be loaded automatically when you run concland_mini.py")
    
    # Count land vs water
    water_count = sum(1 for row in terrain_data for cell in row if cell == CellType.WATER.value)
    land_count = MAP_SIZE * MAP_SIZE - water_count
    water_percent = (water_count * 100) // (MAP_SIZE * MAP_SIZE)
    
    print(f"📊 Terrain stats: {land_count} land tiles, {water_count} water tiles ({water_percent}% water)")

if __name__ == "__main__":
    generate_good_terrain()