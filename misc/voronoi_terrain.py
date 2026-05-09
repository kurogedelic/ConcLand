"""Voronoi-based terrain generation for city simulation"""
import numpy as np
import random
from scipy.spatial import Voronoi, voronoi_plot_2d
from enum import IntEnum

class TerrainType(IntEnum):
    SOIL = 0    # 基本地形
    WATER = 1
    GRASS = 2   # 特別な場所のみ

class VoronoiTerrain:
    def __init__(self, width, height, num_regions=20):
        self.width = width
        self.height = height
        self.num_regions = num_regions
        self.terrain_grid = None
        self.coastline_grid = None  # Stores coastline patterns
        
    def generate_terrain(self):
        """Generate terrain using Voronoi diagram"""
        # Generate random seed points for Voronoi regions
        points = []
        for _ in range(self.num_regions):
            x = random.uniform(0, self.width - 1)
            y = random.uniform(0, self.height - 1)
            points.append([x, y])
        
        # Add boundary points to ensure complete coverage
        # Add corners
        margin = -5  # Negative margin to ensure edge coverage
        points.extend([
            [margin, margin],
            [self.width - 1 + abs(margin), margin],
            [margin, self.height - 1 + abs(margin)],
            [self.width - 1 + abs(margin), self.height - 1 + abs(margin)]
        ])
        
        # Add edge points
        for i in range(0, self.width, 10):
            points.append([i, margin])
            points.append([i, self.height - 1 + abs(margin)])
        for i in range(0, self.height, 10):
            points.append([margin, i])
            points.append([self.width - 1 + abs(margin), i])
        
        points = np.array(points)
        
        # Assign terrain types to each region
        terrain_types = []
        for i in range(len(points)):
            if i < self.num_regions:
                # Main regions get random terrain
                terrain_type = self._get_terrain_type(points[i])
                terrain_types.append(terrain_type)
            else:
                # Boundary points get soil
                terrain_types.append(TerrainType.SOIL)
        
        # Create grid - default to soil
        self.terrain_grid = [[TerrainType.SOIL for _ in range(self.width)] for _ in range(self.height)]
        
        # Fill grid based on nearest Voronoi region
        for y in range(self.height):
            for x in range(self.width):
                # Find nearest seed point
                min_dist = float('inf')
                nearest_idx = 0
                
                for idx, point in enumerate(points):
                    dist = (x - point[0])**2 + (y - point[1])**2
                    if dist < min_dist:
                        min_dist = dist
                        nearest_idx = idx
                
                self.terrain_grid[y][x] = terrain_types[nearest_idx]
        
        # Post-process to smooth terrain
        self._smooth_terrain()
        
        return self.terrain_grid
    
    def _get_terrain_type(self, point):
        """Assign terrain type based on position and random factors"""
        x, y = point
        
        # Create some bias based on position
        # Water tends to be in lower areas (bottom of map)
        water_chance = 0.15 + (y / self.height) * 0.15
        
        # Random selection with biases
        rand = random.random()
        
        if rand < water_chance and y > self.height * 0.3:
            return TerrainType.WATER
        else:
            return TerrainType.SOIL
    
    def _smooth_terrain(self):
        """Smooth terrain transitions"""
        # Create a copy for modifications
        new_grid = [row[:] for row in self.terrain_grid]
        
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                # Count neighboring terrain types
                neighbors = {}
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        terrain = self.terrain_grid[y + dy][x + dx]
                        neighbors[terrain] = neighbors.get(terrain, 0) + 1
                
                # If surrounded by water, become water
                if neighbors.get(TerrainType.WATER, 0) >= 6:
                    new_grid[y][x] = TerrainType.WATER
                
                # If water is isolated, become soil
                if self.terrain_grid[y][x] == TerrainType.WATER:
                    if neighbors.get(TerrainType.WATER, 0) < 2:
                        new_grid[y][x] = TerrainType.SOIL
        
        self.terrain_grid = new_grid
        
        # Generate coastline data
        self.generate_coastlines()
    
    def is_buildable(self, x, y):
        """Check if a position is buildable"""
        if 0 <= x < self.width and 0 <= y < self.height:
            terrain = self.terrain_grid[y][x]
            return terrain in [TerrainType.SOIL, TerrainType.GRASS]
        return False
    
    def get_terrain_color(self, terrain_type):
        """Get color for terrain type (for debug visualization)"""
        colors = {
            TerrainType.SOIL: (121, 85, 72),
            TerrainType.WATER: (3, 169, 244),
            TerrainType.GRASS: (76, 175, 80)
        }
        return colors.get(terrain_type, (0, 0, 0))
    
    def generate_coastlines(self):
        """Generate coastline patterns for water edges"""
        self.coastline_grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        
        for y in range(self.height):
            for x in range(self.width):
                if self.terrain_grid[y][x] == TerrainType.WATER:
                    # Check adjacent non-water cells
                    north = y > 0 and self.terrain_grid[y-1][x] != TerrainType.WATER
                    south = y < self.height-1 and self.terrain_grid[y+1][x] != TerrainType.WATER
                    east = x < self.width-1 and self.terrain_grid[y][x+1] != TerrainType.WATER
                    west = x > 0 and self.terrain_grid[y][x-1] != TerrainType.WATER
                    
                    # Determine coastline pattern
                    if north or south or east or west:
                        # This is a coastline water cell
                        pattern = (north, east, south, west)
                        self.coastline_grid[y][x] = pattern
    
    def get_coastline_tile(self, x, y):
        """Get the appropriate coastline tile pattern for a water cell"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.coastline_grid[y][x]
        return None