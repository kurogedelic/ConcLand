#!/usr/bin/env python3
"""
Coastline System for ConcLand Mini - Redesigned Algorithm
Based on actual asset analysis and proper understanding of coastline mechanics
"""

from typing import List, Dict, Tuple, Set
from enum import IntEnum

class Direction(IntEnum):
    NORTH = 0
    EAST = 1  
    SOUTH = 2
    WEST = 3

class CoastlineSystem:
    def __init__(self):
        """
        New coastline algorithm based on proper understanding:
        
        File naming convention analysis:
        coastline_NESW.png where each bit represents:
        - 1 = this direction has coastline/shore
        - 0 = this direction is interior/no shore
        
        So coastline_0001 = coastline on WEST side only
        coastline_1100 = coastline on NORTH and EAST sides
        """
        
        # Direction bit positions (NESW order)
        self.direction_bits = {
            Direction.NORTH: 0b1000,  # Bit 3
            Direction.EAST:  0b0100,  # Bit 2  
            Direction.SOUTH: 0b0010,  # Bit 1
            Direction.WEST:  0b0001,  # Bit 0
        }
        
        # Direction offsets for neighbor checking
        self.direction_offsets = {
            Direction.NORTH: (0, -1),
            Direction.EAST: (1, 0),
            Direction.SOUTH: (0, 1), 
            Direction.WEST: (-1, 0)
        }
        
        # Available coastline patterns (1-15, no 0)
        self.available_patterns = set(range(1, 16))
    
    def is_water(self, terrain: List[List], x: int, y: int) -> bool:
        """Check if a cell contains water"""
        if x < 0 or y < 0 or y >= len(terrain) or x >= len(terrain[0]):
            return False  # Out of bounds = land
        
        cell = terrain[y][x]
        return str(cell).lower() in ['water', 'w'] or cell == 'water'
    
    def get_coastline_pattern(self, terrain: List[List], x: int, y: int) -> int:
        """
        Determine coastline pattern for a land cell
        Returns 4-bit pattern indicating which directions need coastline
        """
        # This cell must be land
        if self.is_water(terrain, x, y):
            return 0
        
        coastline_pattern = 0
        
        # Check each direction for water adjacency
        for direction in Direction:
            dx, dy = self.direction_offsets[direction]
            neighbor_x, neighbor_y = x + dx, y + dy
            
            # If neighbor is water, this direction needs coastline
            if self.is_water(terrain, neighbor_x, neighbor_y):
                coastline_pattern |= self.direction_bits[direction]
        
        return coastline_pattern
    
    def get_coastline_tile(self, terrain: List[List], x: int, y: int) -> str:
        """
        Get appropriate coastline tile for a land cell
        Returns tile name or None if not coastline
        """
        pattern = self.get_coastline_pattern(terrain, x, y)
        
        if pattern == 0:
            return None  # No water adjacent = no coastline needed
        
        # Convert pattern to binary string
        binary_str = f"{pattern:04b}"
        return f"coastline_{binary_str}"
    
    def generate_coastline_map(self, terrain: List[List]) -> Dict[Tuple[int, int], str]:
        """
        Generate complete coastline mapping for terrain
        Returns: {(x, y): coastline_tile_name}
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
    
    def analyze_pattern(self, pattern: int) -> Dict[str, any]:
        """Analyze a coastline pattern for debugging"""
        analysis = {
            'pattern': pattern,
            'binary': f"{pattern:04b}",
            'tile': f"coastline_{pattern:04b}",
            'directions': [],
            'description': ''
        }
        
        # Determine which directions have coastline
        if pattern & self.direction_bits[Direction.NORTH]:
            analysis['directions'].append('North')
        if pattern & self.direction_bits[Direction.EAST]:
            analysis['directions'].append('East')
        if pattern & self.direction_bits[Direction.SOUTH]:
            analysis['directions'].append('South')
        if pattern & self.direction_bits[Direction.WEST]:
            analysis['directions'].append('West')
        
        # Generate description
        if len(analysis['directions']) == 1:
            analysis['description'] = f"Simple coastline facing {analysis['directions'][0].lower()}"
        elif len(analysis['directions']) == 2:
            dirs = analysis['directions']
            if ('North' in dirs and 'South' in dirs) or ('East' in dirs and 'West' in dirs):
                analysis['description'] = f"Strait coastline: {' & '.join(dirs).lower()}"
            else:
                analysis['description'] = f"Corner coastline: {' & '.join(dirs).lower()}"
        elif len(analysis['directions']) == 3:
            analysis['description'] = f"Peninsula coastline: {', '.join(analysis['directions']).lower()}"
        elif len(analysis['directions']) == 4:
            analysis['description'] = "Island coastline (all directions)"
        
        return analysis
    
    def print_coastline_stats(self, coastline_map: Dict[Tuple[int, int], str]):
        """Print statistics about generated coastlines"""
        if not coastline_map:
            print("🏖️  No coastline tiles generated")
            return
        
        # Count patterns
        pattern_counts = {}
        for tile_name in coastline_map.values():
            pattern_counts[tile_name] = pattern_counts.get(tile_name, 0) + 1
        
        print(f"🏖️  Generated {len(coastline_map)} coastline tiles:")
        
        # Sort and display with analysis
        for tile_name in sorted(pattern_counts.keys()):
            count = pattern_counts[tile_name]
            # Extract pattern from tile name
            pattern_str = tile_name.split('_')[1]
            pattern = int(pattern_str, 2)
            analysis = self.analyze_pattern(pattern)
            
            print(f"  {tile_name}: {count} tiles - {analysis['description']}")
    
    def visualize_pattern(self, pattern: int, show_analysis: bool = True) -> str:
        """Create ASCII visualization of coastline pattern"""
        # Create 3x3 grid
        grid = [['.' for _ in range(3)] for _ in range(3)]
        
        # Center is the land cell with coastline
        grid[1][1] = 'L'
        
        # Mark water directions
        if pattern & self.direction_bits[Direction.NORTH]:
            grid[0][1] = '~'  # North = water
        if pattern & self.direction_bits[Direction.EAST]:
            grid[1][2] = '~'  # East = water
        if pattern & self.direction_bits[Direction.SOUTH]:
            grid[2][1] = '~'  # South = water
        if pattern & self.direction_bits[Direction.WEST]:
            grid[1][0] = '~'  # West = water
        
        # Convert to string
        result = []
        for row in grid:
            result.append(''.join(row))
        
        if show_analysis:
            analysis = self.analyze_pattern(pattern)
            result.append(f"Pattern: {analysis['binary']} - {analysis['description']}")
        
        return '\n'.join(result)

def test_new_coastline_system():
    """Test the new coastline system"""
    print("🧪 Testing New Coastline System")
    print("=" * 50)
    
    # Create test terrain
    terrain = [
        ['land', 'land', 'land', 'land', 'land'],
        ['land', 'water', 'water', 'water', 'land'],
        ['land', 'water', 'land', 'water', 'land'],
        ['land', 'water', 'water', 'water', 'land'],
        ['land', 'land', 'land', 'land', 'land']
    ]
    
    coastline_system = CoastlineSystem()
    coastline_map = coastline_system.generate_coastline_map(terrain)
    coastline_system.print_coastline_stats(coastline_map)
    
    print("\n🎯 Pattern Examples:")
    example_patterns = [
        0b0001,  # West coastline
        0b0100,  # East coastline  
        0b0011,  # South+West corner
        0b1100,  # North+East corner
        0b1111   # All directions (island)
    ]
    
    for pattern in example_patterns:
        print(f"\nPattern {pattern:04b}:")
        print(coastline_system.visualize_pattern(pattern))
        print("-" * 20)

if __name__ == "__main__":
    test_new_coastline_system()