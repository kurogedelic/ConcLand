#!/usr/bin/env python3
"""Simple test to check if 4x4 grid placement works"""

# Test without initializing the game
MAP_SIZE = 64

class SimpleTest:
    def __init__(self):
        self.grid = [["." for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
    
    def place_4x4(self, x, y, symbol):
        """Place a 4x4 building"""
        for dy in range(4):
            for dx in range(4):
                self.grid[y + dy][x + dx] = symbol
    
    def check_4x4(self, x, y, symbol):
        """Check if 4x4 area is filled with symbol"""
        count = 0
        for dy in range(4):
            for dx in range(4):
                if self.grid[y + dy][x + dx] == symbol:
                    count += 1
        return count
    
    def print_area(self, x, y, width, height):
        """Print a portion of the grid"""
        for dy in range(height):
            row = ""
            for dx in range(width):
                row += self.grid[y + dy][x + dx]
            print(row)

# Test
test = SimpleTest()
print("=== Testing 4x4 Placement Logic ===")
print("\nBefore placing coal plant:")
test.print_area(8, 8, 8, 8)

# Place a 4x4 coal plant at (10, 10)
test.place_4x4(10, 10, "C")

print("\nAfter placing 4x4 coal plant at (10,10):")
test.print_area(8, 8, 8, 8)

count = test.check_4x4(10, 10, "C")
print(f"\nCoal plant cells occupied: {count}/16")

if count == 16:
    print("✓ 4x4 placement logic is correct")
else:
    print("✗ 4x4 placement logic has issues")