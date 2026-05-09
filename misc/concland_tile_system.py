"""
Tile loading and connection system for ConcLand Mini
Loads PNG tile assets and handles road/rail connection logic
"""

import pyxel
import os
from typing import Dict, Tuple, Optional

class ConcLandTileManager:
    def __init__(self):
        self.tiles = {}
        self.tile_size = 16  # 16x16 tiles for ConcLand Mini
        self.image_bank = 0
        
        # Tile positions in the tilemap
        # Format: {tile_id: (x, y, width, height)}
        self._define_tile_positions()
        
    def _define_tile_positions(self):
        """Define tile positions in the tilemap"""
        # Basic terrain tiles
        self.tiles['empty'] = (0, 0)
        self.tiles['grass'] = (16, 0)
        self.tiles['water'] = (32, 0)
        
        # Residential tiles (3x3 displayed as scaled single tile)
        self.tiles['residential_1'] = (0, 16)
        self.tiles['residential_2'] = (16, 16)
        self.tiles['residential_3'] = (32, 16)
        self.tiles['residential_4'] = (48, 16)
        
        # Commercial tiles (3x3 displayed as scaled single tile)
        self.tiles['commercial_1'] = (0, 32)
        self.tiles['commercial_2'] = (16, 32)
        self.tiles['commercial_3'] = (32, 32)
        self.tiles['commercial_4'] = (48, 32)
        
        # Industrial tiles (3x3 displayed as scaled single tile)
        self.tiles['industrial_1'] = (0, 48)
        self.tiles['industrial_2'] = (16, 48)
        self.tiles['industrial_3'] = (32, 48)
        self.tiles['industrial_4'] = (48, 48)
        
        # Road tiles (1x1 with connection patterns)
        road_y = 64
        self.tiles['road_alone'] = (0, road_y)
        self.tiles['road_horizontal'] = (16, road_y)
        self.tiles['road_vertical'] = (32, road_y)
        self.tiles['road_corner_ne'] = (48, road_y)
        self.tiles['road_corner_se'] = (64, road_y)
        self.tiles['road_corner_sw'] = (80, road_y)
        self.tiles['road_corner_nw'] = (96, road_y)
        self.tiles['road_cross'] = (112, road_y)
        self.tiles['road_t_north'] = (128, road_y)
        self.tiles['road_t_south'] = (144, road_y)
        self.tiles['road_t_east'] = (160, road_y)
        self.tiles['road_t_west'] = (176, road_y)
        
        # Rail tiles (1x1 with connection patterns)
        rail_y = 80
        self.tiles['rail_alone'] = (0, rail_y)
        self.tiles['rail_horizontal'] = (16, rail_y)
        self.tiles['rail_vertical'] = (32, rail_y)
        self.tiles['rail_corner_ne'] = (48, rail_y)
        self.tiles['rail_corner_se'] = (64, rail_y)
        self.tiles['rail_corner_sw'] = (80, rail_y)
        self.tiles['rail_corner_nw'] = (96, rail_y)
        self.tiles['rail_cross'] = (112, rail_y)
        
        # Infrastructure tiles
        self.tiles['wire'] = (0, 96)
        self.tiles['park'] = (16, 96)
        
        # Power plant tiles (3x3)
        self.tiles['coal_plant'] = (0, 112)
        self.tiles['oil_plant'] = (16, 112)
        self.tiles['nuclear_plant'] = (32, 112)
        
        # Public service tiles (3x3)
        self.tiles['police'] = (0, 128)
        self.tiles['fire'] = (16, 128)
        self.tiles['hospital'] = (32, 128)
        self.tiles['school'] = (48, 128)
        
    def load_tilemap(self, tilemap_path: str):
        """Load the tilemap PNG file with VSCode compatibility"""
        # Try relative path first
        if os.path.exists(tilemap_path):
            try:
                pyxel.images[self.image_bank].load(0, 0, tilemap_path)
                print(f"Successfully loaded tilemap (relative): {tilemap_path}")
                # Verify the image was actually loaded
                if self._verify_image_loaded():
                    return True
                else:
                    print("Image loaded but no data found (relative)")
            except Exception as e:
                print(f"Relative path failed: {e}")
                
        # Try absolute path as fallback (VSCode compatibility)
        try:
            abs_path = os.path.abspath(tilemap_path)
            if os.path.exists(abs_path):
                pyxel.images[self.image_bank].load(0, 0, abs_path)
                print(f"Successfully loaded tilemap (absolute): {abs_path}")
                # Verify the image was actually loaded
                if self._verify_image_loaded():
                    return True
                else:
                    print("Image loaded but no data found")
        except Exception as e:
            print(f"Absolute path failed: {e}")
        
        print(f"Failed to load tilemap: {tilemap_path}")
        return False
    
    def _verify_image_loaded(self):
        """Verify that image data was actually loaded"""
        try:
            # Check if we can read pixels from the image
            for y in range(5):
                for x in range(5):
                    pixel = pyxel.images[self.image_bank].pget(x, y)
                    if pixel != 0:  # Found non-black pixel
                        print(f"Verified: Found pixel {pixel} at ({x},{y})")
                        return True
            print("Warning: Only black pixels found in image")
            return True  # Still consider it loaded, might be intentional
        except Exception as e:
            print(f"Image verification failed: {e}")
            return False
        
    def draw_tile(self, tile_id: str, x: int, y: int, transparent_color=None):
        """Draw a tile at the specified position (tile_id first like original project)"""
        if tile_id not in self.tiles:
            print(f"WARNING: Tile '{tile_id}' not found in tiles dict")
            # Draw fallback colored rectangle
            pyxel.rect(x, y, self.tile_size, self.tile_size, 8)  # Red for missing tiles
            pyxel.text(x + 2, y + 2, "?", 7)
            return
            
        tile_pos = self.tiles[tile_id]
        
        # Validate coordinates
        if not isinstance(tile_pos, (tuple, list)) or len(tile_pos) < 2:
            print(f"ERROR: Invalid tile position for '{tile_id}': {tile_pos}")
            pyxel.rect(x, y, self.tile_size, self.tile_size, 8)
            return
            
        try:
            # Ensure all parameters are integers
            src_x = int(tile_pos[0])
            src_y = int(tile_pos[1])
            dst_x = int(x)
            dst_y = int(y)
            width = int(self.tile_size)
            height = int(self.tile_size)
            
            # Draw the tile
            # For tile graphics, we usually don't want transparency
            # Use None/no transparency parameter to show all pixels
            if transparent_color is None:
                pyxel.blt(dst_x, dst_y, self.image_bank, src_x, src_y, width, height)
            else:
                pyxel.blt(dst_x, dst_y, self.image_bank, src_x, src_y, 
                          width, height, transparent_color)
                      
        except Exception as e:
            print(f"Error drawing tile '{tile_id}' at ({x},{y}) from ({tile_pos[0]},{tile_pos[1]}): {e}")
            # Draw fallback
            pyxel.rect(x, y, self.tile_size, self.tile_size, 4)  # Brown for error
            pyxel.text(x + 2, y + 2, "E", 7)
    
    def get_road_tile_id(self, north: bool = False, east: bool = False, 
                        south: bool = False, west: bool = False) -> str:
        """Get appropriate road tile based on connections"""
        patterns = {
            (False, False, False, False): 'road_alone',
            (False, True, False, True): 'road_horizontal',
            (True, False, True, False): 'road_vertical',
            (False, True, True, False): 'road_corner_ne',
            (False, False, True, True): 'road_corner_se',
            (True, False, False, True): 'road_corner_sw',
            (True, True, False, False): 'road_corner_nw',
            (True, True, True, False): 'road_t_east',
            (True, False, True, True): 'road_t_west',
            (False, True, True, True): 'road_t_south',
            (True, True, False, True): 'road_t_north',
            (True, True, True, True): 'road_cross',
        }
        
        return patterns.get((north, east, south, west), 'road_alone')
    
    def get_rail_tile_id(self, north: bool = False, east: bool = False,
                        south: bool = False, west: bool = False) -> str:
        """Get appropriate rail tile based on connections"""
        patterns = {
            (False, False, False, False): 'rail_alone',
            (False, True, False, True): 'rail_horizontal',
            (True, False, True, False): 'rail_vertical',
            (False, True, True, False): 'rail_corner_ne',
            (False, False, True, True): 'rail_corner_se',
            (True, False, False, True): 'rail_corner_sw',
            (True, True, False, False): 'rail_corner_nw',
            (True, True, True, True): 'rail_cross',
        }
        
        # Rails have fewer patterns than roads
        return patterns.get((north, east, south, west), 'rail_alone')
        
    def get_building_tile_id(self, building_type: str, density: int) -> str:
        """Get building tile based on type and density"""
        # Density 0 = empty, 1-4 = building levels
        if density == 0:
            return 'empty'
            
        density = max(1, min(4, density))  # Clamp to 1-4
        return f"{building_type}_{density}"
        
    def draw_3x3_building(self, x: int, y: int, tile_id: str):
        """Draw a 3x3 building (draws a single tile that represents the whole building)"""
        # For ConcLand Mini, we draw a single 16x16 tile that represents the 3x3 building
        self.draw_tile(x, y, tile_id)