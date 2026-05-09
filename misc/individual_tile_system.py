#!/usr/bin/env python3
"""
Individual PNG Tile System for ConcLand Mini
Supports 256-color custom palette and individual PNG files per tile
"""

import pyxel
import os
from typing import Dict, Optional, Tuple
from enum import IntEnum

class TileBank(IntEnum):
    """Image banks for different tile categories"""
    TERRAIN = 1      # Ground, water, etc. (bank 0 reserved for palette)
    BUILDINGS = 2    # Residential, commercial, industrial
    INFRASTRUCTURE = 3  # Roads, rails, wires
    FACILITIES = 1   # Power plants, services (share with terrain for now)

class IndividualTileSystem:
    def __init__(self):
        self.tile_size = 8   # Default PNG tiles are 8x8
        self.loaded_tiles = {}  # tile_id -> (bank, x, y, width, height)
        self.palette_loaded = False
        self.animation_frame = 0  # For animated tiles
        self.animation_timer = 0  # Frame counter for animation speed
        
        # Special large tiles (actual sprite sizes)
        self.large_tiles = {
            'coal_plant': 32,  # 32x32 pixels for 4x4 cells
            'nuclear_plant': 32,  # 32x32 pixels for 4x4 cells
            'police': 24,  # 24x24 pixels for 3x3 cells
            'fire': 24,  # 24x24 pixels for 3x3 cells
            'hospital': 24,  # 24x24 pixels for 3x3 cells
        }
        
        # Define tile file mappings
        self.tile_files = {
            # Terrain tiles
            'empty': 'assets/tiles/terrain/grass.png',
            'grass': 'assets/tiles/terrain/grass.png', 
            'water': 'assets/tiles/terrain/water_animation.png',  # 4-frame animation
            'water_frame0': 'assets/tiles/terrain/water_animation.png',
            'water_frame1': 'assets/tiles/terrain/water_animation.png',
            'water_frame2': 'assets/tiles/terrain/water_animation.png',
            'water_frame3': 'assets/tiles/terrain/water_animation.png',
            'soil': 'assets/tiles/terrain/soil.png',
            'sand': 'assets/tiles/terrain/sand.png',
            
            # Coastline tiles (15 patterns for water/land boundaries)
            'coastline_0001': 'assets/tiles/terrain/coastline_0001.png',
            'coastline_0010': 'assets/tiles/terrain/coastline_0010.png',
            'coastline_0011': 'assets/tiles/terrain/coastline_0011.png',
            'coastline_0100': 'assets/tiles/terrain/coastline_0100.png',
            'coastline_0101': 'assets/tiles/terrain/coastline_0101.png',
            'coastline_0110': 'assets/tiles/terrain/coastline_0110.png',
            'coastline_0111': 'assets/tiles/terrain/coastline_0111.png',
            'coastline_1000': 'assets/tiles/terrain/coastline_1000.png',
            'coastline_1001': 'assets/tiles/terrain/coastline_1001.png',
            'coastline_1010': 'assets/tiles/terrain/coastline_1010.png',
            'coastline_1011': 'assets/tiles/terrain/coastline_1011.png',
            'coastline_1100': 'assets/tiles/terrain/coastline_1100.png',
            'coastline_1101': 'assets/tiles/terrain/coastline_1101.png',
            'coastline_1110': 'assets/tiles/terrain/coastline_1110.png',
            'coastline_1111': 'assets/tiles/terrain/coastline_1111.png',
            
            # Diagonal coastline tiles
            'coastline_diagonal_ne': 'assets/tiles/terrain/coastline_diagonal_ne.png',
            'coastline_diagonal_se': 'assets/tiles/terrain/coastline_diagonal_se.png',
            'coastline_diagonal_sw': 'assets/tiles/terrain/coastline_diagonal_sw.png',
            'coastline_diagonal_nw': 'assets/tiles/terrain/coastline_diagonal_nw.png',
            
            # Building tiles
            'residential_1': 'assets/tiles/residential/low_1.png',
            'residential_2': 'assets/tiles/residential/middle_1.png',
            'residential_3': 'assets/tiles/residential/high_1.png',
            'residential_4': 'assets/tiles/residential/high_1.png',
            
            'commercial_1': 'assets/tiles/commercial/low_1.png',
            'commercial_2': 'assets/tiles/commercial/middle_1.png',
            'commercial_3': 'assets/tiles/commercial/high_1.png',
            'commercial_4': 'assets/tiles/commercial/high_1.png',
            
            'industrial_1': 'assets/tiles/industrial/low_1.png',
            'industrial_2': 'assets/tiles/industrial/middle_1.png',
            'industrial_3': 'assets/tiles/industrial/high_1.png',
            'industrial_4': 'assets/tiles/industrial/high_1.png',
            
            # Infrastructure tiles
            'road_alone': 'assets/tiles/road/alone.png',
            'road_horizontal': 'assets/tiles/road/horizontal.png',
            'road_vertical': 'assets/tiles/road/vertical.png',
            'road_corner_ne': 'assets/tiles/road/corner_ne.png',
            'road_corner_se': 'assets/tiles/road/corner_se.png',
            'road_corner_sw': 'assets/tiles/road/corner_sw.png',
            'road_corner_nw': 'assets/tiles/road/corner_nw.png',
            'road_cross': 'assets/tiles/road/cross.png',
            'road_t_north': 'assets/tiles/road/t_north.png',
            'road_t_south': 'assets/tiles/road/t_south.png',
            'road_t_east': 'assets/tiles/road/t_east.png',
            'road_t_west': 'assets/tiles/road/t_west.png',
            'road_end_north': 'assets/tiles/road/end_top.png',
            'road_end_south': 'assets/tiles/road/end_bottom.png',
            'road_end_east': 'assets/tiles/road/end_right.png',
            'road_end_west': 'assets/tiles/road/end_left.png',
            'road_rail_horizontal': 'assets/tiles/road/horizontal_rail.png',
            'road_rail_vertical': 'assets/tiles/road/vertical_rail.png',
            
            'rail_alone': 'assets/tiles/rail/alone.png',
            'rail_horizontal': 'assets/tiles/rail/horizontal.png',
            'rail_vertical': 'assets/tiles/rail/vertical.png',
            'rail_corner_ne': 'assets/tiles/rail/corner_ne.png',
            'rail_corner_se': 'assets/tiles/rail/corner_se.png',
            'rail_corner_sw': 'assets/tiles/rail/corner_sw.png',
            'rail_corner_nw': 'assets/tiles/rail/corner_nw.png',
            'rail_cross': 'assets/tiles/rail/cross.png',
            'rail_t_north': 'assets/tiles/rail/t_north.png',
            'rail_t_south': 'assets/tiles/rail/t_south.png',
            'rail_t_east': 'assets/tiles/rail/t_east.png',
            'rail_t_west': 'assets/tiles/rail/t_west.png',
            
            # Other tiles
            'wire': 'assets/tiles/power/solar.png',  # Use solar as wire placeholder
            'park': 'assets/tiles/park/small_park.png',
            
            # Facilities
            'coal_plant': 'assets/tiles/power/coal.png',
            'oil_plant': 'assets/tiles/power/gas.png',
            'nuclear_plant': 'assets/tiles/power/nuclear.png',
            'wind_plant': 'assets/tiles/power/wind_animation.png',
            
            # Agricultural
            'farm': 'assets/tiles/agricultural/field.png',
            'farm_empty': 'assets/tiles/agricultural/empty.png',
            
            # Public services
            'police': 'assets/tiles/public/police.png',  # 24x24 police station
            'fire': 'assets/tiles/public/fire.png',  # 24x24 fire station
            'hospital': 'assets/tiles/public/hospital.png',  # 24x24 hospital
            'school': 'assets/tiles/public/shrine.png',
            
            # Effects
            'construction': 'assets/tiles/effects/construction_animation.png',
            'fire_effect': 'assets/tiles/effects/fire_animation.png',
            
            # Empty lots
            'empty_residential': 'assets/tiles/residential/empty.png',
            'empty_commercial': 'assets/tiles/commercial/empty.png',
            'empty_industrial': 'assets/tiles/industrial/empty.png',
            
            # Item icons (8x8)
            'icon_bulldozer': 'assets/icons/bulldozer.png',
            'icon_residential': 'assets/icons/residential.png',
            'icon_commercial': 'assets/icons/commercial.png',
            'icon_industrial': 'assets/icons/industrial.png',
            'icon_road': 'assets/icons/road.png',
            'icon_rail': 'assets/icons/rail.png',
            'icon_park': 'assets/icons/park.png',
            'icon_wire': 'assets/icons/wire.png',
            'icon_coal_plant': 'assets/icons/coal_plant.png',
            'icon_nuclear_plant': 'assets/icons/nuclear_plant.png',
            'icon_police': 'assets/icons/police.png',
            'icon_fire': 'assets/icons/fire.png',
            'icon_hospital': 'assets/icons/hospital.png',
            'icon_school': 'assets/icons/school.png',
            'icon_budget': 'assets/icons/budget.png',
            'icon_map': 'assets/icons/map.png',
            'icon_query': 'assets/icons/query.png',
            'icon_settings': 'assets/icons/settings.png',
            'no_power_overlay': 'assets/tiles/overlay/power_16color.png',
            'window_9slice': 'assets/window_9slice.png',
            
        }
        
        # Special tiles that need custom handling (loaded separately)
        self.special_tiles = {
            'map_kind': 'assets/map_kind.png',  # Contains all 5 map icons (16x16 each)
        }
        
        # Fallback colors for missing tiles
        self.fallback_colors = {
            'empty': 3,
            'grass': 3,
            'water': 12,
            'sand': 4,
            # Coastline fallback colors (brownish for sand/land border)
            'coastline_0001': 4, 'coastline_0010': 4, 'coastline_0011': 4, 'coastline_0100': 4,
            'coastline_0101': 4, 'coastline_0110': 4, 'coastline_0111': 4, 'coastline_1000': 4,
            'coastline_1001': 4, 'coastline_1010': 4, 'coastline_1011': 4, 'coastline_1100': 4,
            'coastline_1101': 4, 'coastline_1110': 4, 'coastline_1111': 4,
            'residential_1': 10, 'residential_2': 10, 'residential_3': 10, 'residential_4': 10,
            'commercial_1': 14, 'commercial_2': 14, 'commercial_3': 14, 'commercial_4': 14,
            'industrial_1': 4, 'industrial_2': 4, 'industrial_3': 4, 'industrial_4': 4,
            'road_alone': 13, 'road_horizontal': 13, 'road_vertical': 13,
            'road_corner_ne': 13, 'road_corner_se': 13, 'road_corner_sw': 13, 'road_corner_nw': 13,
            'road_cross': 13, 'road_t_north': 13, 'road_t_south': 13, 'road_t_east': 13, 'road_t_west': 13,
            'rail_alone': 1, 'rail_horizontal': 1, 'rail_vertical': 1,
            'rail_corner_ne': 1, 'rail_corner_se': 1, 'rail_corner_sw': 1, 'rail_corner_nw': 1,
            'rail_cross': 1,
            'wire': 10,
            'park': 11,
            'coal_plant': 2,
            'oil_plant': 2,
            'nuclear_plant': 2,
            'police': 6,
            'fire': 8,
            'hospital': 7,
            'school': 7,
            # Icon fallback colors
            'icon_bulldozer': 8,
            'icon_residential': 10,
            'icon_commercial': 14,
            'icon_industrial': 15,
            'icon_road': 6,
            'icon_rail': 13,
            'icon_park': 3,
            'icon_wire': 9,
            'icon_coal_plant': 1,
            'icon_nuclear_plant': 9,
            'icon_police': 2,
            'icon_fire': 8,
            'icon_hospital': 7,
            'icon_school': 12,
            'icon_no_power': 9,  # Yellow
            'icon_no_power_simple': 9,
        }
    
    def load_custom_palette(self, palette_path: str = "assets/palette256_magenta.png") -> bool:
        """Load custom 256-color palette"""
        print(f"🎨 Loading custom palette: {palette_path}")
        
        if not os.path.exists(palette_path):
            print(f"❌ Palette file not found: {palette_path}")
            return False
        
        try:
            # Load palette to extend Pyxel's color system
            pyxel.images[0].load(0, 0, palette_path, incl_colors=True)
            self.palette_loaded = True
            print("✅ Custom 256-color palette loaded successfully")
            
            # Print first 16 colors for verification
            print("🌈 First 16 colors:")
            for i in range(16):
                color = pyxel.colors[i]
                print(f"  Color {i:2d}: 0x{color:06X}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to load palette: {e}")
            return False
    
    def load_individual_tiles(self) -> int:
        """Load individual PNG tiles"""
        print("📁 Loading individual PNG tiles...")
        
        # FIRST: Load large tiles from combined tileset
        if os.path.exists('assets/combined_tileset.png'):
            print("📦 Loading large tiles from combined tileset...")
            pyxel.images[2].load(0, 0, 'assets/combined_tileset.png', incl_colors=False)
            
            # Register large tile positions in the combined tileset
            self.loaded_tiles['coal_plant'] = (2, 0, 0, 32, 32)
            self.loaded_tiles['nuclear_plant'] = (2, 32, 0, 32, 32)
            self.loaded_tiles['oil_plant'] = (2, 64, 0, 32, 32)
            self.loaded_tiles['police'] = (2, 0, 32, 24, 24)
            self.loaded_tiles['fire'] = (2, 24, 32, 24, 24)
            self.loaded_tiles['hospital'] = (2, 48, 32, 24, 24)
            print("  ✅ Large tiles loaded from combined tileset")
        
        loaded_count = 6  # Count the large tiles
        current_bank = TileBank.TERRAIN
        current_x, current_y = 0, 0
        
        # Load regular tiles first
        for tile_id, file_path in self.tile_files.items():
            # Skip large tiles (already loaded from combined tileset)
            if tile_id in ['coal_plant', 'nuclear_plant', 'oil_plant', 'police', 'fire', 'hospital']:
                continue
                
            if os.path.exists(file_path):
                try:
                    # Skip water frame entries (handled by water)
                    if tile_id.startswith('water_frame'):
                        continue
                        
                    # Special handling for water animation
                    if tile_id == 'water':
                        # Load the entire water animation strip (4 frames)
                        pyxel.images[current_bank].load(
                            current_x, current_y, file_path, incl_colors=False
                        )
                        # Store locations for each frame
                        for i in range(4):
                            frame_id = f'water_frame{i}'
                            self.loaded_tiles[frame_id] = (current_bank, current_x + (i * self.tile_size), current_y, self.tile_size, self.tile_size)
                        # Also store the base water tile as frame 0
                        self.loaded_tiles['water'] = (current_bank, current_x, current_y, self.tile_size, self.tile_size)
                        
                        print(f"  ✅ water animation: {file_path} -> bank {current_bank} (4 frames)")
                        loaded_count += 1
                        # Skip space for all 4 frames
                        current_x += self.tile_size * 4  # Skip all 4 frames
                        
                    else:
                        # Load regular 8x8 tile
                        pyxel.images[current_bank].load(
                            current_x, current_y, file_path, incl_colors=False
                        )
                        
                        # Store tile location
                        self.loaded_tiles[tile_id] = (current_bank, current_x, current_y, self.tile_size, self.tile_size)
                        
                        print(f"  ✅ {tile_id}: {file_path} -> bank {current_bank} ({current_x},{current_y})")
                        loaded_count += 1
                        
                        # Move to next position
                        current_x += self.tile_size
                    
                    # Check if we need to wrap to next row/bank
                    if current_x >= 256:  # Pyxel image bank is 256x256
                        current_x = 0
                        current_y += 32 if any(t in tile_id for t in self.large_tiles) else self.tile_size
                        if current_y >= 256:
                            # Move to next bank
                            current_bank += 1
                            if current_bank > 2:
                                current_bank = 1  # Skip bank 0
                            current_x, current_y = 0, 0
                    
                except Exception as e:
                    print(f"  ❌ Failed to load {tile_id} from {file_path}: {e}")
            else:
                print(f"  ⚠️  File not found: {file_path}")
        
        print(f"📊 Loaded {loaded_count}/{len(self.tile_files)} tiles")
        
        # Load special tiles separately (like map_kind)
        print("📁 Loading special tiles...")
        for tile_id, file_path in self.special_tiles.items():
            if os.path.exists(file_path):
                try:
                    if tile_id == 'map_kind':
                        # Load map_kind to a specific location in bank 2
                        # This keeps it separate from regular tiles
                        special_bank = 2
                        special_x = 160  # Far from regular tiles
                        special_y = 0
                        
                        pyxel.images[special_bank].load(
                            special_x, special_y, file_path, incl_colors=False
                        )
                        
                        # map_kind contains 5 16x16 icons = 80x16 pixels total
                        self.loaded_tiles[tile_id] = (special_bank, special_x, special_y, 80, 16)
                        print(f"  ✅ {tile_id}: {file_path} -> bank {special_bank} at ({special_x},{special_y})")
                        loaded_count += 1
                except Exception as e:
                    print(f"  ❌ Failed to load special tile {tile_id}: {e}")
            else:
                print(f"  ⚠️  Special tile not found: {file_path}")
        
        return loaded_count
    
    def create_fallback_tiles(self):
        """Create fallback colored tiles when PNG files are missing"""
        print("🎨 Creating fallback colored tiles...")
        
        # Clear image banks (skip bank 0 which has palette)
        for bank in range(1, 4):
            pyxel.images[bank].cls(0)
        
        current_bank = TileBank.TERRAIN
        current_x, current_y = 0, 0
        
        for tile_id, color in self.fallback_colors.items():
            # Draw colored rectangle
            pyxel.images[current_bank].rect(
                current_x, current_y, self.tile_size, self.tile_size, color
            )
            
            # Add border
            pyxel.images[current_bank].rectb(
                current_x, current_y, self.tile_size, self.tile_size, 7
            )
            
            # Add identifying mark (first letter)
            if tile_id:
                char = tile_id[0].upper()
                pyxel.images[current_bank].text(
                    current_x + 2, current_y + 2, char, 7 if color != 7 else 0
                )
            
            # Store tile location with size
            size = self.large_tiles.get(tile_id, self.tile_size)
            self.loaded_tiles[tile_id] = (current_bank, current_x, current_y, size, size)
            
            # Move to next position
            current_x += self.tile_size
            if current_x + self.tile_size > 256:
                current_x = 0
                current_y += self.tile_size
                if current_y + self.tile_size > 256:  
                    current_bank += 1
                    if current_bank > 3:
                        current_bank = 1  # Skip bank 0
                    current_x, current_y = 0, 0
        
        print(f"✅ Created {len(self.fallback_colors)} fallback tiles")
    
    def initialize(self) -> bool:
        """Initialize the tile system"""
        print("🚀 Initializing Individual Tile System")
        print("="*50)
        
        # Load custom palette first
        palette_success = self.load_custom_palette()
        
        # Try to load individual tiles
        loaded_count = self.load_individual_tiles()
        
        # If no tiles loaded, create fallback
        if loaded_count == 0:
            print("⚠️  No PNG tiles found, using colored fallbacks")
            self.create_fallback_tiles()
        
        success = palette_success or loaded_count > 0
        
        print(f"\n🎯 Tile System Status:")
        print(f"  Palette: {'✅ Custom 256-color' if palette_success else '⚠️  Default 16-color'}")
        print(f"  Tiles: {'✅ PNG files' if loaded_count > 0 else '⚠️  Colored fallbacks'}")
        print(f"  Available tiles: {len(self.loaded_tiles)}")
        
        return success
    
    def draw_tile(self, tile_id: str, x: int, y: int, transparent_color=None, scale_to_fit=None):
        """Draw a tile at the specified position
        
        Args:
            tile_id: ID of the tile to draw
            x, y: Screen position to draw at
            transparent_color: Color to treat as transparent
            scale_to_fit: Target size to scale to (for 32x32 sprites in 24x24 spaces)
        """
        if tile_id not in self.loaded_tiles:
            # Missing tile - draw red error square
            pyxel.rect(x, y, self.tile_size, self.tile_size, 8)
            pyxel.text(x + 2, y + 3, "?", 7)
            return
        
        tile_info = self.loaded_tiles[tile_id]
        if len(tile_info) == 5:
            bank, src_x, src_y, width, height = tile_info
        else:
            # Old format without size (backwards compatibility)
            bank, src_x, src_y = tile_info
            width, height = self.tile_size, self.tile_size
        
        # Debug for large tiles - ALWAYS debug to understand the problem
        if tile_id in self.large_tiles:
            print(f"DEBUG draw_tile: {tile_id} bank={bank} src=({src_x},{src_y}) size={width}x{height} screen=({x},{y})")
            # Also check what's actually in the image bank
            print(f"  Drawing from bank {bank} at ({src_x},{src_y}) with size {width}x{height}")
        
        try:
            # Draw the tile with its actual size
            if transparent_color is None:
                pyxel.blt(x, y, bank, src_x, src_y, width, height)
            else:
                pyxel.blt(x, y, bank, src_x, src_y, width, height, transparent_color)
                
        except Exception as e:
            print(f"Error drawing tile '{tile_id}': {e}")
            # Fallback colored rectangle
            color = self.fallback_colors.get(tile_id, 8)
            pyxel.rect(x, y, width, height, color)
    
    def get_road_tile_id(self, north=False, east=False, south=False, west=False) -> str:
        """Get appropriate road tile based on connections"""
        patterns = {
            (False, False, False, False): 'road_alone',
            # End pieces (single connection)
            (True, False, False, False): 'road_end_south',  # Road ends pointing south
            (False, True, False, False): 'road_end_west',   # Road ends pointing west
            (False, False, True, False): 'road_end_north',  # Road ends pointing north
            (False, False, False, True): 'road_end_east',   # Road ends pointing east
            # Straight pieces
            (False, True, False, True): 'road_horizontal',
            (True, False, True, False): 'road_vertical',
            # Corner pieces
            (False, True, True, False): 'road_corner_ne',
            (False, False, True, True): 'road_corner_se',
            (True, False, False, True): 'road_corner_sw',
            (True, True, False, False): 'road_corner_nw',
            # T-junction pieces
            (True, True, True, False): 'road_t_east',
            (True, False, True, True): 'road_t_west',
            (False, True, True, True): 'road_t_south',
            (True, True, False, True): 'road_t_north',
            # Cross piece
            (True, True, True, True): 'road_cross',
        }
        return patterns.get((north, east, south, west), 'road_alone')
    
    def get_rail_tile_id(self, north=False, east=False, south=False, west=False) -> str:
        """Get appropriate rail tile based on connections"""
        patterns = {
            (False, False, False, False): 'rail_alone',
            (False, True, False, True): 'rail_horizontal',
            (True, False, True, False): 'rail_vertical',
            (False, True, True, False): 'rail_corner_ne',
            (False, False, True, True): 'rail_corner_se',
            (True, False, False, True): 'rail_corner_sw',
            (True, True, False, False): 'rail_corner_nw',
            (True, True, True, False): 'rail_t_east',
            (True, False, True, True): 'rail_t_west',
            (False, True, True, True): 'rail_t_south',
            (True, True, False, True): 'rail_t_north',
            (True, True, True, True): 'rail_cross',
        }
        return patterns.get((north, east, south, west), 'rail_alone')
    
    def get_building_tile_id(self, building_type: str, density: int) -> str:
        """Get appropriate building tile based on type and density"""
        # Map building types to tile prefixes
        building_map = {
            'residential': 'residential',
            'commercial': 'commercial',
            'industrial': 'industrial'
        }
        
        prefix = building_map.get(building_type, building_type)
        
        # For buildings with density levels
        if prefix in ['residential', 'commercial', 'industrial']:
            return f"{prefix}_{min(max(density, 1), 4)}"  # Clamp density to 1-4
        
        # For other building types, return as-is
        return building_type
    
    def update_animation(self):
        """Update animation frame counter"""
        self.animation_timer += 1
        if self.animation_timer >= 15:  # Change frame every 15 frames (4 FPS at 60 FPS)
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4
    
    def draw_animated_tile(self, tile_id: str, x: int, y: int, transparent_color=None):
        """Draw a tile with animation support"""
        # Handle animated tiles
        if tile_id == 'water':
            animated_id = f'water_frame{self.animation_frame}'
            if animated_id in self.loaded_tiles:
                tile_id = animated_id
        
        # Use regular draw method
        self.draw_tile(tile_id, x, y, transparent_color)

