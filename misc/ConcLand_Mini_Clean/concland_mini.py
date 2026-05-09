#!/usr/bin/env python3
"""
ConcLand Mini - Minimal City Simulation Game
Based on original SimCity (1989) mechanics
Game Boy resolution: 160x144
"""

import pyxel
import random
import sys
import os
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional
from concland_tile_system import ConcLandTileManager

# Add font support - look in both assets and project root
font_paths = [
    os.path.join(os.path.dirname(__file__), 'assets'),
    os.path.dirname(__file__)
]
for path in font_paths:
    sys.path.append(path)

try:
    from font.bdfrenderer import BDFRenderer
    FONT_AVAILABLE = True
except ImportError:
    try:
        # Try to import from project root
        from bdfrenderer_fixed import BDFRenderer
        FONT_AVAILABLE = True
    except ImportError:
        FONT_AVAILABLE = False
        print("Warning: Japanese font not available")

# Double resolution for better visibility
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 288
WINDOW_SCALE = 1  # No additional scaling needed
MAP_SIZE = 32  # 32x32 tiles
TILE_SIZE = 16

class CellType(Enum):
    EMPTY = 0
    RESIDENTIAL = 1
    COMMERCIAL = 2
    INDUSTRIAL = 3
    ROAD = 4
    RAIL = 5
    WIRE = 6
    PARK = 7
    WATER = 8
    COAL_PLANT = 9
    OIL_PLANT = 10
    NUCLEAR_PLANT = 11
    POLICE = 12
    FIRE = 13
    HOSPITAL = 14
    SCHOOL = 15

class ToolMode(Enum):
    BULLDOZE = 0
    RESIDENTIAL = 1
    COMMERCIAL = 2
    INDUSTRIAL = 3
    ROAD = 4
    RAIL = 5
    WIRE = 6
    PARK = 7
    COAL_PLANT = 8
    POLICE = 9

@dataclass
class SimData:
    """Simulation data for each cell"""
    population: int = 0
    pollution: int = 0
    land_value: int = 128  # 0-255
    power: bool = False
    traffic: int = 0
    density: int = 0  # Building density 0-4
    building_id: int = 0  # For tracking 3x3 buildings

