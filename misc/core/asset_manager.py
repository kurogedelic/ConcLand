"""
Asset management system for ConcLand
Handles loading and management of images, sprites, and other assets
"""
import pyxel
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class AssetInfo:
    """Information about a loaded asset"""
    path: str
    image_bank: int
    x: int
    y: int
    width: int
    height: int
    
@dataclass 
class SpriteSheet:
    """Sprite sheet information"""
    image_bank: int
    tile_width: int
    tile_height: int
    columns: int
    rows: int

class AssetManager:
    """Manages all game assets"""
    
    def __init__(self):
        self.loaded_assets: Dict[str, AssetInfo] = {}
        self.sprite_sheets: Dict[str, SpriteSheet] = {}
        
        # Image bank allocation
        self.bank_allocation = {
            0: "tilemap",      # Reserved for tilemap
            1: "buildings",    # Building sprites
            2: "tool_icons",   # Tool palette icons
            3: "ui_elements", # UI elements
            4: "effects",      # Visual effects
            5: "terrain",      # Terrain textures
            6: "characters",   # Character sprites (future)
            7: "misc"         # Miscellaneous
        }
        
        # Asset paths
        self.asset_paths = {
            "tool_icons": "assets/tool_icons.png",
            "building_sprites": "assets/building_sprites.png",
            "button_frames": "assets/ui/button_frames.png",
            "panels": "assets/ui/panels.png",
            "progress_bars": "assets/ui/progress_bars.png",
            "elements": "assets/ui/elements.png",
            "notifications": "assets/ui/notifications.png"
        }
    
    def initialize(self) -> bool:
        """Initialize and load all assets"""
        success = True
        
        # Load tool icons
        if self.load_image("tool_icons", 2):
            self.sprite_sheets["tool_icons"] = SpriteSheet(
                image_bank=2,
                tile_width=16,
                tile_height=16,
                columns=8,
                rows=2
            )
        else:
            success = False
        
        # Load building sprites
        if self.load_image("building_sprites", 1):
            self.sprite_sheets["building_sprites"] = SpriteSheet(
                image_bank=1,
                tile_width=32,
                tile_height=32,
                columns=8,
                rows=3
            )
        else:
            success = False
        
        # Load UI elements
        ui_assets = [
            ("button_frames", 3, 0, 0),
            ("panels", 3, 0, 32),
            ("progress_bars", 3, 0, 96),
            ("elements", 3, 0, 112),
            ("notifications", 3, 0, 144)
        ]
        
        for asset_name, bank, x, y in ui_assets:
            if not self.load_image(asset_name, bank, x, y):
                print(f"Warning: Could not load {asset_name}")
        
        return success
    
    def load_image(self, asset_name: str, image_bank: int, 
                   x: int = 0, y: int = 0) -> bool:
        """Load an image asset into specified image bank"""
        if asset_name not in self.asset_paths:
            print(f"Unknown asset: {asset_name}")
            return False
        
        path = self.asset_paths[asset_name]
        if not os.path.exists(path):
            print(f"Asset file not found: {path}")
            return False
        
        try:
            # Load image into Pyxel image bank
            pyxel.images[image_bank].load(x, y, path)
            
            # Store asset info
            self.loaded_assets[asset_name] = AssetInfo(
                path=path,
                image_bank=image_bank,
                x=x,
                y=y,
                width=0,  # Would need PIL to get actual dimensions
                height=0
            )
            
            print(f"Loaded asset: {asset_name} -> bank {image_bank}")
            return True
            
        except Exception as e:
            print(f"Failed to load asset {asset_name}: {e}")
            return False
    
    def get_sprite_sheet(self, name: str) -> Optional[SpriteSheet]:
        """Get sprite sheet information"""
        return self.sprite_sheets.get(name)
    
    def draw_sprite(self, sprite_sheet_name: str, sprite_index: int,
                   x: int, y: int, w: Optional[int] = None, 
                   h: Optional[int] = None, colkey: int = 0) -> bool:
        """Draw a sprite from a sprite sheet"""
        sheet = self.sprite_sheets.get(sprite_sheet_name)
        if not sheet:
            return False
        
        # Calculate sprite position in sheet
        col = sprite_index % sheet.columns
        row = sprite_index // sheet.columns
        
        if row >= sheet.rows:
            return False
        
        src_x = col * sheet.tile_width
        src_y = row * sheet.tile_height
        
        # Use provided dimensions or tile size
        width = w if w is not None else sheet.tile_width
        height = h if h is not None else sheet.tile_height
        
        # Draw sprite
        pyxel.blt(x, y, sheet.image_bank, src_x, src_y, 
                 width, height, colkey)
        
        return True
    
    def draw_ui_element(self, element_type: str, state: int,
                       x: int, y: int, w: int, h: int) -> bool:
        """Draw a UI element (button, panel, etc.)"""
        if element_type == "button":
            # Button states: 0=normal, 1=hover, 2=active, 3=disabled
            if "button_frames" in self.loaded_assets:
                asset = self.loaded_assets["button_frames"]
                src_x = state * 32  # Each button frame is 32px wide
                pyxel.blt(x, y, asset.image_bank, src_x, 0, 
                         min(w, 32), min(h, 32), 0)
                return True
        
        elif element_type == "panel":
            # Panel types: 0=solid, 1=gradient, 2=textured
            if "panels" in self.loaded_assets:
                asset = self.loaded_assets["panels"]
                src_x = state * 64  # Each panel is 64px wide
                
                # Tile the panel to fill the area
                for py in range(0, h, 64):
                    for px in range(0, w, 64):
                        pyxel.blt(x + px, y + py, asset.image_bank,
                                 src_x, 32, min(64, w - px), min(64, h - py), 0)
                return True
        
        return False
    
    def is_loaded(self, asset_name: str) -> bool:
        """Check if an asset is loaded"""
        return asset_name in self.loaded_assets