# Test function
def test_individual_tiles():
    """Test the individual tile system"""
    print("🧪 Testing Individual Tile System")
    
    pyxel.init(320, 288, title="Individual Tile Test")
    
    tile_system = IndividualTileSystem()
    tile_system.initialize()
    
    def update():
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
    
    def draw():
        pyxel.cls(0)
        
        # Draw title
        pyxel.text(10, 10, "Individual Tile System Test", 7)
        
        # Draw sample tiles
        test_tiles = ['empty', 'grass', 'water', 'residential_1', 'commercial_1', 
                     'industrial_1', 'road_horizontal', 'rail_vertical', 'park']
        
        for i, tile_id in enumerate(test_tiles):
            x = 10 + (i % 3) * 30
            y = 30 + (i // 3) * 30
            tile_system.draw_tile(tile_id, x, y)
            pyxel.text(x, y + 18, tile_id[:5], 7)
        
        pyxel.text(10, 200, "ESC: Exit", 7)
        
        # Show palette info
        palette_text = "256-color palette" if tile_system.palette_loaded else "16-color default"
        pyxel.text(10, 220, f"Palette: {palette_text}", 6)
        pyxel.text(10, 230, f"Tiles: {len(tile_system.loaded_tiles)}", 6)
    
    pyxel.run(update, draw)

if __name__ == "__main__":
    test_individual_tiles()