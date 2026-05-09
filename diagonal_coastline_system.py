#!/usr/bin/env python3
"""
Enhanced Coastline System with Diagonal Support
Detects both straight and diagonal coastlines for smooth, natural shores
"""

from typing import List, Dict, Tuple
from enum import IntEnum

class Direction(IntEnum):
    NORTH = 0
    NORTHEAST = 1
    EAST = 2
    SOUTHEAST = 3
    SOUTH = 4
    SOUTHWEST = 5
    WEST = 6
    NORTHWEST = 7

class DiagonalCoastlineSystem:
    def __init__(self):
        # 8-direction offsets (N, NE, E, SE, S, SW, W, NW)
        self.direction_offsets = {
            Direction.NORTH: (0, -1),
            Direction.NORTHEAST: (1, -1),
            Direction.EAST: (1, 0),
            Direction.SOUTHEAST: (1, 1),
            Direction.SOUTH: (0, 1),
            Direction.SOUTHWEST: (-1, 1),
            Direction.WEST: (-1, 0),
            Direction.NORTHWEST: (-1, -1)
        }
        
        # Basic 4-direction coastlines (existing system)
        self.basic_coastlines = {}
        for pattern in range(1, 16):
            self.basic_coastlines[pattern] = f"coastline_{pattern:04b}"
    
    def is_water(self, terrain: List[List], x: int, y: int) -> bool:
        """Check if a cell contains water"""
        if x < 0 or y < 0 or y >= len(terrain) or x >= len(terrain[0]):
            return False
        
        cell = terrain[y][x]
        return str(cell).lower() in ['water', 'w'] or cell == 'water'
    
    def is_land(self, terrain: List[List], x: int, y: int) -> bool:
        """Check if a cell contains land"""
        if x < 0 or y < 0 or y >= len(terrain) or x >= len(terrain[0]):
            return True  # Out of bounds = land
        
        return not self.is_water(terrain, x, y)
    
    def check_diagonal_pattern(self, terrain: List[List], x: int, y: int) -> str:
        """
        Check for diagonal coastline patterns
        Returns diagonal tile name or None
        """
        # Check all 8 neighbors
        neighbors = {}
        for direction, (dx, dy) in self.direction_offsets.items():
            nx, ny = x + dx, y + dy
            neighbors[direction] = self.is_water(terrain, nx, ny)
        
        # Northeast diagonal: North=land, East=land, NE=water
        if (not neighbors[Direction.NORTH] and 
            not neighbors[Direction.EAST] and 
            neighbors[Direction.NORTHEAST]):
            # Additional check: SW should be land for clean diagonal
            if not neighbors[Direction.SOUTHWEST]:
                return 'coastline_diagonal_ne'
        
        # Southeast diagonal: South=land, East=land, SE=water
        if (not neighbors[Direction.SOUTH] and 
            not neighbors[Direction.EAST] and 
            neighbors[Direction.SOUTHEAST]):
            # Additional check: NW should be land
            if not neighbors[Direction.NORTHWEST]:
                return 'coastline_diagonal_se'
        
        # Southwest diagonal: South=land, West=land, SW=water
        if (not neighbors[Direction.SOUTH] and 
            not neighbors[Direction.WEST] and 
            neighbors[Direction.SOUTHWEST]):
            # Additional check: NE should be land
            if not neighbors[Direction.NORTHEAST]:
                return 'coastline_diagonal_sw'
        
        # Northwest diagonal: North=land, West=land, NW=water
        if (not neighbors[Direction.NORTH] and 
            not neighbors[Direction.WEST] and 
            neighbors[Direction.NORTHWEST]):
            # Additional check: SE should be land
            if not neighbors[Direction.SOUTHEAST]:
                return 'coastline_diagonal_nw'
        
        return None
    
    def get_basic_pattern(self, terrain: List[List], x: int, y: int) -> int:
        """Get 4-direction water adjacency pattern"""
        pattern = 0
        
        # Check 4 cardinal directions
        if self.is_water(terrain, x, y - 1):  # North
            pattern |= 0b1000
        if self.is_water(terrain, x + 1, y):  # East
            pattern |= 0b0100
        if self.is_water(terrain, x, y + 1):  # South
            pattern |= 0b0010
        if self.is_water(terrain, x - 1, y):  # West
            pattern |= 0b0001
        
        return pattern
    
    def get_coastline_tile(self, terrain: List[List], x: int, y: int) -> str:
        """
        Get appropriate coastline tile for a land cell
        Prioritizes diagonal tiles over basic tiles
        """
        # This cell must be land
        if self.is_water(terrain, x, y):
            return None
        
        # First check for diagonal patterns
        diagonal_tile = self.check_diagonal_pattern(terrain, x, y)
        if diagonal_tile:
            return diagonal_tile
        
        # Fall back to basic 4-direction pattern
        pattern = self.get_basic_pattern(terrain, x, y)
        if pattern == 0:
            return None
        
        return self.basic_coastlines.get(pattern)
    
    def generate_coastline_map(self, terrain: List[List]) -> Dict[Tuple[int, int], str]:
        """Generate complete coastline mapping with diagonals"""
        coastline_map = {}
        height = len(terrain)
        width = len(terrain[0]) if height > 0 else 0
        
        for y in range(height):
            for x in range(width):
                coastline_tile = self.get_coastline_tile(terrain, x, y)
                if coastline_tile:
                    coastline_map[(x, y)] = coastline_tile
        
        return coastline_map
    
    def print_coastline_stats(self, coastline_map: Dict[Tuple[int, int], str]):
        """Print statistics including diagonal coastlines"""
        if not coastline_map:
            print("🏖️  No coastline tiles generated")
            return
        
        # Count patterns
        pattern_counts = {}
        diagonal_count = 0
        
        for tile_name in coastline_map.values():
            pattern_counts[tile_name] = pattern_counts.get(tile_name, 0) + 1
            if 'diagonal' in tile_name:
                diagonal_count += 1
        
        print(f"🏖️  Generated {len(coastline_map)} coastline tiles:")
        print(f"    - Basic coastlines: {len(coastline_map) - diagonal_count}")
        print(f"    - Diagonal coastlines: {diagonal_count}")
        
        # Show details
        for tile_name in sorted(pattern_counts.keys()):
            count = pattern_counts[tile_name]
            if 'diagonal' in tile_name:
                direction = tile_name.split('_')[-1].upper()
                print(f"  {tile_name}: {count} tiles - Diagonal {direction}")
            else:
                print(f"  {tile_name}: {count} tiles")

