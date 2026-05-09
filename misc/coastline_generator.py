#!/usr/bin/env python3
"""
Coastline Generator for ConcLand Mini
Generates appropriate coastline tiles based on water/land adjacency
"""

from typing import List, Dict, Tuple
from enum import IntEnum

class Direction(IntEnum):
    NORTH = 0
    EAST = 1  
    SOUTH = 2
    WEST = 3

class CoastlineGenerator:
    def __init__(self):
        # Coastline pattern mapping: water adjacency pattern -> tile name
        # After testing: complete bit inversion is needed
        # File naming appears to be inverted from water pattern
        self.coastline_patterns = {}
        
        # Generate all patterns by completely inverting water patterns
        for water_pattern in range(1, 16):  # 1 to 15 (exclude 0 = no water)
            # Complete bit inversion
            inverted_pattern = (~water_pattern) & 0b1111  # Invert and mask to 4 bits
            inverted_binary = f"{inverted_pattern:04b}"
            
            # Handle special case: coastline_0000 doesn't exist
            if inverted_binary == "0000":
                tile_name = "coastline_1111"  # Use full coastline as fallback
            else:
                tile_name = f"coastline_{inverted_binary}"
                
            self.coastline_patterns[water_pattern] = tile_name
        
        # Direction offsets for checking neighbors
        self.direction_offsets = {
            Direction.NORTH: (0, -1),
            Direction.EAST: (1, 0),
            Direction.SOUTH: (0, 1), 
            Direction.WEST: (-1, 0)
        }
    
    def is_water(self, terrain: List[List], x: int, y: int) -> bool:
        """Check if a cell contains water (handle bounds checking)"""
        if x < 0 or y < 0 or y >= len(terrain) or x >= len(terrain[0]):
            return False  # Out of bounds treated as land
        
        # Check if this cell is water (you may need to adjust this based on your terrain enum)
        return terrain[y][x] == 'water' or str(terrain[y][x]).lower().endswith('water')
    
    def get_water_adjacency_pattern(self, terrain: List[List], x: int, y: int) -> int:
        """
        Get 4-bit pattern representing water adjacency
        Returns integer where bits represent: North, East, South, West
        """
        pattern = 0
        
        for direction in Direction:
            dx, dy = self.direction_offsets[direction]
            neighbor_x, neighbor_y = x + dx, y + dy
            
            if self.is_water(terrain, neighbor_x, neighbor_y):
                pattern |= (1 << (3 - direction))  # Set bit for this direction
        
        return pattern
    
    def get_coastline_tile(self, terrain: List[List], x: int, y: int) -> str:
        """
        Get appropriate coastline tile for a land cell adjacent to water
        Returns tile name or None if not a coastline cell
        """
        # This cell must be land
        if self.is_water(terrain, x, y):
            return None
        
        # Check if adjacent to any water
        water_pattern = self.get_water_adjacency_pattern(terrain, x, y)
        
        if water_pattern == 0:
            return None  # Not adjacent to water
        
        # Use the corrected mapping table
        return self.coastline_patterns.get(water_pattern, 'coastline_0001')
    
    def generate_coastline_map(self, terrain: List[List]) -> Dict[Tuple[int, int], str]:
        """
        Generate coastline tile mapping for entire terrain
        Returns dictionary: (x, y) -> coastline_tile_name
        """
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
        """Print statistics about coastline generation"""
        if not coastline_map:
            print("🏖️  No coastline tiles generated")
            return
        
        # Count different coastline patterns
        pattern_counts = {}
        for tile_name in coastline_map.values():
            pattern_counts[tile_name] = pattern_counts.get(tile_name, 0) + 1
        
        print(f"🏖️  Generated {len(coastline_map)} coastline tiles:")
        for pattern, count in sorted(pattern_counts.items()):
            # Extract binary pattern from filename
            binary = pattern.split('_')[1]
            print(f"  {pattern} ({binary}): {count} tiles")
    
    def visualize_coastline_pattern(self, pattern: int) -> str:
        """
        Create ASCII visualization of a coastline pattern
        """
        # Create 3x3 grid showing water (~) and land (#) pattern
        grid = [['#' for _ in range(3)] for _ in range(3)]
        
        # Center is always land for coastline
        grid[1][1] = 'C'  # C for coastline
        
        # Check each direction
        if pattern & 0b1000:  # North
            grid[0][1] = '~'
        if pattern & 0b0100:  # East  
            grid[1][2] = '~'
        if pattern & 0b0010:  # South
            grid[2][1] = '~'
        if pattern & 0b0001:  # West
            grid[1][0] = '~'
        
        # Convert to string
        result = []
        for row in grid:
            result.append(''.join(row))
        
        return '\n'.join(result)

def test_coastline_generator():
    """Test the coastline generator with sample terrain"""
    print("🧪 Testing Coastline Generator")
    
    # Create sample terrain (simple water body)
    terrain = [
        ['land', 'land', 'land', 'land', 'land'],
        ['land', 'water', 'water', 'water', 'land'],
        ['land', 'water', 'water', 'water', 'land'], 
        ['land', 'water', 'water', 'water', 'land'],
        ['land', 'land', 'land', 'land', 'land']
    ]
    
    generator = CoastlineGenerator()
    coastline_map = generator.generate_coastline_map(terrain)
    generator.print_coastline_stats(coastline_map)
    
    print("\n🗺️  Sample coastline patterns:")
    
    # Show a few example patterns
    example_patterns = [0b0001, 0b0011, 0b1111]
    for pattern in example_patterns:
        tile_name = generator.coastline_patterns.get(pattern)
        binary_str = f"{pattern:04b}"
        print(f"\nPattern {binary_str} ({tile_name}):")
        print(generator.visualize_coastline_pattern(pattern))

if __name__ == "__main__":
    test_coastline_generator()