class SpriteRenderer:
    """High-level sprite rendering utilities"""
    
    def __init__(self, asset_manager: AssetManager):
        self.asset_manager = asset_manager
    
    def draw_building(self, building_type: str, x: int, y: int, 
                     size: int = 32, animated: bool = False, 
                     frame: int = 0) -> bool:
        """Draw a building sprite"""
        # Building type to sprite index mapping
        building_sprite_map = {
            # Era 1 buildings
            "RESIDENCE": 0,       # barracks
            "COMMERCIAL": 1,      # small_shop
            "POLICE": 2,          # police_box
            "SCHOOL": 3,          # elementary_school
            # Era 2 buildings  
            "PUBLIC_HOUSING": 4,  # public_housing
            "SHOPPING_STREET": 5, # shopping_street
            "INDUSTRIAL": 6,      # small_factory
            "HOSPITAL": 7,        # clinic
            # Era 3 buildings
            "HIGH_RISE": 8,       # high_rise
            "DEPARTMENT": 9,      # department_store
            "GENERAL_HOSPITAL": 10, # general_hospital
            "STATION": 11,        # train_station
            # Era 4 buildings
            "HIGHWAY": 12,        # highway
            "TV_TOWER": 13,       # tv_tower
            "NUCLEAR": 14,        # nuclear_plant
            "AIRPORT": 15,        # airport
            # Infrastructure
            "POWERPLANT": 16,     # coal_plant
            "SOLAR": 17,          # solar_panel
            "WIND": 18,           # wind_turbine
            "GAS": 19,            # gas_plant
            # Nature/Culture
            "AGRICULTURAL": 20,   # rice_field
            "PARK": 21,           # park
            "SHRINE": 22,         # shrine
            "ROAD": 23            # road
        }
        
        sprite_index = building_sprite_map.get(building_type)
        
        # Try to draw sprite from sheet first
        if sprite_index is not None and self.asset_manager.draw_sprite(
            "building_sprites", sprite_index, x, y, size, size, 0
        ):
            return True
        
        # Fallback to colored rectangles
        building_colors = {
            "RESIDENCE": 11,      # Green
            "COMMERCIAL": 12,     # Blue  
            "INDUSTRIAL": 10,     # Yellow
            "ROAD": 5,           # Dark gray
            "POWERPLANT": 8,     # Red
            "AGRICULTURAL": 4,    # Brown
            "SOLAR": 10,         # Yellow
            "WIND": 7,           # White
            "NUCLEAR": 9,        # Orange
            "GAS": 14,           # Pink
            "PARK": 11,          # Green
            "SHRINE": 8,         # Red
            "SCHOOL": 9,         # Orange
            "HOSPITAL": 8,       # Red
            "POLICE": 12         # Blue
        }
        
        color = building_colors.get(building_type, 7)
        pyxel.rect(x, y, size, size, color)
        
        # Add simple details for some buildings
        if building_type == "RESIDENCE":
            # Door
            pyxel.rect(x + size//3, y + size*2//3, size//3, size//3, 4)
        elif building_type == "COMMERCIAL":
            # Windows
            pyxel.rect(x + 2, y + 2, size//3-2, size//3-2, 7)
            pyxel.rect(x + size*2//3, y + 2, size//3-2, size//3-2, 7)
        elif building_type == "POWERPLANT":
            # Chimney
            pyxel.rect(x + size*2//3, y, size//4, size//2, 5)
        
        return True
    
    def draw_terrain(self, terrain_type: str, x: int, y: int, 
                    size: int = 8, variation: int = 0) -> bool:
        """Draw terrain tile"""
        terrain_colors = {
            "water": [12, 1],      # Blue shades
            "grass": [11, 3],      # Green shades
            "soil": [4, 9],        # Brown shades
            "sand": [10, 15],      # Yellow/beige shades
            "rock": [5, 13]        # Gray shades
        }
        
        colors = terrain_colors.get(terrain_type, [7])
        color = colors[variation % len(colors)]
        
        pyxel.rect(x, y, size, size, color)
        
        # Add texture patterns
        if terrain_type == "water" and variation % 2 == 0:
            # Wave pattern
            pyxel.pset(x + 1, y + 1, 7)
            pyxel.pset(x + size - 2, y + size - 2, 7)
        elif terrain_type == "grass":
            # Grass blades
            if variation % 3 == 0:
                pyxel.line(x + 2, y + size - 1, x + 2, y + size - 3, 3)
                pyxel.line(x + size - 3, y + size - 1, x + size - 3, y + size - 3, 3)
        
        return True

# Global asset manager instance
_asset_manager = None

def get_asset_manager() -> AssetManager:
    """Get or create global asset manager"""
    global _asset_manager
    if _asset_manager is None:
        _asset_manager = AssetManager()
        _asset_manager.initialize()
    return _asset_manager