def test_diagonal_coastline():
    """Test diagonal coastline detection"""
    print("🧪 Testing Diagonal Coastline System")
    print("=" * 50)
    
    # Create test terrain with diagonal shore
    terrain = [
        ['land', 'land', 'land', 'land', 'water', 'water'],
        ['land', 'land', 'land', 'water', 'water', 'water'],
        ['land', 'land', 'water', 'water', 'water', 'water'],
        ['land', 'water', 'water', 'water', 'water', 'water'],
    ]
    
    # Display terrain
    print("Test terrain:")
    for row in terrain:
        print('  ' + ' '.join('L' if cell == 'land' else '~' for cell in row))
    
    system = DiagonalCoastlineSystem()
    coastline_map = system.generate_coastline_map(terrain)
    
    print("\nCoastline detection:")
    for y in range(len(terrain)):
        row_str = ""
        for x in range(len(terrain[0])):
            if terrain[y][x] == 'water':
                row_str += '~ '
            else:
                tile = coastline_map.get((x, y))
                if tile and 'diagonal' in tile:
                    if 'ne' in tile: row_str += '╱ '
                    elif 'se' in tile: row_str += '╲ '
                    elif 'sw' in tile: row_str += '╱ '
                    elif 'nw' in tile: row_str += '╲ '
                elif tile:
                    row_str += '│ '
                else:
                    row_str += 'L '
        print(f"  {row_str}")
    
    system.print_coastline_stats(coastline_map)

if __name__ == "__main__":
    test_diagonal_coastline()