class ConcLandMini:
    def __init__(self):
        # Initialize Pyxel with doubled resolution
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="ConcLand Mini", fps=60)
        
        # Game state
        self.running = True
        self.camera_x = 0
        self.camera_y = 0
        self.cursor_x = 8  # Start at center
        self.cursor_y = 8
        self.current_tool = ToolMode.RESIDENTIAL
        self.funds = 10000
        self.population = 0
        self.simulation_tick = 0
        self.next_building_id = 1  # For tracking 3x3 buildings
        
        # Maps
        self.grid = [[CellType.EMPTY for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
        self.sim_data = [[SimData() for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
        
        # RCI Demand (-100 to 100)
        self.res_demand = 50
        self.com_demand = 30
        self.ind_demand = 20
        
        # View mode
        self.view_mode = 0  # 0=normal, 1=pollution, 2=land_value, 3=power
        
        # Input state
        self.key_repeat_timer = 0
        self.key_repeat_delay = 10
        
        # Initialize game world
        self._init_world()
        
        # Load assets (will be created later)
        self._init_assets()
        
        # Initialize Japanese font
        self._init_font()
        
        # Start game loop
        pyxel.run(self.update, self.draw)
    
    def _init_world(self):
        """Initialize the game world with some basic terrain"""
        # Add a river through the middle
        for y in range(12, 20):
            for x in range(0, MAP_SIZE):
                if 14 <= y <= 16:
                    self.grid[y][x] = CellType.WATER
        
        # Add some initial roads
        for x in range(8, 24):
            if self.grid[10][x] != CellType.WATER:
                self.grid[10][x] = CellType.ROAD
                self.sim_data[10][x].power = True
        
        for y in range(4, 12):
            if self.grid[y][16] != CellType.WATER:
                self.grid[y][16] = CellType.ROAD
                self.sim_data[y][16].power = True
        
        # Add a 3x3 power plant
        if self._can_place_3x3_building(18, 6):
            self._place_3x3_building(18, 6, CellType.COAL_PLANT)
        self._spread_power()
    
    def _init_assets(self):
        """Initialize graphics assets"""
        # Initialize tile manager
        self.tile_manager = ConcLandTileManager()
        
        # Try to load PNG tilemap (try converted versions first)  
        tilemap_paths = [
            'assets/concland_tiles_indexed.png',
            'assets/concland_tiles_rgb.png',
            'assets/concland_tiles_16x16.png', 
            'assets/tiles_16x16.png',
            'assets/tilemap_generated.png'
        ]
        
        self.use_graphics = False
        # Log to file for debugging
        with open('concland_debug.log', 'w') as f:
            f.write("=== ConcLand Mini PNG Loading ===\n")
            for path in tilemap_paths:
                exists = os.path.exists(path)
                f.write(f"Checking: {path} - {'EXISTS' if exists else 'MISSING'}\n")
                if exists:
                    try:
                        if self.tile_manager.load_tilemap(path):
                            self.use_graphics = True
                            f.write(f"SUCCESS: Loaded tilemap: {path}\n")
                            break
                        else:
                            f.write(f"FAILED: Could not load {path}\n")
                    except Exception as e:
                        f.write(f"ERROR loading {path}: {e}\n")
            
            f.write(f"Graphics status: {'ENABLED' if self.use_graphics else 'DISABLED (using fallback)'}\n")
        
        print("=== ConcLand Mini PNG Loading ===")
        for path in tilemap_paths:
            print(f"Checking: {path} - {'EXISTS' if os.path.exists(path) else 'MISSING'}")
            if os.path.exists(path):
                try:
                    if self.tile_manager.load_tilemap(path):
                        self.use_graphics = True
                        print(f"SUCCESS: Loaded tilemap: {path}")
                        break
                    else:
                        print(f"FAILED: Could not load {path}")
                except Exception as e:
                    print(f"ERROR loading {path}: {e}")
        
        print(f"Graphics status: {'ENABLED' if self.use_graphics else 'DISABLED (using fallback)'}")
        if not self.use_graphics:
            print("Warning: Could not load tile graphics, using fallback colors")
        
        # Load 256-color palette
        try:
            pyxel.images[1].load(0, 0, "assets/palette256.png", incl_colors=True)
            self.palette_loaded = True
        except:
            self.palette_loaded = False
            print("Warning: Could not load 256-color palette")
        
        # Tile mapping for graphics
        self.tile_map = {
            CellType.EMPTY: 0,
            CellType.RESIDENTIAL: 1,
            CellType.COMMERCIAL: 2,
            CellType.INDUSTRIAL: 3,
            CellType.ROAD: 4,
            CellType.RAIL: 5,
            CellType.WIRE: 6,
            CellType.PARK: 7,
            CellType.WATER: 8,
            CellType.COAL_PLANT: 9,
            CellType.OIL_PLANT: 10,
            CellType.NUCLEAR_PLANT: 11,
            CellType.POLICE: 12,
            CellType.FIRE: 13,
            CellType.HOSPITAL: 14,
            CellType.SCHOOL: 15
        }
        
        # Fallback colors if graphics don't load
        self.tile_colors = {
            CellType.EMPTY: 3,      # Green
            CellType.RESIDENTIAL: 10, # Light blue
            CellType.COMMERCIAL: 12,  # Light green
            CellType.INDUSTRIAL: 4,   # Brown
            CellType.ROAD: 13,        # Gray
            CellType.RAIL: 1,         # Dark blue
            CellType.WIRE: 9,         # Orange
            CellType.PARK: 11,        # Bright green
            CellType.WATER: 5,        # Blue
            CellType.COAL_PLANT: 2,   # Purple
            CellType.OIL_PLANT: 8,    # Red
            CellType.NUCLEAR_PLANT: 7, # White
            CellType.POLICE: 1,       # Dark blue
            CellType.FIRE: 8,         # Red
            CellType.HOSPITAL: 7,     # White
            CellType.SCHOOL: 9        # Orange
        }
    
    def _init_font(self):
        """Initialize Japanese font support"""
        self.font_loaded = False
        
        if FONT_AVAILABLE:
            # Simple direct loading
            try:
                font_path = "assets/font/umplus_j10r.bdf"
                if os.path.exists(font_path):
                    self.font_renderer = BDFRenderer(font_path)
                    self.font_loaded = True
            except Exception:
                # Fallback to English if font loading fails
                self.font_loaded = False
    
    def _draw_japanese_text(self, x: int, y: int, text: str, color: int = 7):
        """Draw Japanese text using BDF font"""
        if self.font_loaded:
            try:
                self.font_renderer.draw_text(x, y, text, color)  # 正しいメソッド名
            except Exception as e:
                # Fallback to English text if Japanese rendering fails
                pyxel.text(x, y, text, color)
        else:
            # Fallback to English text
            pyxel.text(x, y, text, color)
    
    def update(self):
        """Main game update loop"""
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        
        self._handle_input()
        self._update_simulation()
        
        # Update camera to follow cursor
        self._update_camera()
    
    def _handle_input(self):
        """Handle keyboard input with repeat"""
        # Reduce key repeat timer
        if self.key_repeat_timer > 0:
            self.key_repeat_timer -= 1
        
        # Cursor movement with repeat
        if self.key_repeat_timer == 0:
            moved = False
            if pyxel.btn(pyxel.KEY_LEFT) and self.cursor_x > 0:
                self.cursor_x -= 1
                moved = True
            elif pyxel.btn(pyxel.KEY_RIGHT) and self.cursor_x < MAP_SIZE - 1:
                self.cursor_x += 1
                moved = True
            elif pyxel.btn(pyxel.KEY_UP) and self.cursor_y > 0:
                self.cursor_y -= 1
                moved = True
            elif pyxel.btn(pyxel.KEY_DOWN) and self.cursor_y < MAP_SIZE - 1:
                self.cursor_y += 1
                moved = True
            
            if moved:
                self.key_repeat_timer = self.key_repeat_delay
        
        # Tool selection
        if pyxel.btnp(pyxel.KEY_1):
            self.current_tool = ToolMode.RESIDENTIAL
        elif pyxel.btnp(pyxel.KEY_2):
            self.current_tool = ToolMode.COMMERCIAL
        elif pyxel.btnp(pyxel.KEY_3):
            self.current_tool = ToolMode.INDUSTRIAL
        elif pyxel.btnp(pyxel.KEY_4):
            self.current_tool = ToolMode.ROAD
        elif pyxel.btnp(pyxel.KEY_5):
            self.current_tool = ToolMode.PARK
        elif pyxel.btnp(pyxel.KEY_6):
            self.current_tool = ToolMode.RAIL
        elif pyxel.btnp(pyxel.KEY_7):
            self.current_tool = ToolMode.WIRE  
        elif pyxel.btnp(pyxel.KEY_8):
            self.current_tool = ToolMode.COAL_PLANT
        elif pyxel.btnp(pyxel.KEY_9):
            self.current_tool = ToolMode.POLICE
        elif pyxel.btnp(pyxel.KEY_0):
            self.current_tool = ToolMode.BULLDOZE
        
        # View mode toggle - add traffic view
        if pyxel.btnp(pyxel.KEY_V):
            self.view_mode = (self.view_mode + 1) % 5  # 5 view modes now
        
        # Place/remove buildings
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z):
            self._place_building()
        
        # Remove buildings
        if pyxel.btnp(pyxel.KEY_X):
            self._remove_building()
    
    def _place_building(self):
        """Place a building at cursor position"""
        x, y = self.cursor_x, self.cursor_y
        
        if self.current_tool == ToolMode.BULLDOZE:
            self._remove_building()
            return
        
        # Can't build on water
        if self.grid[y][x] == CellType.WATER:
            return
        
        # Get cost for this building
        cost = self._get_building_cost(self.current_tool)
        if self.funds < cost:
            return
        
        new_type = self._tool_to_cell_type(self.current_tool)
        if not new_type:
            return
        
        # Check if this is a 3x3 building (RCI zones, power plants, police)
        if new_type in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL, CellType.COAL_PLANT, CellType.POLICE]:
            if self._can_place_3x3_building(x, y):
                self._place_3x3_building(x, y, new_type)
                self.funds -= cost
                if new_type == CellType.COAL_PLANT:
                    self._spread_power()
        else:
            # 1x1 buildings (roads, rails, wires, parks)
            if self.grid[y][x] == CellType.EMPTY or self.grid[y][x] != new_type:
                self.grid[y][x] = new_type
                self.sim_data[y][x] = SimData()
                self.funds -= cost
                if new_type in [CellType.ROAD, CellType.WIRE]:
                    self._spread_power()
    
    def _can_place_3x3_building(self, x: int, y: int) -> bool:
        """Check if a 3x3 building can be placed at position"""
        # Check bounds
        if x + 2 >= MAP_SIZE or y + 2 >= MAP_SIZE:
            return False
        
        # Check if all 9 cells are empty or water
        for dy in range(3):
            for dx in range(3):
                cell_type = self.grid[y + dy][x + dx]
                if cell_type != CellType.EMPTY and cell_type != CellType.WATER:
                    return False
        
        # Can't build on water
        if self.grid[y + 1][x + 1] == CellType.WATER:  # Center must not be water
            return False
            
        return True
    
    def _place_3x3_building(self, x: int, y: int, building_type: CellType):
        """Place a 3x3 building"""
        building_id = self.next_building_id
        self.next_building_id += 1
        
        # Place building in all 9 cells
        for dy in range(3):
            for dx in range(3):
                self.grid[y + dy][x + dx] = building_type
                self.sim_data[y + dy][x + dx] = SimData()
                self.sim_data[y + dy][x + dx].building_id = building_id
                
                # Power plants generate power
                if building_type == CellType.COAL_PLANT:
                    self.sim_data[y + dy][x + dx].power = True
    
    def _remove_building(self):
        """Remove building at cursor position"""
        x, y = self.cursor_x, self.cursor_y
        
        if self.grid[y][x] == CellType.EMPTY or self.grid[y][x] == CellType.WATER:
            return
        
        cell_type = self.grid[y][x]
        
        # If it's a 3x3 building, remove the entire building
        if cell_type in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL, CellType.COAL_PLANT, CellType.POLICE]:
            building_id = self.sim_data[y][x].building_id
            if building_id > 0:
                self._remove_3x3_building(building_id)
                self.funds += 10  # Larger refund for 3x3 buildings
            else:
                # Single cell of what should be a 3x3 building
                self.grid[y][x] = CellType.EMPTY
                self.sim_data[y][x] = SimData()
                self.funds += 5
        else:
            # 1x1 building (road, rail, wire, park)
            self.grid[y][x] = CellType.EMPTY
            self.sim_data[y][x] = SimData()
            self.funds += 2  # Small refund
        
        self._spread_power()
    
    def _remove_3x3_building(self, building_id: int):
        """Remove entire 3x3 building by ID"""
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                if self.sim_data[y][x].building_id == building_id:
                    self.grid[y][x] = CellType.EMPTY
                    self.sim_data[y][x] = SimData()
    
    def _tool_to_cell_type(self, tool: ToolMode) -> Optional[CellType]:
        """Convert tool mode to cell type"""
        mapping = {
            ToolMode.RESIDENTIAL: CellType.RESIDENTIAL,
            ToolMode.COMMERCIAL: CellType.COMMERCIAL,
            ToolMode.INDUSTRIAL: CellType.INDUSTRIAL,
            ToolMode.ROAD: CellType.ROAD,
            ToolMode.RAIL: CellType.RAIL,
            ToolMode.WIRE: CellType.WIRE,
            ToolMode.PARK: CellType.PARK,
            ToolMode.COAL_PLANT: CellType.COAL_PLANT,
            ToolMode.POLICE: CellType.POLICE
        }
        return mapping.get(tool)
    
    def _get_building_cost(self, tool: ToolMode) -> int:
        """Get the cost of a building"""
        costs = {
            ToolMode.BULLDOZE: 1,
            ToolMode.RESIDENTIAL: 100,
            ToolMode.COMMERCIAL: 100,
            ToolMode.INDUSTRIAL: 100,
            ToolMode.ROAD: 10,
            ToolMode.RAIL: 25,
            ToolMode.WIRE: 5,
            ToolMode.PARK: 20,
            ToolMode.COAL_PLANT: 3000,
            ToolMode.POLICE: 500
        }
        return costs.get(tool, 0)
    
    def _update_simulation(self):
        """Update simulation every few frames"""
        self.simulation_tick += 1
        
        # Run different simulation aspects at different intervals for performance
        if self.simulation_tick % 20 == 0:  # Every 0.33 second - faster growth
            self._update_rci_zones()
            self._calculate_population()
        
        if self.simulation_tick % 40 == 0:  # Every 0.67 second - environmental updates
            self._spread_pollution()
            self._calculate_land_value()
            self._update_rci_demand()
            
        # Add traffic calculation for better simulation
        if self.simulation_tick % 80 == 0:  # Every 1.33 second - traffic updates
            self._calculate_traffic()
    
    def _spread_power(self):
        """Spread power from power plants through roads and wires"""
        # Reset power grid
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                self.sim_data[y][x].power = False
        
        # Find power sources
        power_sources = []
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                if self.grid[y][x] in [CellType.COAL_PLANT, CellType.OIL_PLANT, CellType.NUCLEAR_PLANT]:
                    power_sources.append((x, y))
                    self.sim_data[y][x].power = True
        
        # Spread power through connected infrastructure
        changed = True
        while changed:
            changed = False
            for y in range(MAP_SIZE):
                for x in range(MAP_SIZE):
                    if not self.sim_data[y][x].power and self.grid[y][x] in [CellType.ROAD, CellType.WIRE]:
                        # Check adjacent cells for power
                        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE:
                                if self.sim_data[ny][nx].power:
                                    self.sim_data[y][x].power = True
                                    changed = True
                                    break
        
        # Power buildings adjacent to powered infrastructure
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                if not self.sim_data[y][x].power and self.grid[y][x] in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL, CellType.POLICE, CellType.FIRE, CellType.HOSPITAL, CellType.SCHOOL]:
                    # Check adjacent cells for powered infrastructure
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE:
                            if (self.sim_data[ny][nx].power and 
                                self.grid[ny][nx] in [CellType.ROAD, CellType.WIRE, CellType.COAL_PLANT, CellType.OIL_PLANT, CellType.NUCLEAR_PLANT]):
                                self.sim_data[y][x].power = True
                                break
    
    def _update_rci_zones(self):
        """Update RCI zone growth - only process center of 3x3 buildings"""
        processed_buildings = set()
        
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                cell_type = self.grid[y][x]
                if cell_type in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL]:
                    building_id = self.sim_data[y][x].building_id
                    
                    # Only process each 3x3 building once (from its center or any part)
                    if building_id > 0 and building_id not in processed_buildings:
                        processed_buildings.add(building_id)
                        self._update_zone_growth_3x3(building_id, cell_type)
    
    def _update_zone_growth_3x3(self, building_id: int, zone_type: CellType):
        """Update growth for a 3x3 building"""
        # Find the center cell of this building
        center_x, center_y = None, None
        total_population = 0
        total_pollution = 0
        total_land_value = 0
        total_traffic = 0
        cell_count = 0
        has_power = False
        
        # Aggregate data from all cells of this building
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                if self.sim_data[y][x].building_id == building_id:
                    cell_count += 1
                    total_population += self.sim_data[y][x].population
                    total_pollution += self.sim_data[y][x].pollution
                    total_land_value += self.sim_data[y][x].land_value
                    total_traffic += self.sim_data[y][x].traffic
                    if self.sim_data[y][x].power:
                        has_power = True
                    if center_x is None:  # Use first found cell as reference
                        center_x, center_y = x, y
        
        if cell_count == 0 or center_x is None:
            return
        
        # Calculate averages
        avg_pollution = total_pollution // cell_count
        avg_land_value = total_land_value // cell_count
        avg_traffic = total_traffic // cell_count
        
        # No growth without power, but slower decline
        if not has_power:
            new_population = max(0, total_population - 5)
            self._set_building_population(building_id, new_population)
            return
        
        # Calculate growth factors using averages
        demand = 0
        if zone_type == CellType.RESIDENTIAL:
            demand = self.res_demand
        elif zone_type == CellType.COMMERCIAL:
            demand = self.com_demand
        elif zone_type == CellType.INDUSTRIAL:
            demand = self.ind_demand
        
        # Enhanced growth probability
        base_chance = 0.2 if demand > 0 else 0.03
        land_value_factor = avg_land_value / 255.0
        pollution_factor = max(0.1, 1.0 - (avg_pollution / 255.0))
        
        # Traffic factor
        traffic_factor = 1.0
        if zone_type == CellType.COMMERCIAL and avg_traffic > 100:
            traffic_factor = max(0.5, 1.0 - (avg_traffic / 400.0))
        elif zone_type in [CellType.RESIDENTIAL, CellType.INDUSTRIAL] and avg_traffic > 150:
            traffic_factor = max(0.7, 1.0 - (avg_traffic / 500.0))
        
        # Adjacency bonus
        adjacency_bonus = 1.0
        if zone_type == CellType.RESIDENTIAL:
            nearby_commercial = self._count_nearby_type(center_x, center_y, CellType.COMMERCIAL, 5)
            nearby_parks = self._count_nearby_type(center_x, center_y, CellType.PARK, 3)
            adjacency_bonus = 1.0 + (nearby_commercial * 0.1) + (nearby_parks * 0.2)
        elif zone_type == CellType.COMMERCIAL:
            nearby_residential = self._count_nearby_type(center_x, center_y, CellType.RESIDENTIAL, 6)
            adjacency_bonus = 1.0 + (nearby_residential * 0.15)
        
        growth_chance = base_chance * land_value_factor * pollution_factor * traffic_factor * adjacency_bonus
        
        if random.random() < growth_chance:
            # Increase population for the entire 3x3 building
            max_pop = 2400  # 3x3 building can hold more population (800 * 3)
            if total_population < max_pop:
                growth_amount = random.randint(25, 75)  # Larger growth for 3x3
                new_population = min(total_population + growth_amount, max_pop)
                self._set_building_population(building_id, new_population)
    
    def _set_building_population(self, building_id: int, total_population: int):
        """Set population for entire 3x3 building"""
        cells = []
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                if self.sim_data[y][x].building_id == building_id:
                    cells.append((x, y))
        
        if not cells:
            return
        
        # Distribute population among cells
        pop_per_cell = total_population // len(cells)
        remaining_pop = total_population % len(cells)
        
        for i, (x, y) in enumerate(cells):
            self.sim_data[y][x].population = pop_per_cell
            if i < remaining_pop:  # Distribute remainder
                self.sim_data[y][x].population += 1
            
            # Update density based on population
            pop = self.sim_data[y][x].population
            if pop >= 640:
                self.sim_data[y][x].density = 4
            elif pop >= 480:
                self.sim_data[y][x].density = 3
            elif pop >= 320:
                self.sim_data[y][x].density = 2
            elif pop >= 160:
                self.sim_data[y][x].density = 1
            else:
                self.sim_data[y][x].density = 0

    def _update_zone_growth(self, x: int, y: int, zone_type: CellType):
        """Update growth for a specific zone with improved SimCity mechanics"""
        data = self.sim_data[y][x]
        
        # No growth without power, but slower decline
        if not data.power:
            data.population = max(0, data.population - 2)
            return
        
        # Calculate growth factors
        demand = 0
        if zone_type == CellType.RESIDENTIAL:
            demand = self.res_demand
        elif zone_type == CellType.COMMERCIAL:
            demand = self.com_demand
        elif zone_type == CellType.INDUSTRIAL:
            demand = self.ind_demand
        
        # Enhanced growth probability with traffic consideration
        base_chance = 0.2 if demand > 0 else 0.03
        land_value_factor = data.land_value / 255.0
        pollution_factor = max(0.1, 1.0 - (data.pollution / 255.0))
        
        # Traffic factor - too much traffic hurts commercial growth
        traffic_factor = 1.0
        if zone_type == CellType.COMMERCIAL and data.traffic > 100:
            traffic_factor = max(0.5, 1.0 - (data.traffic / 400.0))
        elif zone_type in [CellType.RESIDENTIAL, CellType.INDUSTRIAL] and data.traffic > 150:
            traffic_factor = max(0.7, 1.0 - (data.traffic / 500.0))
        
        # Adjacency bonus for mixed development
        adjacency_bonus = 1.0
        if zone_type == CellType.RESIDENTIAL:
            nearby_commercial = self._count_nearby_type(x, y, CellType.COMMERCIAL, 3)
            nearby_parks = self._count_nearby_type(x, y, CellType.PARK, 2)
            adjacency_bonus = 1.0 + (nearby_commercial * 0.1) + (nearby_parks * 0.2)
        elif zone_type == CellType.COMMERCIAL:
            nearby_residential = self._count_nearby_type(x, y, CellType.RESIDENTIAL, 4)
            adjacency_bonus = 1.0 + (nearby_residential * 0.15)
        
        growth_chance = base_chance * land_value_factor * pollution_factor * traffic_factor * adjacency_bonus
        
        if random.random() < growth_chance:
            # Increase population/density
            max_pop = 800  # Max population per cell (like SimCity original)
            if data.population < max_pop:
                growth_amount = random.randint(8, 25)  # Faster growth
                data.population += growth_amount
                data.population = min(data.population, max_pop)
                
                # Update density based on population (SimCity original thresholds)
                if data.population >= 640:
                    data.density = 4
                elif data.population >= 480:
                    data.density = 3
                elif data.population >= 320:
                    data.density = 2
                elif data.population >= 160:
                    data.density = 1
                else:
                    data.density = 0
    
    def _count_nearby_type(self, x: int, y: int, cell_type: CellType, radius: int) -> int:
        """Count nearby cells of specific type within radius"""
        count = 0
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE:
                    if self.grid[ny][nx] == cell_type:
                        count += 1
        return count
    
    def _spread_pollution(self):
        """Spread pollution using cellular automaton"""
        # Create new pollution map
        new_pollution = [[0 for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
        
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                current = self.sim_data[y][x].pollution
                
                # Add pollution sources
                if self.grid[y][x] == CellType.INDUSTRIAL and self.sim_data[y][x].density >= 1:
                    new_pollution[y][x] += 20 + self.sim_data[y][x].density * 10
                elif self.grid[y][x] == CellType.COAL_PLANT:
                    new_pollution[y][x] += 50
                elif self.grid[y][x] == CellType.OIL_PLANT:
                    new_pollution[y][x] += 30
                elif self.grid[y][x] == CellType.ROAD and self.sim_data[y][x].traffic > 50:
                    new_pollution[y][x] += self.sim_data[y][x].traffic // 15  # More traffic pollution
                
                # Spread existing pollution
                if current > 0:
                    # Natural decay
                    spread_amount = int(current * 0.8)
                    diffuse_amount = current - spread_amount
                    new_pollution[y][x] += spread_amount
                    
                    # Diffuse to neighbors
                    neighbors = 0
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE:
                            new_pollution[ny][nx] += diffuse_amount // 8
                            neighbors += 1
                
                # Parks reduce pollution
                if self.grid[y][x] == CellType.PARK:
                    new_pollution[y][x] = max(0, new_pollution[y][x] - 5)
                
                # Water reduces pollution
                if self.grid[y][x] == CellType.WATER:
                    new_pollution[y][x] = max(0, new_pollution[y][x] - 10)
                
                # Clamp pollution values
                new_pollution[y][x] = max(0, min(255, new_pollution[y][x]))
        
        # Update pollution map
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                self.sim_data[y][x].pollution = new_pollution[y][x]
    
    def _calculate_land_value(self):
        """Calculate land value based on various factors"""
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                # Base land value (higher near center)
                center_x, center_y = MAP_SIZE // 2, MAP_SIZE // 2
                distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                base_value = max(50, 200 - int(distance * 5))
                
                # Pollution reduces land value
                pollution_penalty = self.sim_data[y][x].pollution
                
                # Parks and commercial areas increase land value
                proximity_bonus = 0
                for dx in range(-3, 4):
                    for dy in range(-3, 4):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE:
                            if self.grid[ny][nx] == CellType.PARK:
                                proximity_bonus += max(0, 10 - abs(dx) - abs(dy))
                            elif self.grid[ny][nx] == CellType.COMMERCIAL and self.sim_data[ny][nx].density >= 2:
                                proximity_bonus += max(0, 5 - abs(dx) - abs(dy))
                
                # Calculate final land value
                land_value = base_value - pollution_penalty + proximity_bonus
                self.sim_data[y][x].land_value = max(0, min(255, land_value))
    
    def _calculate_population(self):
        """Calculate total population"""
        self.population = 0
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                if self.grid[y][x] in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL]:
                    self.population += self.sim_data[y][x].population
    
    def _update_rci_demand(self):
        """Update RCI demand based on current city state"""
        total_res = sum(1 for y in range(MAP_SIZE) for x in range(MAP_SIZE) 
                       if self.grid[y][x] == CellType.RESIDENTIAL and self.sim_data[y][x].population > 0)
        total_com = sum(1 for y in range(MAP_SIZE) for x in range(MAP_SIZE) 
                       if self.grid[y][x] == CellType.COMMERCIAL and self.sim_data[y][x].population > 0)
        total_ind = sum(1 for y in range(MAP_SIZE) for x in range(MAP_SIZE) 
                       if self.grid[y][x] == CellType.INDUSTRIAL and self.sim_data[y][x].population > 0)
        
        # Calculate demand (improved SimCity formula with more realistic balancing)
        res_ratio = total_res / max(1, total_com + total_ind)
        
        self.res_demand = max(-100, min(100, 30 + (total_com + total_ind) * 4 - total_res * 3))
        self.com_demand = max(-100, min(100, 20 + self.population // 40 - total_com * 6 + total_res * 2))
        self.ind_demand = max(-100, min(100, 15 + self.population // 80 - total_ind * 4 + total_res))
    
    def _calculate_traffic(self):
        """Calculate traffic density based on commuting patterns"""
        # Reset traffic
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                self.sim_data[y][x].traffic = 0
        
        # Calculate traffic from residential to commercial/industrial
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                if self.grid[y][x] == CellType.RESIDENTIAL and self.sim_data[y][x].population > 20:
                    # Find nearest commercial/industrial within 8 tiles
                    traffic_generated = self.sim_data[y][x].population // 10
                    
                    for target_y in range(max(0, y-8), min(MAP_SIZE, y+9)):
                        for target_x in range(max(0, x-8), min(MAP_SIZE, x+9)):
                            if self.grid[target_y][target_x] in [CellType.COMMERCIAL, CellType.INDUSTRIAL]:
                                if self.sim_data[target_y][target_x].population > 0:
                                    # Simple path - add traffic to roads between
                                    self._add_traffic_to_path(x, y, target_x, target_y, traffic_generated // 4)
                                    break
    
    def _add_traffic_to_path(self, x1: int, y1: int, x2: int, y2: int, traffic: int):
        """Add traffic along simple path between two points"""
        # Simple Manhattan distance path
        cx, cy = x1, y1
        
        while cx != x2 or cy != y2:
            if self.grid[cy][cx] == CellType.ROAD:
                self.sim_data[cy][cx].traffic += traffic
            
            # Move towards target
            if cx < x2:
                cx += 1
            elif cx > x2:
                cx -= 1
            elif cy < y2:
                cy += 1
            elif cy > y2:
                cy -= 1
                
            # Avoid infinite loop
            if abs(cx - x1) + abs(cy - y1) > 16:
                break
    
    def _update_camera(self):
        """Update camera to center on cursor"""
        # Calculate target camera position
        target_x = self.cursor_x * TILE_SIZE - SCREEN_WIDTH // 2
        target_y = self.cursor_y * TILE_SIZE - SCREEN_HEIGHT // 2
        
        # Clamp camera to map bounds
        max_camera_x = MAP_SIZE * TILE_SIZE - SCREEN_WIDTH
        max_camera_y = MAP_SIZE * TILE_SIZE - SCREEN_HEIGHT
        
        self.camera_x = max(0, min(target_x, max_camera_x))
        self.camera_y = max(0, min(target_y, max_camera_y))
    
    def draw(self):
        """Main drawing function"""
        pyxel.cls(0)
        
        # Draw map
        self._draw_map()
        
        # Draw cursor
        self._draw_cursor()
        
        # Draw UI (must be last to overlay on top)
        self._draw_ui()
    
    def _draw_map(self):
        """Draw the game map"""
        # Calculate visible tile range
        start_x = max(0, self.camera_x // TILE_SIZE)
        start_y = max(0, self.camera_y // TILE_SIZE)
        end_x = min(MAP_SIZE, (self.camera_x + SCREEN_WIDTH) // TILE_SIZE + 1)
        end_y = min(MAP_SIZE, (self.camera_y + SCREEN_HEIGHT) // TILE_SIZE + 1)
        
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                # Calculate screen position
                screen_x = x * TILE_SIZE - self.camera_x
                screen_y = y * TILE_SIZE - self.camera_y
                
                # Skip if off screen
                if screen_x < -TILE_SIZE or screen_x >= SCREEN_WIDTH:
                    continue
                if screen_y < -TILE_SIZE or screen_y >= SCREEN_HEIGHT:
                    continue
                
                # Draw tile based on view mode
                self._draw_tile(x, y, screen_x, screen_y)
    
    def _draw_tile(self, x: int, y: int, screen_x: int, screen_y: int):
        """Draw a single tile"""
        cell_type = self.grid[y][x]
        data = self.sim_data[y][x]
        
        if self.view_mode == 0 and self.use_graphics:  # Normal view with graphics
            # Draw base terrain first (tile_id, x, y order)
            if cell_type == CellType.WATER:
                self.tile_manager.draw_tile('water', screen_x, screen_y)
            elif cell_type == CellType.EMPTY:
                self.tile_manager.draw_tile('empty', screen_x, screen_y)
            else:
                self.tile_manager.draw_tile('grass', screen_x, screen_y)
            
            # Draw the actual tile based on type (don't redraw background)
            if cell_type == CellType.ROAD:
                # Check connections for roads
                north = y > 0 and self.grid[y-1][x] == CellType.ROAD
                south = y < MAP_SIZE-1 and self.grid[y+1][x] == CellType.ROAD
                east = x < MAP_SIZE-1 and self.grid[y][x+1] == CellType.ROAD
                west = x > 0 and self.grid[y][x-1] == CellType.ROAD
                
                road_tile = self.tile_manager.get_road_tile_id(north, east, south, west)
                self.tile_manager.draw_tile(road_tile, screen_x, screen_y)
                
            elif cell_type == CellType.RAIL:
                # Check connections for rails
                north = y > 0 and self.grid[y-1][x] == CellType.RAIL
                south = y < MAP_SIZE-1 and self.grid[y+1][x] == CellType.RAIL
                east = x < MAP_SIZE-1 and self.grid[y][x+1] == CellType.RAIL
                west = x > 0 and self.grid[y][x-1] == CellType.RAIL
                
                rail_tile = self.tile_manager.get_rail_tile_id(north, east, south, west)
                self.tile_manager.draw_tile(rail_tile, screen_x, screen_y)
                
            elif cell_type in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL]:
                # Draw RCI buildings based on density
                if data.density > 0:  # Only draw building if there's actual development
                    building_type = {
                        CellType.RESIDENTIAL: 'residential',
                        CellType.COMMERCIAL: 'commercial', 
                        CellType.INDUSTRIAL: 'industrial'
                    }[cell_type]
                    
                    tile_id = self.tile_manager.get_building_tile_id(building_type, data.density)
                    self.tile_manager.draw_tile(tile_id, screen_x, screen_y)
                
                # Show unpowered buildings with red X
                if not data.power:
                    pyxel.line(screen_x + 2, screen_y + 2, screen_x + 13, screen_y + 13, 8)
                    pyxel.line(screen_x + 13, screen_y + 2, screen_x + 2, screen_y + 13, 8)
                    
            elif cell_type == CellType.WIRE:
                self.tile_manager.draw_tile('wire', screen_x, screen_y)
            elif cell_type == CellType.PARK:
                self.tile_manager.draw_tile('park', screen_x, screen_y)
            elif cell_type == CellType.COAL_PLANT:
                self.tile_manager.draw_tile('coal_plant', screen_x, screen_y)
            elif cell_type == CellType.OIL_PLANT:
                self.tile_manager.draw_tile('oil_plant', screen_x, screen_y)
            elif cell_type == CellType.NUCLEAR_PLANT:
                self.tile_manager.draw_tile('nuclear_plant', screen_x, screen_y)
            elif cell_type == CellType.POLICE:
                self.tile_manager.draw_tile('police', screen_x, screen_y)
            elif cell_type == CellType.FIRE:
                self.tile_manager.draw_tile('fire', screen_x, screen_y)
            elif cell_type == CellType.HOSPITAL:
                self.tile_manager.draw_tile('hospital', screen_x, screen_y)
            elif cell_type == CellType.SCHOOL:
                self.tile_manager.draw_tile('school', screen_x, screen_y)
            
        else:  # Fallback to colored rectangles or data view modes
            if self.view_mode == 0:  # Normal view fallback
                color = self.tile_colors.get(cell_type, 0)
                
                # Adjust color based on density for RCI zones
                if cell_type in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL]:
                    if data.density >= 3:
                        color = 7  # White for high density
                    elif data.density >= 2:
                        color = 6  # Light color for medium density
                    elif data.density >= 1:
                        color = self.tile_colors[cell_type]
                    else:
                        color = 15  # Very light for low density
                    
                    # Show unpowered buildings darker
                    if not data.power:
                        color = 1  # Dark color for unpowered
                
            elif self.view_mode == 1:  # Pollution view
                pollution_level = data.pollution
                if self.palette_loaded:
                    # Use palette colors for smooth gradient
                    color = 16 + min(47, pollution_level // 5)  # Colors 16-63 for pollution
                else:
                    # Fallback colors
                    if pollution_level == 0:
                        color = 3  # Green for clean
                    elif pollution_level < 64:
                        color = 11  # Light green
                    elif pollution_level < 128:
                        color = 10  # Yellow
                    elif pollution_level < 192:
                        color = 9   # Orange
                    else:
                        color = 8   # Red for high pollution
                    
            elif self.view_mode == 2:  # Land value view
                land_value = data.land_value
                if self.palette_loaded:
                    # Use palette colors for smooth gradient
                    color = 64 + min(47, land_value // 5)  # Colors 64-111 for land value
                else:
                    # Fallback colors
                    if land_value < 64:
                        color = 1   # Dark for low value
                    elif land_value < 128:
                        color = 2   # Purple
                    elif land_value < 192:
                        color = 12  # Light green
                    else:
                        color = 7   # White for high value
                    
            elif self.view_mode == 3:  # Power view
                color = 11 if data.power else 1  # Green if powered, dark if not
                
            elif self.view_mode == 4:  # Traffic view
                traffic_level = data.traffic
                if traffic_level == 0:
                    color = 1   # Dark for no traffic
                elif traffic_level < 25:
                    color = 3   # Green for light traffic
                elif traffic_level < 75:
                    color = 10  # Yellow for medium traffic
                elif traffic_level < 150:
                    color = 9   # Orange for heavy traffic
                else:
                    color = 8   # Red for congested traffic
            
            # Draw the tile
            pyxel.rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE, color)
            
            # Draw border for certain tile types
            if cell_type == CellType.WATER and self.view_mode == 0:
                pyxel.rectb(screen_x, screen_y, TILE_SIZE, TILE_SIZE, 1)
    
    def _draw_cursor(self):
        """Draw the cursor - 3x3 for buildings, 1x1 for infrastructure"""
        cursor_screen_x = self.cursor_x * TILE_SIZE - self.camera_x
        cursor_screen_y = self.cursor_y * TILE_SIZE - self.camera_y
        
        # Determine cursor size based on current tool
        if self.current_tool in [ToolMode.RESIDENTIAL, ToolMode.COMMERCIAL, ToolMode.INDUSTRIAL, ToolMode.COAL_PLANT, ToolMode.POLICE]:
            # 3x3 cursor for buildings
            cursor_width = TILE_SIZE * 3
            cursor_height = TILE_SIZE * 3
            
            # Check if 3x3 can be placed
            can_place = self._can_place_3x3_building(self.cursor_x, self.cursor_y)
            cursor_color = 11 if can_place else 8  # Green if can place, red if cannot
        else:
            # 1x1 cursor for roads, rails, etc.
            cursor_width = TILE_SIZE
            cursor_height = TILE_SIZE
            cursor_color = 7  # White
        
        # Only draw if cursor is visible
        if (cursor_screen_x < SCREEN_WIDTH and cursor_screen_y < SCREEN_HEIGHT and
            cursor_screen_x + cursor_width > 0 and cursor_screen_y + cursor_height > 0):
            pyxel.rectb(cursor_screen_x, cursor_screen_y, cursor_width, cursor_height, cursor_color)
            pyxel.rectb(cursor_screen_x + 1, cursor_screen_y + 1, cursor_width - 2, cursor_height - 2, 0)
    
    def _draw_ui(self):
        """Draw the UI overlay"""
        # Draw black background for UI area
        pyxel.rect(0, SCREEN_HEIGHT - 64, SCREEN_WIDTH, 64, 0)
        
        # Draw basic info with Japanese
        if self.font_loaded:
            self._draw_japanese_text(4, SCREEN_HEIGHT - 60, f"資金: ${self.funds}", 7)
            self._draw_japanese_text(4, SCREEN_HEIGHT - 50, f"人口: {self.population}", 7)
        else:
            pyxel.text(4, SCREEN_HEIGHT - 60, f"FUNDS: ${self.funds}", 7)
            pyxel.text(4, SCREEN_HEIGHT - 50, f"POP: {self.population}", 7)
        
        # Draw RCI demand
        if self.font_loaded:
            self._draw_japanese_text(4, SCREEN_HEIGHT - 40, f"住:{self.res_demand:+3d}", 10 if self.res_demand > 0 else 8)
            self._draw_japanese_text(44, SCREEN_HEIGHT - 40, f"商:{self.com_demand:+3d}", 10 if self.com_demand > 0 else 8)
            self._draw_japanese_text(84, SCREEN_HEIGHT - 40, f"工:{self.ind_demand:+3d}", 10 if self.ind_demand > 0 else 8)
        else:
            pyxel.text(4, SCREEN_HEIGHT - 40, "R:", 7)
            pyxel.text(16, SCREEN_HEIGHT - 40, f"{self.res_demand:+3d}", 10 if self.res_demand > 0 else 8)
            pyxel.text(44, SCREEN_HEIGHT - 40, "C:", 7)
            pyxel.text(56, SCREEN_HEIGHT - 40, f"{self.com_demand:+3d}", 10 if self.com_demand > 0 else 8)
            pyxel.text(84, SCREEN_HEIGHT - 40, "I:", 7)
            pyxel.text(96, SCREEN_HEIGHT - 40, f"{self.ind_demand:+3d}", 10 if self.ind_demand > 0 else 8)
        
        # Draw view mode
        if self.font_loaded:
            view_names = ["地図", "汚染", "地価", "電力", "交通"]
            self._draw_japanese_text(140, SCREEN_HEIGHT - 40, f"表示: {view_names[self.view_mode]}", 12)
        else:
            view_names = ["MAP", "POL", "VAL", "PWR", "TRF"]
            pyxel.text(140, SCREEN_HEIGHT - 40, f"VIEW: {view_names[self.view_mode]}", 12)
        
        # Draw current tool - now at bottom with icon preview
        if self.font_loaded:
            tool_names = {
                ToolMode.BULLDOZE: "破壊",
                ToolMode.RESIDENTIAL: "住宅地",
                ToolMode.COMMERCIAL: "商業地", 
                ToolMode.INDUSTRIAL: "工業地",
                ToolMode.ROAD: "道路",
                ToolMode.RAIL: "鉄道",
                ToolMode.WIRE: "電線",
                ToolMode.PARK: "公園",
                ToolMode.COAL_PLANT: "発電所",
                ToolMode.POLICE: "警察署"
            }
        else:
            tool_names = {
                ToolMode.BULLDOZE: "BULLDOZE",
                ToolMode.RESIDENTIAL: "RESIDENTIAL",
                ToolMode.COMMERCIAL: "COMMERCIAL", 
                ToolMode.INDUSTRIAL: "INDUSTRIAL",
                ToolMode.ROAD: "ROAD",
                ToolMode.RAIL: "RAIL",
                ToolMode.WIRE: "WIRE",
                ToolMode.PARK: "PARK",
                ToolMode.COAL_PLANT: "COAL PLANT",
                ToolMode.POLICE: "POLICE"
            }
        tool_name = tool_names.get(self.current_tool, "???")
        
        # Draw current tool name and cost
        cost = self._get_building_cost(self.current_tool)
        if self.font_loaded:
            self._draw_japanese_text(4, SCREEN_HEIGHT - 28, f"ツール: {tool_name}", 11)
            self._draw_japanese_text(4, SCREEN_HEIGHT - 18, f"コスト: ${cost}", 10)
        else:
            pyxel.text(4, SCREEN_HEIGHT - 28, f"TOOL: {tool_name}", 11)
            pyxel.text(4, SCREEN_HEIGHT - 18, f"COST: ${cost}", 10)
        
        # Draw building size indicator
        if self.font_loaded:
            if self.current_tool in [ToolMode.RESIDENTIAL, ToolMode.COMMERCIAL, ToolMode.INDUSTRIAL, ToolMode.COAL_PLANT, ToolMode.POLICE]:
                self._draw_japanese_text(4, SCREEN_HEIGHT - 8, "サイズ: 3x3", 13)
            else:
                self._draw_japanese_text(4, SCREEN_HEIGHT - 8, "サイズ: 1x1", 13)
        else:
            if self.current_tool in [ToolMode.RESIDENTIAL, ToolMode.COMMERCIAL, ToolMode.INDUSTRIAL, ToolMode.COAL_PLANT, ToolMode.POLICE]:
                pyxel.text(4, SCREEN_HEIGHT - 8, "SIZE: 3x3", 13)
            else:
                pyxel.text(4, SCREEN_HEIGHT - 8, "SIZE: 1x1", 13)
        
        # Draw a simple icon representation of current tool
        icon_x = 260
        icon_y = SCREEN_HEIGHT - 32
        tool_color = self.tile_colors.get(self._tool_to_cell_type(self.current_tool), 7)
        if self.current_tool in [ToolMode.RESIDENTIAL, ToolMode.COMMERCIAL, ToolMode.INDUSTRIAL, ToolMode.COAL_PLANT, ToolMode.POLICE]:
            # 3x3 icon
            pyxel.rect(icon_x, icon_y, 24, 24, tool_color)
            pyxel.rectb(icon_x, icon_y, 24, 24, 0)
            # Draw grid lines
            for i in range(1, 3):
                pyxel.line(icon_x + i * 8, icon_y, icon_x + i * 8, icon_y + 23, 0)
                pyxel.line(icon_x, icon_y + i * 8, icon_x + 23, icon_y + i * 8, 0)
        else:
            # 1x1 icon
            pyxel.rect(icon_x + 4, icon_y + 4, 16, 16, tool_color)
            pyxel.rectb(icon_x + 4, icon_y + 4, 16, 16, 0)

if __name__ == "__main__":
    ConcLandMini()