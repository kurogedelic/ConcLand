#!/usr/bin/env python3
"""
Voronoi Terrain Generator for ConcLand Mini
Generates realistic terrain using Voronoi diagrams
"""

import random
import math
from typing import List, Tuple, Dict
from enum import IntEnum
from dataclasses import dataclass

class TerrainType(IntEnum):
    WATER = 0
    SAND = 1
    GRASS = 2
    SOIL = 3
    COASTLINE = 4  # Special type for coastline tiles

@dataclass
class VoronoiSeed:
    x: float
    y: float
    terrain_type: TerrainType
    strength: float = 1.0  # Influence strength

class VoronoiTerrainGenerator:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.seeds: List[VoronoiSeed] = []
        
    def add_seed(self, x: float, y: float, terrain_type: TerrainType, strength: float = 1.0):
        """Add a Voronoi seed point"""
        self.seeds.append(VoronoiSeed(x, y, terrain_type, strength))
    
    def generate_random_seeds(self, num_seeds: int = 20):
        """Generate random seed points with realistic terrain distribution"""
        self.seeds.clear()
        
        # Generate water bodies (lakes, rivers)
        water_seeds = max(2, num_seeds // 6)
        for _ in range(water_seeds):
            x = random.uniform(0.1, 0.9) * self.width
            y = random.uniform(0.1, 0.9) * self.height  
            strength = random.uniform(0.8, 1.5)
            self.add_seed(x, y, TerrainType.WATER, strength)
        
        # Generate sand/beach areas (near water or random)
        sand_seeds = max(1, num_seeds // 8)
        for _ in range(sand_seeds):
            x = random.uniform(0, 1) * self.width
            y = random.uniform(0, 1) * self.height
            strength = random.uniform(0.6, 1.0)
            self.add_seed(x, y, TerrainType.SAND, strength)
        
        # Generate soil patches
        soil_seeds = max(2, num_seeds // 5)
        for _ in range(soil_seeds):
            x = random.uniform(0, 1) * self.width
            y = random.uniform(0, 1) * self.height
            strength = random.uniform(0.7, 1.2)
            self.add_seed(x, y, TerrainType.SOIL, strength)
        
        # Fill remaining with grass (most common terrain)
        grass_seeds = num_seeds - water_seeds - sand_seeds - soil_seeds
        for _ in range(grass_seeds):
            x = random.uniform(0, 1) * self.width
            y = random.uniform(0, 1) * self.height
            strength = random.uniform(0.8, 1.0)
            self.add_seed(x, y, TerrainType.GRASS, strength)
    
    def distance(self, x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate Euclidean distance between two points"""
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    
    def generate_terrain(self) -> List[List[TerrainType]]:
        """Generate terrain using Voronoi diagram"""
        terrain = [[TerrainType.GRASS for _ in range(self.width)] for _ in range(self.height)]
        
        if not self.seeds:
            print("⚠️  No seeds found, generating random seeds")
            self.generate_random_seeds()
        
        print(f"🏔️  Generating {self.width}x{self.height} terrain with {len(self.seeds)} seeds...")
        
        # For each cell, find the closest seed
        for y in range(self.height):
            for x in range(self.width):
                min_distance = float('inf')
                closest_terrain = TerrainType.GRASS
                
                # Check all seeds
                for seed in self.seeds:
                    dist = self.distance(x, y, seed.x, seed.y)
                    # Apply strength weighting
                    weighted_dist = dist / seed.strength
                    
                    if weighted_dist < min_distance:
                        min_distance = weighted_dist
                        closest_terrain = seed.terrain_type
                
                terrain[y][x] = closest_terrain
        
        # Post-processing: smooth terrain transitions
        terrain = self._smooth_terrain(terrain)
        
        # Generate coastlines for water edges
        terrain = self._generate_coastlines(terrain)
        
        return terrain
    
    def _smooth_terrain(self, terrain: List[List[TerrainType]]) -> List[List[TerrainType]]:
        """Apply smoothing to reduce harsh terrain transitions"""
        smoothed = [row[:] for row in terrain]  # Deep copy
        
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                # Count neighbor terrain types
                neighbors = {}
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        neighbor_type = terrain[y + dy][x + dx]
                        neighbors[neighbor_type] = neighbors.get(neighbor_type, 0) + 1
                
                # If current cell is isolated, change to most common neighbor
                current_type = terrain[y][x]
                if neighbors.get(current_type, 0) < 2:  # Less than 2 similar neighbors
                    most_common = max(neighbors.items(), key=lambda item: item[1])
                    if most_common[1] >= 3:  # At least 3 neighbors of same type
                        smoothed[y][x] = most_common[0]
        
        return smoothed
    
    def _generate_coastlines(self, terrain: List[List[TerrainType]]) -> List[List[TerrainType]]:
        """Generate sand coastlines around water bodies"""
        coastlined = [row[:] for row in terrain]  # Deep copy
        
        for y in range(self.height):
            for x in range(self.width):
                if terrain[y][x] != TerrainType.WATER:
                    # Check if this cell is adjacent to water
                    adjacent_to_water = False
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < self.height and 0 <= nx < self.width:
                                if terrain[ny][nx] == TerrainType.WATER:
                                    adjacent_to_water = True
                                    break
                        if adjacent_to_water:
                            break
                    
                    # Convert to sand if adjacent to water and not already soil/sand
                    if adjacent_to_water and terrain[y][x] == TerrainType.GRASS:
                        # 70% chance to become sand (for natural variation)
                        if random.random() < 0.7:
                            coastlined[y][x] = TerrainType.SAND
        
        return coastlined
    
    def generate_detailed_coastlines(self, terrain: List[List[TerrainType]]) -> Tuple[List[List[TerrainType]], Dict[Tuple[int, int], str]]:
        """
        Generate detailed coastline tiles for water/land boundaries  
        Returns: (updated_terrain, coastline_tile_map)
        """
        try:
            from diagonal_coastline_system import DiagonalCoastlineSystem
        except ImportError:
            print("⚠️  CoastlineSystem not available, using simple coastlines")
            return terrain, {}
        
        # Convert terrain to format expected by coastline system
        terrain_strings = []
        for row in terrain:
            string_row = []
            for cell in row:
                if cell == TerrainType.WATER:
                    string_row.append('water')
                else:
                    string_row.append('land')
            terrain_strings.append(string_row)
        
        # Generate coastline mapping with diagonal support
        coastline_system = DiagonalCoastlineSystem()
        coastline_map = coastline_system.generate_coastline_map(terrain_strings)
        coastline_system.print_coastline_stats(coastline_map)
        
        # Update terrain with coastline information
        coastlined_terrain = [row[:] for row in terrain]  # Deep copy
        
        for (x, y), coastline_tile in coastline_map.items():
            # Mark land cells adjacent to water as coastline
            if terrain[y][x] != TerrainType.WATER:
                coastlined_terrain[y][x] = TerrainType.COASTLINE
        
        return coastlined_terrain, coastline_map
    
    def get_cell_type_mapping(self) -> Dict[TerrainType, str]:
        """Get mapping from TerrainType to CellType string"""
        return {
            TerrainType.WATER: 'water',
            TerrainType.SAND: 'sand',  # Now using dedicated sand tile
            TerrainType.GRASS: 'grass',
            TerrainType.SOIL: 'soil',
            TerrainType.COASTLINE: 'coastline'  # Will be handled specially
        }
    
    def print_terrain_stats(self, terrain: List[List[TerrainType]]):
        """Print statistics about generated terrain"""
        stats = {terrain_type: 0 for terrain_type in TerrainType}
        total_cells = self.width * self.height
        
        for row in terrain:
            for cell in row:
                stats[cell] += 1
        
        print("🌍 Terrain Generation Complete!")
        print("📊 Terrain Statistics:")
        for terrain_type, count in stats.items():
            percentage = (count / total_cells) * 100
            name = terrain_type.name.lower()
            print(f"  {name.capitalize()}: {count} cells ({percentage:.1f}%)")

def test_terrain_generator():
    """Test the terrain generator"""
    print("🧪 Testing Voronoi Terrain Generator")
    
    generator = VoronoiTerrainGenerator(32, 32)
    generator.generate_random_seeds(15)
    terrain = generator.generate_terrain()
    generator.print_terrain_stats(terrain)
    
    # Print small sample
    print("\n🗺️  Sample terrain (top-left 8x8):")
    type_chars = {
        TerrainType.WATER: '~',
        TerrainType.SAND: '.',
        TerrainType.GRASS: '#',
        TerrainType.SOIL: 'o'
    }
    
    for y in range(min(8, len(terrain))):
        row_str = ""
        for x in range(min(8, len(terrain[0]))):
            row_str += type_chars[terrain[y][x]]
        print(f"  {row_str}")

if __name__ == "__main__":
    test_terrain_generator()