"""
RCI Zone Growth Fix for ConcLand
Ensures RCI zones properly reserve 3x3 areas for development
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import random

class CellType(Enum):
    """Cell types matching main game"""
    EMPTY = 0
    WATER = 1
    RESIDENTIAL = 2
    COMMERCIAL = 3
    INDUSTRIAL = 4
    ROAD = 5
    RAIL = 6
    WIRE = 7
    PARK = 8
    WASTELAND = 9
    # Add other types as needed

@dataclass
class RCIZoneReservation:
    """Manages 3x3 zone reservations for RCI development"""
    center_x: int
    center_y: int
    zone_type: CellType
    building_id: int
    reserved_tiles: List[Tuple[int, int]]
    
class RCIZoneManager:
    """Manages RCI zone placement and growth with proper 3x3 reservations"""
    
    def __init__(self, map_size: int):
        self.map_size = map_size
        self.zone_reservations: Dict[int, RCIZoneReservation] = {}  # building_id -> reservation
        self.tile_to_reservation: Dict[Tuple[int, int], int] = {}  # (x, y) -> building_id
        self.next_building_id = 1000
    
    def can_place_rci_zone(self, x: int, y: int, grid, zone_type: CellType) -> bool:
        """Check if RCI zone can be placed with 3x3 reservation"""
        # Find best 3x3 area that includes this position
        best_center = self._find_best_3x3_center(x, y, grid)
        
        if best_center is None:
            # No valid 3x3 area available
            return False
        
        cx, cy = best_center
        
        # Check if entire 3x3 area is available for reservation
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                check_x = cx + dx
                check_y = cy + dy
                
                # Out of bounds
                if not (0 <= check_x < self.map_size and 0 <= check_y < self.map_size):
                    return False
                
                # Check if tile is already reserved
                if (check_x, check_y) in self.tile_to_reservation:
                    return False
                
                # Check if tile is available (empty, wasteland, or same zone type)
                current_type = grid[check_y][check_x]
                if current_type not in [CellType.EMPTY, CellType.WASTELAND, zone_type]:
                    # Don't allow placement if non-compatible building exists
                    if current_type not in [CellType.ROAD, CellType.RAIL, CellType.WIRE]:
                        return False
        
        return True
    
    def _find_best_3x3_center(self, x: int, y: int, grid) -> Optional[Tuple[int, int]]:
        """Find the best center point for a 3x3 zone that includes the given position"""
        # Try different center positions that would include (x, y) in the 3x3 area
        possible_centers = []
        
        for cy in range(max(1, y - 1), min(self.map_size - 1, y + 2)):
            for cx in range(max(1, x - 1), min(self.map_size - 1, x + 2)):
                # Check if (x, y) is within this 3x3 area
                if abs(cx - x) <= 1 and abs(cy - y) <= 1:
                    # Check if this center is valid (not too close to edges)
                    if 1 <= cx < self.map_size - 1 and 1 <= cy < self.map_size - 1:
                        score = self._score_3x3_area(cx, cy, grid)
                        if score >= 0:  # Valid area
                            possible_centers.append((cx, cy, score))
        
        if not possible_centers:
            return None
        
        # Sort by score (higher is better) and return best center
        possible_centers.sort(key=lambda c: c[2], reverse=True)
        return (possible_centers[0][0], possible_centers[0][1])
    
    def _score_3x3_area(self, cx: int, cy: int, grid) -> float:
        """Score a 3x3 area for RCI placement (higher is better, -1 if invalid)"""
        score = 0.0
        empty_count = 0
        
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                check_x = cx + dx
                check_y = cy + dy
                
                # Out of bounds
                if not (0 <= check_x < self.map_size and 0 <= check_y < self.map_size):
                    return -1
                
                # Already reserved
                if (check_x, check_y) in self.tile_to_reservation:
                    return -1
                
                cell_type = grid[check_y][check_x]
                
                # Water or incompatible building
                if cell_type == CellType.WATER:
                    return -1
                elif cell_type in [CellType.EMPTY, CellType.WASTELAND]:
                    empty_count += 1
                    score += 1.0
                elif cell_type in [CellType.ROAD, CellType.RAIL, CellType.WIRE]:
                    # Infrastructure - lower score but still valid
                    score += 0.5
                elif cell_type in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL]:
                    # Existing RCI - can merge
                    score += 0.8
                else:
                    # Other buildings block placement
                    return -1
        
        # Prefer areas with more empty space
        score += empty_count * 0.5
        
        # Prefer central positions
        distance_from_center = abs(cx - self.map_size // 2) + abs(cy - self.map_size // 2)
        score -= distance_from_center * 0.01
        
        return score
    
    def place_rci_zone(self, x: int, y: int, grid, sim_data, zone_type: CellType) -> Optional[int]:
        """Place RCI zone with 3x3 reservation"""
        # Find best 3x3 center
        best_center = self._find_best_3x3_center(x, y, grid)
        
        if best_center is None:
            return None
        
        cx, cy = best_center
        
        # Create new building ID
        building_id = self.next_building_id
        self.next_building_id += 1
        
        # Reserve the 3x3 area
        reserved_tiles = []
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                tile_x = cx + dx
                tile_y = cy + dy
                reserved_tiles.append((tile_x, tile_y))
                self.tile_to_reservation[(tile_x, tile_y)] = building_id
                
                # Update sim_data with building_id
                if hasattr(sim_data[tile_y][tile_x], 'building_id'):
                    sim_data[tile_y][tile_x].building_id = building_id
        
        # Create reservation
        reservation = RCIZoneReservation(
            center_x=cx,
            center_y=cy,
            zone_type=zone_type,
            building_id=building_id,
            reserved_tiles=reserved_tiles
        )
        self.zone_reservations[building_id] = reservation
        
        # Place the initial zone tile at the requested position
        grid[y][x] = zone_type
        
        return building_id
    
    def can_develop_zone(self, building_id: int, grid) -> bool:
        """Check if a zone can develop into full 3x3 building"""
        if building_id not in self.zone_reservations:
            return False
        
        reservation = self.zone_reservations[building_id]
        
        # Check all reserved tiles are still available
        for tile_x, tile_y in reservation.reserved_tiles:
            cell_type = grid[tile_y][tile_x]
            
            # Allow if empty, wasteland, or same zone type
            if cell_type not in [CellType.EMPTY, CellType.WASTELAND, reservation.zone_type]:
                # Infrastructure is okay if zone has road access
                if cell_type not in [CellType.ROAD, CellType.RAIL, CellType.WIRE]:
                    return False
        
        return True
    
    def develop_zone(self, building_id: int, grid, sim_data, density: int = 1):
        """Develop a reserved zone into full 3x3 building"""
        if building_id not in self.zone_reservations:
            return False
        
        reservation = self.zone_reservations[building_id]
        
        # Place zone type in all reserved tiles
        for tile_x, tile_y in reservation.reserved_tiles:
            # Preserve roads at edges if they exist
            current_type = grid[tile_y][tile_x]
            
            # Keep infrastructure at zone edges for access
            is_edge = (abs(tile_x - reservation.center_x) == 1 or 
                      abs(tile_y - reservation.center_y) == 1)
            
            if is_edge and current_type in [CellType.ROAD, CellType.RAIL]:
                # Keep the road/rail for access but mark as part of zone
                if hasattr(sim_data[tile_y][tile_x], 'zone_underneath'):
                    sim_data[tile_y][tile_x].zone_underneath = reservation.zone_type
            else:
                # Place the zone
                grid[tile_y][tile_x] = reservation.zone_type
            
            # Update density
            if hasattr(sim_data[tile_y][tile_x], 'density'):
                sim_data[tile_y][tile_x].density = density
            
            # Ensure building_id is set
            if hasattr(sim_data[tile_y][tile_x], 'building_id'):
                sim_data[tile_y][tile_x].building_id = building_id
        
        return True
    
    def get_zone_info(self, x: int, y: int) -> Optional[RCIZoneReservation]:
        """Get zone reservation info for a tile"""
        building_id = self.tile_to_reservation.get((x, y))
        if building_id:
            return self.zone_reservations.get(building_id)
        return None
    
    def remove_zone(self, x: int, y: int, grid, sim_data):
        """Remove a zone and its reservation"""
        # Get building ID for this tile
        building_id = self.tile_to_reservation.get((x, y))
        
        if building_id and building_id in self.zone_reservations:
            reservation = self.zone_reservations[building_id]
            
            # Clear all reserved tiles
            for tile_x, tile_y in reservation.reserved_tiles:
                if (tile_x, tile_y) in self.tile_to_reservation:
                    del self.tile_to_reservation[(tile_x, tile_y)]
                
                # Clear grid
                if grid[tile_y][tile_x] == reservation.zone_type:
                    grid[tile_y][tile_x] = CellType.EMPTY
                
                # Clear sim_data
                if hasattr(sim_data[tile_y][tile_x], 'building_id'):
                    sim_data[tile_y][tile_x].building_id = 0
                if hasattr(sim_data[tile_y][tile_x], 'density'):
                    sim_data[tile_y][tile_x].density = 0
                if hasattr(sim_data[tile_y][tile_x], 'population'):
                    sim_data[tile_y][tile_x].population = 0
            
            # Remove reservation
            del self.zone_reservations[building_id]
    
    def merge_adjacent_zones(self, grid, sim_data):
        """Merge adjacent single RCI zones into 3x3 developments"""
        merged = []
        
        # Find all single RCI tiles without reservations
        single_zones = []
        for y in range(self.map_size):
            for x in range(self.map_size):
                cell_type = grid[y][x]
                if cell_type in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL]:
                    if (x, y) not in self.tile_to_reservation:
                        single_zones.append((x, y, cell_type))
        
        # Try to merge groups of 9 adjacent zones
        processed = set()
        for x, y, zone_type in single_zones:
            if (x, y) in processed:
                continue
            
            # Check for 3x3 group
            adjacent_tiles = []
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    check_x = x + dx
                    check_y = y + dy
                    
                    if 0 <= check_x < self.map_size and 0 <= check_y < self.map_size:
                        if grid[check_y][check_x] == zone_type:
                            if (check_x, check_y) not in self.tile_to_reservation:
                                adjacent_tiles.append((check_x, check_y))
            
            # If we have 9 adjacent tiles, merge them
            if len(adjacent_tiles) >= 9:
                # Create a new reservation
                center_x = x
                center_y = y
                building_id = self.place_rci_zone(x, y, grid, sim_data, zone_type)
                
                if building_id:
                    # Mark tiles as processed
                    for tile in adjacent_tiles[:9]:
                        processed.add(tile)
                    
                    merged.append((center_x, center_y, zone_type))
        
        return merged

def integrate_rci_fix(game_instance):
    """Integrate RCI zone fix into existing game"""
    
    # Create zone manager
    zone_manager = RCIZoneManager(game_instance.MAP_SIZE)
    game_instance.zone_manager = zone_manager
    
    # Override place building method
    original_place = game_instance._place_building
    
    def enhanced_place_building():
        x, y = game_instance.cursor_x, game_instance.cursor_y
        item = game_instance.current_item
        
        # Map item to cell type
        item_to_cell = {
            'RESIDENTIAL': CellType.RESIDENTIAL,
            'COMMERCIAL': CellType.COMMERCIAL,
            'INDUSTRIAL': CellType.INDUSTRIAL
        }
        
        # Check if placing RCI zone
        if str(item) in item_to_cell:
            zone_type = item_to_cell[str(item)]
            
            # Use zone manager for placement
            if zone_manager.can_place_rci_zone(x, y, game_instance.grid, zone_type):
                building_id = zone_manager.place_rci_zone(
                    x, y, 
                    game_instance.grid, 
                    game_instance.sim_data,
                    zone_type
                )
                
                if building_id:
                    # Deduct cost
                    cost = game_instance._get_building_cost(item)
                    if not game_instance.infinite_funds:
                        game_instance.funds -= cost
                    return True
            return False
        else:
            # Use original method for non-RCI buildings
            return original_place()
    
    game_instance._place_building = enhanced_place_building
    
    # Add zone development to update cycle
    original_update = game_instance._update_rci_zones
    
    def enhanced_update_rci():
        # Run original update
        original_update()
        
        # Check for zone development
        for building_id, reservation in zone_manager.zone_reservations.items():
            if zone_manager.can_develop_zone(building_id, game_instance.grid):
                # Check if zone has enough population to develop
                cx, cy = reservation.center_x, reservation.center_y
                
                if hasattr(game_instance.sim_data[cy][cx], 'population'):
                    pop = game_instance.sim_data[cy][cx].population
                    
                    # Develop based on population thresholds
                    if pop >= 100:
                        density = 1 if pop < 500 else 2 if pop < 1000 else 3 if pop < 2000 else 4
                        zone_manager.develop_zone(
                            building_id,
                            game_instance.grid,
                            game_instance.sim_data,
                            density
                        )
    
    game_instance._update_rci_zones = enhanced_update_rci
    
    return zone_manager

# Example test
def test_rci_zone_manager():
    """Test the RCI zone manager"""
    
    # Create test grid
    map_size = 20
    grid = [[CellType.EMPTY for _ in range(map_size)] for _ in range(map_size)]
    
    # Create mock sim_data
    class MockSimData:
        def __init__(self):
            self.building_id = 0
            self.density = 0
            self.population = 0
    
    sim_data = [[MockSimData() for _ in range(map_size)] for _ in range(map_size)]
    
    # Create manager
    manager = RCIZoneManager(map_size)
    
    # Test placement
    print("Testing RCI zone placement...")
    
    # Place a residential zone
    building_id = manager.place_rci_zone(5, 5, grid, sim_data, CellType.RESIDENTIAL)
    print(f"Placed residential zone with building_id: {building_id}")
    
    # Check reservation
    info = manager.get_zone_info(5, 5)
    if info:
        print(f"Zone center: ({info.center_x}, {info.center_y})")
        print(f"Reserved tiles: {len(info.reserved_tiles)}")
    
    # Test if another zone can be placed nearby (should fail if overlapping)
    can_place = manager.can_place_rci_zone(6, 6, grid, CellType.COMMERCIAL)
    print(f"Can place commercial at (6, 6): {can_place}")
    
    # Test if zone can be placed further away
    can_place = manager.can_place_rci_zone(10, 10, grid, CellType.COMMERCIAL)
    print(f"Can place commercial at (10, 10): {can_place}")
    
    # Develop the zone
    if building_id:
        success = manager.develop_zone(building_id, grid, sim_data, density=2)
        print(f"Zone developed: {success}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_rci_zone_manager()