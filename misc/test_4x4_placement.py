#!/usr/bin/env python3
"""Test if 4x4 buildings are placed correctly"""

import pyxel
from concland_mini import ConcLandMini, CellType

class Test4x4Placement:
    def __init__(self):
        pyxel.init(320, 240)
        self.game = ConcLandMini()
        
        # Place a coal plant at (10, 10)
        print("\n=== Testing 4x4 Coal Plant Placement ===")
        if self.game._can_place_4x4_building(10, 10):
            self.game._place_4x4_building(10, 10, CellType.COAL_PLANT)
            print(f"✓ Placed coal plant at (10, 10)")
            
            # Check if all 16 cells are occupied
            occupied_cells = []
            for dy in range(4):
                for dx in range(4):
                    x, y = 10 + dx, 10 + dy
                    cell_type = self.game.grid[y][x]
                    if cell_type == CellType.COAL_PLANT:
                        occupied_cells.append((x, y))
            
            print(f"Occupied cells: {len(occupied_cells)}/16")
            if len(occupied_cells) == 16:
                print("✓ All 16 cells (4x4) are correctly occupied")
            else:
                print(f"✗ Only {len(occupied_cells)} cells occupied, expected 16")
                print(f"Occupied positions: {occupied_cells}")
        else:
            print("✗ Cannot place coal plant at (10, 10)")
        
        pyxel.run(self.update, self.draw)
    
    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
    
    def draw(self):
        pyxel.cls(0)
        
        # Draw title
        pyxel.text(10, 10, "4x4 Placement Test", 7)
        
        # Show grid around (10, 10)
        start_x, start_y = 50, 50
        cell_size = 8
        
        for dy in range(8):
            for dx in range(8):
                x = start_x + dx * cell_size
                y = start_y + dy * cell_size
                grid_x = 8 + dx
                grid_y = 8 + dy
                
                # Draw cell border
                pyxel.rectb(x, y, cell_size, cell_size, 1)
                
                # Highlight coal plant cells
                if 10 <= grid_x < 14 and 10 <= grid_y < 14:
                    if self.game.grid[grid_y][grid_x] == CellType.COAL_PLANT:
                        pyxel.rect(x, y, cell_size, cell_size, 2)  # Purple for coal plant
                    else:
                        pyxel.rect(x, y, cell_size, cell_size, 8)  # Red if not occupied
        
        # Draw expected 4x4 area outline
        expected_x = start_x + 2 * cell_size  # (10-8) * 8
        expected_y = start_y + 2 * cell_size  # (10-8) * 8
        pyxel.rectb(expected_x, expected_y, 32, 32, 11)  # Green outline for expected 4x4
        
        pyxel.text(10, 150, "Purple = Coal Plant cells", 2)
        pyxel.text(10, 160, "Red = Should be occupied but isn't", 8)
        pyxel.text(10, 170, "Green outline = Expected 4x4 area", 11)
        pyxel.text(10, 190, "Press Q to quit", 7)

if __name__ == "__main__":
    Test4x4Placement()