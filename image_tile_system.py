#!/usr/bin/env python3
"""
Image-based tile system using pyxel.Image for proper large tile support
"""

import pyxel
import os
from enum import IntEnum
from typing import Dict, Optional, Tuple

class TileBank(IntEnum):
    """Image bank assignments"""
    PALETTE = 0
    TERRAIN = 1  
    BUILDINGS = 2
    SPECIAL = 3

class ImageTileSystem:
    """Tile system using pyxel.Image for each tile"""
    
    def __init__(self):
        self.tile_size = 8  # Default tile size
        self.tile_images: Dict[str, pyxel.Image] = {}  # Store Image objects instead of bank positions
        self.palette_loaded = False
        self.animation_frame = 0
        self.animation_timer = 0
        self.terrain_img = None  # Store terrains.png as a single image
        self.terrain_frame = 0  # Current animation frame for terrain
        
        # Special large tiles (actual sprite sizes)
        self.large_tiles = {
            'coal_plant': 32,
            'nuclear_plant': 32,
            'gas_plant': 32,
            'wind_plant': 32,
            'oil_plant': 32,
            'police': 24,
            'fire': 24,
            'hospital': 24,
            'school': 24,
            'university': 24,
            # RCI merged buildings
            'residential_2': 16,  # middle_1.png
            'residential_3': 32,  # high_1.png
            'residential_4': 32,  # high_1.png
            'commercial_2': 16,   # middle_1.png
            'commercial_3': 32,   # high_1.png
            'commercial_4': 32,   # high_1.png
            'industrial_2': 16,   # middle_1.png
            'industrial_3': 32,   # high_1.png
            'industrial_4': 32,   # high_1.png
            'sewage_plant': 24,
            'water_plant': 24,
        }
        
        # Define tile file mappings
        # Map terrain tile names to their index in terrains.png
        self.terrain_indices = {
            'grass': 0,
            'empty': 0,  # Use grass for empty
            'coastline_0001': 1,
            'coastline_0010': 2,
            'coastline_0011': 3,
            'coastline_0100': 4,
            'coastline_0101': 5,
            'coastline_0110': 6,
            'coastline_0111': 7,
            'coastline_1000': 8,
            'coastline_1001': 9,
            'coastline_1010': 10,
            'coastline_1011': 11,
            'coastline_1100': 12,
            'coastline_1101': 13,
            'coastline_1110': 14,
            'coastline_1111': 15,
            'coastline_diagonal_ne': 16,
            'coastline_diagonal_nw': 17,
            'coastline_diagonal_se': 18,
            'coastline_diagonal_sw': 19,
        }
        
        self.tile_files = {
            # Terrain tiles are now in terrains.png
            # Keep water and other non-terrain tiles as individual files
            'water': 'assets/tiles/terrain/water_animation.png',
            'soil': 'assets/tiles/terrain/soil.png',
            'sand': 'assets/tiles/terrain/sand.png',
            'wasteland': 'assets/tiles/terrain/wasteland.png',
            
            # Buildings with variations
            'residential_1': 'assets/tiles/residential/low_1.png',
            'residential_1_v1': 'assets/tiles/residential/low_1.png',
            'residential_1_v2': 'assets/tiles/residential/low_2.png',
            'residential_1_v3': 'assets/tiles/residential/low_3.png',
            'residential_2': 'assets/tiles/residential/middle_1.png',
            'residential_3': 'assets/tiles/residential/high_1.png',
            'residential_4': 'assets/tiles/residential/high_1.png',
            'commercial_1': 'assets/tiles/commercial/low_1.png',
            'commercial_1_v1': 'assets/tiles/commercial/low_1.png',
            'commercial_1_v2': 'assets/tiles/commercial/low_2.png',
            'commercial_1_v3': 'assets/tiles/commercial/low_3.png',
            'commercial_2': 'assets/tiles/commercial/middle_1.png',
            'commercial_3': 'assets/tiles/commercial/high_1.png',
            'commercial_4': 'assets/tiles/commercial/high_1.png',
            'industrial_1': 'assets/tiles/industrial/low_1.png',
            'industrial_1_v1': 'assets/tiles/industrial/low_1.png',
            'industrial_1_v2': 'assets/tiles/industrial/low_2.png',
            'industrial_1_v3': 'assets/tiles/industrial/low_3.png',
            'industrial_2': 'assets/tiles/industrial/middle_1.png',
            'industrial_3': 'assets/tiles/industrial/high_1.png',
            'industrial_4': 'assets/tiles/industrial/high_1.png',
            'empty_residential': 'assets/tiles/residential/empty.png',
            'empty_commercial': 'assets/tiles/commercial/empty.png',
            'empty_industrial': 'assets/tiles/industrial/empty.png',
            'const_residential': 'assets/tiles/residential/const.png',
            'const_commercial': 'assets/tiles/commercial/const.png',
            'const_industrial': 'assets/tiles/industrial/const.png',
            
            # Agricultural
            'farm': 'assets/tiles/agricultural/farm.png',
            'field': 'assets/tiles/agricultural/field.png',
            'orchard': 'assets/tiles/agricultural/orchard.png',
            'silo': 'assets/tiles/agricultural/silo.png',
            'empty_agricultural': 'assets/tiles/agricultural/empty.png',
            
            # Roads
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
            
            # Rails
            'rail_alone': 'assets/tiles/rail/alone.png',
            'rail_horizontal': 'assets/tiles/rail/horizontal.png',
            'rail_vertical': 'assets/tiles/rail/vertical.png',
            'rail_corner_ne': 'assets/tiles/rail/corner_ne.png',
            'rail_corner_se': 'assets/tiles/rail/corner_se.png',
            'rail_corner_sw': 'assets/tiles/rail/corner_sw.png',
            'rail_corner_nw': 'assets/tiles/rail/corner_nw.png',
            'rail_cross': 'assets/tiles/rail/cross.png',
            'station': 'assets/tiles/rail/station.png',
            'rail_t_north': 'assets/tiles/rail/t_north.png',
            'rail_t_south': 'assets/tiles/rail/t_south.png',
            'rail_t_east': 'assets/tiles/rail/t_east.png',
            'rail_t_west': 'assets/tiles/rail/t_west.png',
            
            # Wire/Power lines
            'wire_alone': 'assets/tiles/power/wire_alone_black.png',
            'wire_horizontal': 'assets/tiles/power/wire_horizontal_black.png',
            'wire_vertical': 'assets/tiles/power/wire_vertical_black.png',
            'wire_corner_ne': 'assets/tiles/power/wire_ne_black.png',
            'wire_corner_se': 'assets/tiles/power/wire_se_black.png',
            'wire_corner_sw': 'assets/tiles/power/wire_sw_black.png',
            'wire_corner_nw': 'assets/tiles/power/wire_nw_black.png',
            'wire_cross': 'assets/tiles/power/wire_cross_black.png',
            'wire_t_north': 'assets/tiles/power/wire_t_top_black.png',
            'wire_t_south': 'assets/tiles/power/wire_t_down_black.png',
            'wire_t_east': 'assets/tiles/power/wire_t_right_black.png',
            'wire_t_west': 'assets/tiles/power/wire_t_left_black.png',
            
            # Other tiles (fallback wire for compatibility)
            'wire': 'assets/tiles/power/solar.png',  # Fallback
            'park': 'assets/tiles/park/small_park.png',
            
            # Facilities
            'coal_plant': 'assets/tiles/power/coal.png',
            'oil': 'assets/tiles/power/oil.png',
            'oil_plant': 'assets/tiles/power/oil.png',
            'nuclear_plant': 'assets/tiles/power/nuclear.png',
            'gas': 'assets/tiles/power/gas.png',
            'gas_plant': 'assets/tiles/power/gas.png',
            'solar': 'assets/tiles/power/solar.png',
            'wind': 'assets/tiles/power/wind.png',
            'wind_plant': 'assets/tiles/power/wind_animation.png',
            'wind_animation': 'assets/tiles/power/wind_animation.png',
            
            # Public services
            'police': 'assets/tiles/public/police.png',
            'fire': 'assets/tiles/public/fire.png',
            'hospital': 'assets/tiles/public/hospital.png',
            'school': 'assets/tiles/public/school.png',
            'university': 'assets/tiles/public/university.png',
            'library': 'assets/tiles/public/library.png',
            'incinerator': 'assets/tiles/public/incinerator.png',
            'waste': 'assets/tiles/public/waste.png',
            'military': 'assets/tiles/public/military.png',
            'prison': 'assets/tiles/public/prison.png',
            'shrine': 'assets/tiles/public/shrine.png',
            'laboratory': 'assets/tiles/public/laboratory.png',
            'space': 'assets/tiles/public/space.png',
            'airport': 'assets/tiles/port/airport.png',
            'heliport': 'assets/tiles/port/heliport.png',
            'port': 'assets/tiles/port/port.png',
            'seaport': 'assets/tiles/port/port.png',
            'onsen': 'assets/tiles/special/onsen.png',
            'pachinko': 'assets/tiles/special/pachinko.png',
            
            # Parks
            'park_middle': 'assets/tiles/park/park_middle.png',
            
            # Water facilities
            'sewage_plant': 'assets/tiles/water/sewage.png',
            'water_plant': 'assets/tiles/water/waterplant.png',
            'pump': 'assets/tiles/water/pump.png',
            
            # Wire overlays for roads/rails
            'wire_overlay_alone': 'assets/tiles/overlay/wire/wire_alone_overlay.png',
            'wire_overlay_horizontal': 'assets/tiles/overlay/wire/wire_horizontal_overlay.png',
            'wire_overlay_vertical': 'assets/tiles/overlay/wire/wire_vertical_overlay.png',
            'wire_overlay_corner_nw': 'assets/tiles/overlay/wire/wire_nw_overlay.png',
            'wire_overlay_corner_ne': 'assets/tiles/overlay/wire/wire_ne_overlay.png',
            'wire_overlay_corner_sw': 'assets/tiles/overlay/wire/wire_sw_overlay.png',
            'wire_overlay_corner_se': 'assets/tiles/overlay/wire/wire_se_overlay.png',
            'wire_overlay_t_north': 'assets/tiles/overlay/wire/wire_t_top_overlay.png',
            'wire_overlay_t_east': 'assets/tiles/overlay/wire/wire_t_right_overlay.png',
            'wire_overlay_t_south': 'assets/tiles/overlay/wire/wire_t_down_overlay.png',
            'wire_overlay_t_west': 'assets/tiles/overlay/wire/wire_t_left_overlay.png',
            'wire_overlay_cross': 'assets/tiles/overlay/wire/wire_cross_overlay.png',
            
            # Train overlays
            'train_horizontal': 'assets/tiles/overlay/train_horizontal.png',
            'train_vertical': 'assets/tiles/overlay/train_vertical.png',
            
            # Effects (removed - files don't exist)
            # 'construction': 'assets/tiles/effects/construction_animation.png',
            # 'fire_effect': 'assets/tiles/effects/fire_animation.png',
            
            # Empty lots
            'empty_residential': 'assets/tiles/residential/empty.png',
            'empty_commercial': 'assets/tiles/commercial/empty.png',
            'empty_industrial': 'assets/tiles/industrial/empty.png',
            
            # Icons (8x8)
            'icon_bulldozer': 'assets/icons/bulldozer.png',
            'icon_residential': 'assets/icons/residential.png',
            'icon_commercial': 'assets/icons/commercial.png',
            'icon_industrial': 'assets/icons/industrial.png',
            'icon_road': 'assets/icons/road.png',
            'icon_rail': 'assets/icons/rail.png',
            'icon_park': 'assets/icons/park.png',
            'icon_wire': 'assets/icons/wire.png',
            'icon_coal_plant': 'assets/icons/coal.png',
            'icon_nuclear_plant': 'assets/icons/nuclear.png',
            'icon_gas_plant': 'assets/icons/gas.png',
            'icon_wind_plant': 'assets/icons/wind.png',
            'icon_police': 'assets/icons/police.png',
            'icon_fire': 'assets/icons/fire.png',
            'icon_hospital': 'assets/icons/hospital.png',
            'icon_school': 'assets/icons/school.png',
            'icon_university': 'assets/icons/university.png',
            'icon_park_middle': 'assets/icons/park_middle.png',
            'icon_sewage_plant': 'assets/icons/sewage.png',
            'icon_water_plant': 'assets/icons/library.png',  # Use library icon for water plant
            'icon_pump': 'assets/icons/pump.png',
            # Icons that don't exist yet
            # 'icon_budget': 'assets/icons/budget.png',
            # 'icon_map': 'assets/icons/map.png',
            # 'icon_query': 'assets/icons/query.png',
            # 'icon_settings': 'assets/icons/settings.png',
            'no_power_overlay': 'assets/tiles/overlay/power_16color.png',
            'no_water_overlay': 'assets/tiles/overlay/water_16color.png',
            'traffic_overlay_horizontal': 'assets/tiles/overlay/cars_horizontal_fixed.png',  # Horizontal traffic (black transparent)
            'traffic_overlay_vertical': 'assets/tiles/overlay/cars_vertical_fixed.png',    # Vertical traffic (black transparent)
            'train_overlay_horizontal': 'assets/tiles/overlay/train_horizontal.png',  # Horizontal train
            'train_overlay_vertical': 'assets/tiles/overlay/train_vertical.png',    # Vertical train
            'window_9slice': 'assets/window_9slice.png',
        }
        
        # Special tiles that need custom handling
        self.special_tiles = {
            'map_kind': 'assets/map_kind.png',  # Contains all 5 map icons (16x16 each)
        }
        
        # Fallback colors for missing tiles
        self.fallback_colors = {
            'empty': 3, 'grass': 3, 'water': 12, 'sand': 4, 'wasteland': 4,
            'residential_1': 10, 'commercial_1': 14, 'industrial_1': 4,
            'road_alone': 13, 'rail_alone': 1,
            'wire': 10, 'park': 11,
            'coal_plant': 2, 'oil_plant': 2, 'nuclear_plant': 2, 'gas_plant': 2, 'wind_plant': 2,
            'police': 6, 'fire': 8, 'hospital': 7, 'school': 7, 'university': 7,
            'park_middle': 11, 'sewage_plant': 9, 'water_plant': 12, 'pump': 12,
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
            return True
            
        except Exception as e:
            print(f"❌ Failed to load palette: {e}")
            return False
    
    def load_tiles_as_images(self) -> int:
        """Load tiles as pyxel.Image objects"""
        # print("📁 Loading tiles as Image objects...")
        
        loaded_count = 0
        
        # Load regular tiles
        for tile_id, file_path in self.tile_files.items():
            if os.path.exists(file_path):
                try:
                    # Use pyxel.Image.from_image to load the PNG directly
                    img = pyxel.Image.from_image(file_path)
                    self.tile_images[tile_id] = img
                    
                    # Special handling for water animation (32x8 strip with 4 frames)
                    if tile_id == 'water':
                        # For now, just use the whole strip as water
                        # Animation will cycle through positions when drawing
                        pass
                    
                    # size_str = f"[{img.width}x{img.height}]" if tile_id in self.large_tiles else ""
                    # print(f"  ✅ {tile_id}: {file_path} {size_str}")
                    loaded_count += 1
                    
                except Exception as e:
                    print(f"  ❌ Failed to load {tile_id} from {file_path}: {e}")
                    self._create_fallback_tile(tile_id)
            else:
                # File not found - create fallback
                self._create_fallback_tile(tile_id)
        
        # Load special tiles
        for tile_id, file_path in self.special_tiles.items():
            if os.path.exists(file_path):
                try:
                    img = pyxel.Image.from_image(file_path)
                    self.tile_images[tile_id] = img
                    # print(f"  ✅ {tile_id}: {file_path} [{img.width}x{img.height}]")
                    loaded_count += 1
                except Exception as e:
                    print(f"  ❌ Failed to load special tile {tile_id}: {e}")
        
        print(f"📊 Loaded {loaded_count} tiles")
        return loaded_count
    
    def _create_fallback_tile(self, tile_id: str):
        """Create a colored fallback tile"""
        color = self.fallback_colors.get(tile_id, 8)
        size = self.large_tiles.get(tile_id, 8)
        
        img = pyxel.Image(size, size)
        # Fill with single color
        img.cls(color)
        
        self.tile_images[tile_id] = img
    
    def initialize(self) -> bool:
        """Initialize the tile system"""
        print("🚀 Initializing Image Tile System")
        print("="*50)
        
        # Load custom palette first
        palette_success = self.load_custom_palette()
        
        # Load terrains.png strip
        terrains_path = 'assets/tiles/terrain/terrains.png'
        if os.path.exists(terrains_path):
            try:
                self.terrain_img = pyxel.Image.from_image(terrains_path)
                print(f"✅ Loaded terrains.png: {self.terrain_img.width}x{self.terrain_img.height}")
            except Exception as e:
                print(f"❌ Failed to load terrains.png: {e}")
                self.terrain_img = None
        
        # Load tiles as Image objects
        loaded_count = self.load_tiles_as_images()
        
        success = loaded_count > 0
        
        print(f"\n🎯 Tile System Status:")
        print(f"  Palette: {'✅ Custom 256-color' if palette_success else '⚠️  Default 16-color'}")
        print(f"  Terrains: {'✅ Loaded' if self.terrain_img else '❌ Not loaded'}")
        print(f"  Tiles loaded: {loaded_count}")
        print(f"  Using pyxel.Image for proper size support")
        
        return success
    
    def draw_tile(self, tile_id: str, x: int, y: int, transparent_color=None):
        """Draw a tile at the specified position"""
        # Check if this is a terrain tile from terrains.png
        if tile_id in self.terrain_indices and self.terrain_img:
            index = self.terrain_indices[tile_id]
            # Calculate position in the strip (160x16, 20 tiles across, 2 frames)
            src_x = index * 8
            src_y = self.terrain_frame * 8  # Use current animation frame
            
            # Draw from terrain strip
            if transparent_color is None:
                pyxel.blt(x, y, self.terrain_img, src_x, src_y, 8, 8)
            else:
                pyxel.blt(x, y, self.terrain_img, src_x, src_y, 8, 8, transparent_color)
            return
        
        # Regular tile drawing
        if tile_id not in self.tile_images:
            # Missing tile - draw red error square
            pyxel.rect(x, y, 8, 8, 8)
            pyxel.text(x + 2, y + 3, "?", 7)
            return
        
        img = self.tile_images[tile_id]
        
        # Special handling for large tiles
        if tile_id in self.large_tiles:
            expected_size = self.large_tiles[tile_id]
            # Use multiple 8x8 draws for large tiles to ensure proper display
            if expected_size == 16:
                # 16x16 tile - draw as 2x2 grid of 8x8
                for dy in range(2):
                    for dx in range(2):
                        src_x = dx * 8
                        src_y = dy * 8
                        dst_x = x + dx * 8
                        dst_y = y + dy * 8
                        if transparent_color is None:
                            pyxel.blt(dst_x, dst_y, img, src_x, src_y, 8, 8)
                        else:
                            pyxel.blt(dst_x, dst_y, img, src_x, src_y, 8, 8, transparent_color)
            elif expected_size == 24:
                # 24x24 tile - draw as 3x3 grid of 8x8
                for dy in range(3):
                    for dx in range(3):
                        src_x = dx * 8
                        src_y = dy * 8
                        dst_x = x + dx * 8
                        dst_y = y + dy * 8
                        if transparent_color is None:
                            pyxel.blt(dst_x, dst_y, img, src_x, src_y, 8, 8)
                        else:
                            pyxel.blt(dst_x, dst_y, img, src_x, src_y, 8, 8, transparent_color)
            elif expected_size == 32:
                # 32x32 tile - draw as 4x4 grid of 8x8
                for dy in range(4):
                    for dx in range(4):
                        src_x = dx * 8
                        src_y = dy * 8
                        dst_x = x + dx * 8
                        dst_y = y + dy * 8
                        if transparent_color is None:
                            pyxel.blt(dst_x, dst_y, img, src_x, src_y, 8, 8)
                        else:
                            pyxel.blt(dst_x, dst_y, img, src_x, src_y, 8, 8, transparent_color)
            else:
                # Fallback to full image draw
                if transparent_color is None:
                    pyxel.blt(x, y, img, 0, 0, img.width, img.height)
                else:
                    pyxel.blt(x, y, img, 0, 0, img.width, img.height, transparent_color)
        else:
            # Regular 8x8 tile
            if transparent_color is None:
                pyxel.blt(x, y, img, 0, 0, img.width, img.height)
            else:
                pyxel.blt(x, y, img, 0, 0, img.width, img.height, transparent_color)
    
    def update_animation(self):
        """Update animation frame counter"""
        self.animation_timer += 1
        if self.animation_timer >= 15:  # Change frame every 15 frames
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4
            
        # Update terrain animation (slower, every 30 frames = 0.5 seconds)
        if pyxel.frame_count % 30 == 0:
            self.terrain_frame = (self.terrain_frame + 1) % 2  # Toggle between 0 and 1
    
    def draw_animated_tile(self, tile_id: str, x: int, y: int, transparent_color=None):
        """Draw a tile with animation support"""
        # Terrain tiles use the terrain animation frame
        if tile_id in self.terrain_indices:
            # Terrain tiles already handle animation in draw_tile
            self.draw_tile(tile_id, x, y, transparent_color)
        # Handle water animation
        elif tile_id == 'water' and tile_id in self.tile_images:
            img = self.tile_images[tile_id]
            # Water strip is 32x8 (4 frames of 8x8)
            frame_x = self.animation_frame * 8
            if transparent_color is None:
                pyxel.blt(x, y, img, frame_x, 0, 8, 8)
            else:
                pyxel.blt(x, y, img, frame_x, 0, 8, 8, transparent_color)
        else:
            # Use regular draw method
            self.draw_tile(tile_id, x, y, transparent_color)
    
    def get_road_tile_id(self, north=False, east=False, south=False, west=False) -> str:
        """Get appropriate road tile based on connections"""
        patterns = {
            (False, False, False, False): 'road_alone',
            (True, False, False, False): 'road_end_south',
            (False, True, False, False): 'road_end_west',
            (False, False, True, False): 'road_end_north',
            (False, False, False, True): 'road_end_east',
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
    
    def get_wire_tile_id(self, north=False, east=False, south=False, west=False, overlay=False) -> str:
        """Get appropriate wire/power line tile based on connections
        
        Args:
            north, east, south, west: Connection flags
            overlay: If True, return overlay version for roads/rails
        """
        patterns = {
            (False, False, False, False): 'wire_alone',
            # Single connections use continuous lines instead of ends
            (True, False, False, False): 'wire_vertical',    # North only -> vertical
            (False, True, False, False): 'wire_horizontal',  # East only -> horizontal  
            (False, False, True, False): 'wire_vertical',    # South only -> vertical
            (False, False, False, True): 'wire_horizontal',  # West only -> horizontal
            # Two connections
            (False, True, False, True): 'wire_horizontal',
            (True, False, True, False): 'wire_vertical',
            (False, True, True, False): 'wire_corner_nw',
            (False, False, True, True): 'wire_corner_ne',
            (True, False, False, True): 'wire_corner_se',
            (True, True, False, False): 'wire_corner_sw',
            # Three and four connections
            (True, True, True, False): 'wire_t_east',
            (True, False, True, True): 'wire_t_west',
            (False, True, True, True): 'wire_t_south',
            (True, True, False, True): 'wire_t_north',
            (True, True, True, True): 'wire_cross',
        }
        
        # Add overlay prefix if this is for overlay on roads/rails
        if overlay:
            patterns = {
                (False, False, False, False): 'wire_overlay_alone',
                # Single connections use continuous lines for overlays too
                (True, False, False, False): 'wire_overlay_vertical',    # North only -> vertical
                (False, True, False, False): 'wire_overlay_horizontal',  # East only -> horizontal  
                (False, False, True, False): 'wire_overlay_vertical',    # South only -> vertical
                (False, False, False, True): 'wire_overlay_horizontal',  # West only -> horizontal
                # Two connections
                (False, True, False, True): 'wire_overlay_horizontal',
                (True, False, True, False): 'wire_overlay_vertical',
                (False, True, True, False): 'wire_overlay_corner_nw',
                (False, False, True, True): 'wire_overlay_corner_ne',
                (True, False, False, True): 'wire_overlay_corner_se',
                (True, True, False, False): 'wire_overlay_corner_sw',
                # Three and four connections
                (True, True, True, False): 'wire_overlay_t_east',
                (True, False, True, True): 'wire_overlay_t_west',
                (False, True, True, True): 'wire_overlay_t_south',
                (True, True, False, True): 'wire_overlay_t_north',
                (True, True, True, True): 'wire_overlay_cross',
            }
        # Return appropriate default based on overlay flag
        default = 'wire_overlay_alone' if overlay else 'wire_alone'
        return patterns.get((north, east, south, west), default)
    
    def get_building_tile_id(self, building_type: str, density: int) -> str:
        """Get appropriate building tile based on type and density"""
        building_map = {
            'residential': 'residential',
            'commercial': 'commercial',
            'industrial': 'industrial'
        }
        
        prefix = building_map.get(building_type, building_type)
        
        if prefix in ['residential', 'commercial', 'industrial']:
            return f"{prefix}_{min(max(density, 1), 4)}"
        
        return building_type


# Test function
def test_image_tiles():
    """Test the image tile system"""
    print("🧪 Testing Image Tile System")
    
    pyxel.init(320, 288, title="Image Tile Test")
    
    tile_system = ImageTileSystem()
    tile_system.initialize()
    
    def update():
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
        tile_system.update_animation()
    
    def draw():
        pyxel.cls(0)
        
        # Draw title
        pyxel.text(10, 10, "Image Tile System Test", 7)
        
        # Test large tiles
        pyxel.text(10, 30, "Large tiles (32x32, 24x24):", 7)
        
        # Coal plant (32x32)
        tile_system.draw_tile('coal_plant', 10, 45)
        pyxel.rectb(10, 45, 32, 32, 10)
        pyxel.text(10, 78, "Coal", 7)
        
        # Nuclear plant (32x32)
        tile_system.draw_tile('nuclear_plant', 50, 45)
        pyxel.rectb(50, 45, 32, 32, 11)
        pyxel.text(50, 78, "Nuclear", 7)
        
        # Police (24x24)
        tile_system.draw_tile('police', 90, 45)
        pyxel.rectb(90, 45, 24, 24, 12)
        pyxel.text(90, 70, "Police", 7)
        
        # Fire (24x24)
        tile_system.draw_tile('fire', 120, 45)
        pyxel.rectb(120, 45, 24, 24, 13)
        pyxel.text(120, 70, "Fire", 7)
        
        # Test regular tiles
        pyxel.text(10, 100, "Regular tiles (8x8):", 7)
        
        test_tiles = ['grass', 'road_horizontal', 'rail_vertical', 'park']
        for i, tile_id in enumerate(test_tiles):
            x = 10 + i * 20
            y = 115
            tile_system.draw_tile(tile_id, x, y)
            pyxel.rectb(x, y, 8, 8, 6)
        
        # Test water animation
        pyxel.text(10, 140, "Water animation:", 7)
        tile_system.draw_animated_tile('water', 10, 155)
        
        pyxel.text(10, 270, "ESC: Exit", 7)
    
    pyxel.run(update, draw)

if __name__ == "__main__":
    test_image_tiles()