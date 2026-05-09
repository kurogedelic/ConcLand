import pyxel
import random
import os
from enum import IntEnum
from collections import deque
from font.bdfrenderer import BDFRenderer
from tile_system import TileManager
from voronoi_terrain import VoronoiTerrain, TerrainType

class CellType(IntEnum):
    EMPTY = 0
    RESIDENCE = 1
    COMMERCIAL = 2
    ROAD = 3
    POWERPLANT = 4
    INDUSTRIAL = 5
    AGRICULTURAL = 6
    SOLAR = 7
    WIND = 8
    NUCLEAR = 9
    GAS = 10
    SHRINE = 11
    PARK = 12
    RAILWAY = 13
    TRAIN_STATION = 14
    AIRPORT = 15
    SEAPORT = 16
    UNIVERSITY = 17
    HOSPITAL = 18
    FIRE_STATION = 19
    POLICE_STATION = 20

class ViewMode(IntEnum):
    NORMAL = 0
    POLLUTION = 1
    POWER = 2
    LAND_VALUE = 3
    TRAFFIC = 4
    HAPPINESS = 5
    DENSITY = 6

class City:
    def __init__(self):
        # まず画面を初期化（早めに実行）
        self.screen_width = 512
        self.screen_height = 342
        pyxel.init(self.screen_width, self.screen_height, title="City Sim")
        
        # Load the 256 color palette image
        if os.path.exists("assets/palette256.png"):
            pyxel.images[2].load(0, 0, "assets/palette256.png", incl_colors=True)
            print("Loaded 256-color palette")
        else:
            print("Warning: palette256.png not found")
        
        # Building sizes definition
        self.building_sizes = {
            CellType.RESIDENCE: 1,
            CellType.COMMERCIAL: 1,
            CellType.INDUSTRIAL: 1,
            CellType.ROAD: 1,
            CellType.POWERPLANT: 4,
            CellType.NUCLEAR: 4,
            CellType.GAS: 4,
            CellType.AGRICULTURAL: 3,
            CellType.SOLAR: 2,
            CellType.WIND: 1,
            CellType.PARK: 1,
            CellType.SHRINE: 1,
            CellType.RAILWAY: 1,
            CellType.TRAIN_STATION: 2,
            CellType.AIRPORT: 6,
            CellType.SEAPORT: 4,
            CellType.UNIVERSITY: 3,
            CellType.HOSPITAL: 3,
            CellType.FIRE_STATION: 2,
            CellType.POLICE_STATION: 2,
        }
        
        # Building clusters for specific building types (reduces search cost)
        self.building_clusters = {
            CellType.ROAD: set(),
            CellType.RAILWAY: set(),
            CellType.COMMERCIAL: set(),
            CellType.PARK: set(),
            CellType.SHRINE: set(),
            CellType.RESIDENCE: set(),
            CellType.INDUSTRIAL: set(),
            CellType.AGRICULTURAL: set(),
            CellType.TRAIN_STATION: set(),
            CellType.HOSPITAL: set(),
            CellType.FIRE_STATION: set(),
            CellType.POLICE_STATION: set(),
        }
        
        # UI layout constants
        self.status_height = 32
        self.palette_width = 128
        
        # Game area calculations
        self.screen_width = 512
        self.screen_height = 342
        self.cell_size = 8
        self.standard_size = 32
        
        # Calculate map dimensions based on available space
        self.game_width = self.screen_width - self.palette_width
        self.game_height = self.screen_height - self.status_height
        
        # Make the map square and larger than the viewport
        self.map_size = 64
        self.width = self.map_size
        self.height = self.map_size
        
        # Viewport size (visible area)
        self.viewport_width = self.game_width // self.cell_size
        self.viewport_height = self.game_height // self.cell_size
        
        # Camera position (top-left corner of viewport)
        self.camera_x = 0
        self.camera_y = 0
        
        self.grid = [[CellType.EMPTY for _ in range(self.width)] for _ in range(self.height)]
        self.power_grid = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.power_map = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.population_map = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.traffic_density = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.zone_density = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Cache for road distances
        self.road_distance_cache = [[float('inf') for _ in range(self.width)] for _ in range(self.height)]
        self.road_cache_dirty = True
        
        # Generate terrain using Voronoi
        self.terrain_gen = VoronoiTerrain(self.width, self.height, num_regions=15)
        self.terrain_grid = self.terrain_gen.generate_terrain()
        # Generate coastlines
        self.terrain_gen.generate_coastlines()
        
        self.pollution = [[0.0 for _ in range(self.width)] for _ in range(self.height)]
        self.land_value = [[50.0 for _ in range(self.width)] for _ in range(self.height)]
        self.crime_rate = [[0.0 for _ in range(self.width)] for _ in range(self.height)]
        self.happiness = [[50.0 for _ in range(self.width)] for _ in range(self.height)]
        
        self.total_population = 0
        self.res_population = 0
        self.com_population = 0
        self.ind_population = 0
        
        self.res_demand = 10
        self.com_demand = 10
        self.ind_demand = 10
        
        # Building counts
        self.building_counts = {cell_type: 0 for cell_type in CellType}
        
        self.time = 0
        self.time_tick = 0
        self.speed = 1
        self.paused = False
        self.selected_type = CellType.RESIDENCE
        self.view_mode = ViewMode.NORMAL
        self.hovered_tool = None
        self.frame_count = 0
        
        # Update phases for distributed processing
        self.update_phases = ['power', 'growth', 'traffic', 'other']
        self.phase_counter = 0
        self.census_rate = 4
        
        # Initialize funds
        self.city_funds = 50000
        self.god_mode = True
        
        # Public service coverage maps
        self.hospital_coverage = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.fire_coverage = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.police_coverage = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.education_coverage = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Cell costs
        self.cell_costs = {
            CellType.RESIDENCE: 1000,
            CellType.COMMERCIAL: 2000,
            CellType.INDUSTRIAL: 3000,
            CellType.ROAD: 10,
            CellType.POWERPLANT: 50000,
            CellType.AGRICULTURAL: 15000,
            CellType.SOLAR: 30000,
            CellType.WIND: 25000,
            CellType.NUCLEAR: 100000,
            CellType.GAS: 75000,
            CellType.PARK: 500,
            CellType.SHRINE: 1000,
            CellType.RAILWAY: 50,
            CellType.TRAIN_STATION: 25000,
            CellType.AIRPORT: 500000,
            CellType.SEAPORT: 200000,
            CellType.UNIVERSITY: 80000,
            CellType.HOSPITAL: 60000,
            CellType.FIRE_STATION: 40000,
            CellType.POLICE_STATION: 35000,
            CellType.EMPTY: 10,
        }
        
        # Cell maintenance costs (per time unit)
        self.cell_maintenance = {
            CellType.RESIDENCE: 5,
            CellType.COMMERCIAL: 10,
            CellType.INDUSTRIAL: 15,
            CellType.ROAD: 1,
            CellType.POWERPLANT: 100,
            CellType.AGRICULTURAL: 50,
            CellType.SOLAR: 20,
            CellType.WIND: 30,
            CellType.NUCLEAR: 200,
            CellType.GAS: 150,
            CellType.PARK: 5,
            CellType.SHRINE: 10,
            CellType.RAILWAY: 2,
            CellType.TRAIN_STATION: 150,
            CellType.AIRPORT: 2000,
            CellType.SEAPORT: 800,
            CellType.UNIVERSITY: 300,
            CellType.HOSPITAL: 250,
            CellType.FIRE_STATION: 100,
            CellType.POLICE_STATION: 80,
            CellType.EMPTY: 0,
        }
        
        # Initialize fonts
        self.use_bdf_font = self.init_fonts()
        
        # Load tile system
        self.tile_manager = TileManager()
        self.tile_manager.load_all_tiles()
        
        # Load tool icons
        self._load_tool_icons()
        
        # Mouse state
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        
        # Drag state for building placement
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.drag_direction = None  # 'horizontal', 'vertical', or None
        self.drag_last_x = 0
        self.drag_last_y = 0
        
        pyxel.run(self.update, self.draw)
    
    def _load_tool_icons(self):
        """Load tool palette icons"""
        # Load tool icons into image bank 1 (bank 2 is used for 256-color palette)
        if os.path.exists("assets/tool_icons.png"):
            pyxel.images[1].load(0, 0, "assets/tool_icons.png")
            self.tool_icons_loaded = True
        else:
            self.tool_icons_loaded = False
            print("Warning: tool_icons.png not found")
    
    def init_fonts(self):
        """Initialize BDF fonts for Japanese text"""
        # Load BDF fonts
        try:
            self.font_small = BDFRenderer("font/umplus_j10r.bdf")
            self.font_normal = BDFRenderer("font/umplus_j12r.bdf")
            # Check if font has Japanese characters
            # Current BDF files only have ASCII, so use for English labels
            self.use_bdf_font = True
            print("Loaded Japanese BDF fonts successfully")
            return True
        except:
            print("BDF fonts not found, using default Pyxel font")
            self.use_bdf_font = False
            return False
    
    
    def update(self):
        self.frame_count += 1
        
        # Update tile animations
        self.tile_manager.update_animations(self.frame_count)
        
        # Camera movement with arrow keys
        camera_speed = 1
        if pyxel.btn(pyxel.KEY_LEFT):
            self.camera_x = max(0, self.camera_x - camera_speed)
        elif pyxel.btn(pyxel.KEY_RIGHT):
            self.camera_x = min(self.width - self.viewport_width, self.camera_x + camera_speed)
        elif pyxel.btn(pyxel.KEY_UP):
            self.camera_y = max(0, self.camera_y - camera_speed)
        elif pyxel.btn(pyxel.KEY_DOWN):
            self.camera_y = min(self.height - self.viewport_height, self.camera_y + camera_speed)
        
        # Handle pause
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.paused = not self.paused
        
        # Handle speed control
        if pyxel.btnp(pyxel.KEY_1):
            self.speed = 1
        elif pyxel.btnp(pyxel.KEY_2):
            self.speed = 2
        elif pyxel.btnp(pyxel.KEY_3):
            self.speed = 4
        
        # Handle view mode switching (only Tab key now)
        if pyxel.btnp(pyxel.KEY_TAB):
            self.view_mode = ViewMode((self.view_mode + 1) % len(ViewMode))
        
        # Handle tool selection with number keys
        tool_keys = {
            pyxel.KEY_R: CellType.RESIDENCE,
            pyxel.KEY_C: CellType.COMMERCIAL,
            pyxel.KEY_I: CellType.INDUSTRIAL,
            pyxel.KEY_D: CellType.ROAD,
            pyxel.KEY_P: CellType.POWERPLANT,
            pyxel.KEY_A: CellType.AGRICULTURAL,
            pyxel.KEY_S: CellType.SOLAR,
            pyxel.KEY_W: CellType.WIND,
            pyxel.KEY_N: CellType.NUCLEAR,
            pyxel.KEY_G: CellType.GAS,
            pyxel.KEY_K: CellType.PARK,
            pyxel.KEY_J: CellType.SHRINE,
            pyxel.KEY_X: CellType.EMPTY
        }
        
        for key, tool in tool_keys.items():
            if pyxel.btnp(key):
                self.selected_type = tool
        
        # Handle tool palette interaction
        if pyxel.mouse_x >= self.game_width:
            self.handle_palette_interaction()
        
        # Handle view mode buttons
        self.handle_view_mode_buttons()
        
        # Handle building placement with drag support
        self.handle_building_placement()
        
        # Update simulation with frame skip
        if not self.paused:
            # 速度に応じてフレームスキップ
            if self.speed == 1 or self.frame_count % (5 - self.speed) == 0:
                self.simulate()
                
        # Building clusters update (less frequent)
        if self.frame_count % 120 == 0:  # 4秒ごと
            self.update_building_clusters()
            self.update_public_services()
    
    def handle_building_placement(self):
        """Handle building placement with drag support for roads and RCI zones"""
        # Only handle placement in game area
        if pyxel.mouse_x >= self.game_width or pyxel.mouse_y < self.status_height:
            return
            
        current_world_x = (pyxel.mouse_x // self.cell_size) + self.camera_x
        current_world_y = ((pyxel.mouse_y - self.status_height) // self.cell_size) + self.camera_y
        
        # Check bounds
        if not (0 <= current_world_x < self.width and 0 <= current_world_y < self.height):
            return
        
        # Mouse button pressed - start drag
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.is_dragging = True
            self.drag_start_x = current_world_x
            self.drag_start_y = current_world_y
            self.drag_last_x = current_world_x
            self.drag_last_y = current_world_y
            self.drag_direction = None
            
            # Place initial building
            if self.can_place_building(current_world_x, current_world_y, self.selected_type):
                self.place_building(current_world_x, current_world_y, self.selected_type)
        
        # Mouse button held - continue drag
        elif pyxel.btn(pyxel.MOUSE_BUTTON_LEFT) and self.is_dragging:
            # For roads and railways: only allow straight lines (horizontal or vertical)
            if self.selected_type in {CellType.ROAD, CellType.RAILWAY}:
                self.handle_road_drag(current_world_x, current_world_y)
            # For RCI zones: allow area placement
            elif self.selected_type in {CellType.RESIDENCE, CellType.COMMERCIAL, CellType.INDUSTRIAL}:
                self.handle_rci_drag(current_world_x, current_world_y)
        
        # Mouse button released - end drag
        elif not pyxel.btn(pyxel.MOUSE_BUTTON_LEFT) and self.is_dragging:
            # For RCI zones, place buildings in the dragged area
            if self.selected_type in {CellType.RESIDENCE, CellType.COMMERCIAL, CellType.INDUSTRIAL}:
                self.place_rci_area()
            
            self.is_dragging = False
            self.drag_direction = None
    
    def handle_road_drag(self, current_x, current_y):
        """Handle road/railway drag - only straight lines"""
        dx = current_x - self.drag_start_x
        dy = current_y - self.drag_start_y
        
        # Determine direction on first move
        if self.drag_direction is None and (abs(dx) > 0 or abs(dy) > 0):
            if abs(dx) > abs(dy):
                self.drag_direction = 'horizontal'
            else:
                self.drag_direction = 'vertical'
        
        # Only place roads in the determined direction
        if self.drag_direction == 'horizontal':
            target_y = self.drag_start_y
            if current_x != self.drag_last_x:
                # Draw line from last position to current
                start_x = min(self.drag_last_x, current_x)
                end_x = max(self.drag_last_x, current_x)
                for x in range(start_x, end_x + 1):
                    if self.can_place_building(x, target_y, self.selected_type):
                        self.place_building(x, target_y, self.selected_type)
                self.drag_last_x = current_x
        
        elif self.drag_direction == 'vertical':
            target_x = self.drag_start_x
            if current_y != self.drag_last_y:
                # Draw line from last position to current
                start_y = min(self.drag_last_y, current_y)
                end_y = max(self.drag_last_y, current_y)
                for y in range(start_y, end_y + 1):
                    if self.can_place_building(target_x, y, self.selected_type):
                        self.place_building(target_x, y, self.selected_type)
                self.drag_last_y = current_y
    
    def handle_rci_drag(self, current_x, current_y):
        """Handle RCI zone drag - area placement"""
        # For RCI zones, we'll place buildings in the rectangular area
        # But we only actually place them when the drag ends to avoid lag
        # For now, just update the drag position
        self.drag_last_x = current_x
        self.drag_last_y = current_y
    
    def place_rci_area(self):
        """Place RCI buildings in the dragged rectangular area"""
        min_x = min(self.drag_start_x, self.drag_last_x)
        max_x = max(self.drag_start_x, self.drag_last_x)
        min_y = min(self.drag_start_y, self.drag_last_y)
        max_y = max(self.drag_start_y, self.drag_last_y)
        
        # Place buildings in the rectangular area
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                if (0 <= x < self.width and 0 <= y < self.height and 
                    self.can_place_building(x, y, self.selected_type)):
                    self.place_building(x, y, self.selected_type)
    
    def simulate_tick(self):
        self.time_tick += 1
        
        if self.time_tick % self.census_rate == 0:
            self.take_census()
        
        # Distribute update processing across phases
        current_phase = self.update_phases[self.phase_counter % len(self.update_phases)]
        
        if current_phase == 'power':
            self.update_power_grid()
            self.cleanup_zone_data()
        elif current_phase == 'growth':
            # Only update a portion of zones each tick
            self.update_zone_growth_partial()
            self.update_rci_demand()
        elif current_phase == 'traffic':
            self.update_traffic()
            self.update_pollution_optimized()
        elif current_phase == 'other':
            self.update_land_value_optimized()
            self.update_happiness_optimized()
            self.update_special_facilities()
            self.collect_taxes()
        
        self.phase_counter += 1
    
    def update_zone_growth_partial(self):
        """Update only a portion of zones each tick to reduce lag"""
        # Process 1/4 of the map each tick
        section = self.phase_counter % 4
        start_y = (self.height // 4) * section
        end_y = (self.height // 4) * (section + 1)
        
        for y in range(start_y, min(end_y, self.height)):
            for x in range(self.width):
                cell_type = self.grid[y][x]
                
                if cell_type == CellType.RESIDENCE:
                    self.grow_residential_zone(x, y)
                elif cell_type == CellType.COMMERCIAL:
                    self.grow_commercial_zone(x, y)
                elif cell_type == CellType.INDUSTRIAL:
                    self.grow_industrial_zone(x, y)
                elif cell_type == CellType.AGRICULTURAL:
                    self.grow_agricultural_zone(x, y)
    
    def update_road_distance_cache(self):
        """Update the road distance cache using BFS"""
        if not self.road_cache_dirty:
            return
            
        # Reset cache
        self.road_distance_cache = [[float('inf') for _ in range(self.width)] for _ in range(self.height)]
        
        # BFS from all road tiles
        queue = deque()
        for (x, y) in self.building_clusters.get(CellType.ROAD, set()):
            self.road_distance_cache[y][x] = 0
            queue.append((x, y, 0))
        
        while queue:
            x, y, dist = queue.popleft()
            
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.road_distance_cache[ny][nx] > dist + 1:
                        self.road_distance_cache[ny][nx] = dist + 1
                        if dist + 1 < 10:  # Only cache up to distance 10
                            queue.append((nx, ny, dist + 1))
        
        self.road_cache_dirty = False
    
    def _get_distance_to_road_fast(self, x, y):
        """Get cached road distance"""
        if self.road_cache_dirty:
            self.update_road_distance_cache()
        return self.road_distance_cache[y][x]
    
    def count_nearby_type_fast(self, x, y, cell_type, radius):
        """Optimized nearby counting using building clusters"""
        count = 0
        buildings = self.building_clusters.get(cell_type, set())
        
        for bx, by in buildings:
            if abs(bx - x) <= radius and abs(by - y) <= radius:
                count += 1
        
        return count
    
    def update_building_clusters(self):
        """Update building position clusters for fast lookups"""
        # Clear existing clusters
        for key in self.building_clusters:
            self.building_clusters[key].clear()
        
        # Rebuild clusters
        for y in range(self.height):
            for x in range(self.width):
                cell_type = self.grid[y][x]
                if cell_type in self.building_clusters:
                    self.building_clusters[cell_type].add((x, y))
    
    def update_public_services(self):
        """Update public service coverage maps"""
        # Reset coverage maps
        self.hospital_coverage = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.fire_coverage = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.police_coverage = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.education_coverage = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Public service ranges and effects
        service_facilities = {
            CellType.HOSPITAL: {'range': 8, 'effect': 'hospital'},
            CellType.FIRE_STATION: {'range': 6, 'effect': 'fire'},
            CellType.POLICE_STATION: {'range': 6, 'effect': 'police'},
            CellType.UNIVERSITY: {'range': 10, 'effect': 'education'},
        }
        
        # Calculate coverage for each service type
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] in service_facilities:
                    service_info = service_facilities[self.grid[y][x]]
                    service_range = service_info['range']
                    effect_type = service_info['effect']
                    
                    # Apply service coverage in radius
                    for dy in range(-service_range, service_range + 1):
                        for dx in range(-service_range, service_range + 1):
                            nx, ny = x + dx, y + dy
                            if (0 <= nx < self.width and 0 <= ny < self.height):
                                distance = abs(dx) + abs(dy)  # Manhattan distance
                                if distance <= service_range:
                                    coverage_strength = max(0, 100 - (distance * 100 // service_range))
                                    
                                    if effect_type == 'hospital':
                                        self.hospital_coverage[ny][nx] = max(self.hospital_coverage[ny][nx], coverage_strength)
                                    elif effect_type == 'fire':
                                        self.fire_coverage[ny][nx] = max(self.fire_coverage[ny][nx], coverage_strength)
                                    elif effect_type == 'police':
                                        self.police_coverage[ny][nx] = max(self.police_coverage[ny][nx], coverage_strength)
                                    elif effect_type == 'education':
                                        self.education_coverage[ny][nx] = max(self.education_coverage[ny][nx], coverage_strength)
    
    def update_special_facilities(self):
        """Update effects of special large facilities"""
        # Airport effects - boosts commercial growth citywide
        airport_count = len([1 for y in range(self.height) for x in range(self.width) 
                           if self.grid[y][x] == CellType.AIRPORT])
        if airport_count > 0:
            # Airports boost commercial demand
            self.com_demand += airport_count * 5
            # Also boost land value around them
            for y in range(self.height):
                for x in range(self.width):
                    if self.grid[y][x] == CellType.AIRPORT:
                        # Boost land value in 10-tile radius
                        for dy in range(-10, 11):
                            for dx in range(-10, 11):
                                nx, ny = x + dx, y + dy
                                if (0 <= nx < self.width and 0 <= ny < self.height):
                                    distance = (dx*dx + dy*dy) ** 0.5
                                    if distance <= 10:
                                        bonus = max(0, 20 - distance * 2)
                                        self.land_value[ny][nx] = min(100, self.land_value[ny][nx] + bonus * 0.1)
        
        # Seaport effects - boosts industrial growth
        seaport_count = len([1 for y in range(self.height) for x in range(self.width) 
                           if self.grid[y][x] == CellType.SEAPORT])
        if seaport_count > 0:
            # Seaports boost industrial demand
            self.ind_demand += seaport_count * 5
            # Reduce pollution from nearby industrial (better logistics)
            for y in range(self.height):
                for x in range(self.width):
                    if self.grid[y][x] == CellType.SEAPORT:
                        # Reduce pollution in 8-tile radius
                        for dy in range(-8, 9):
                            for dx in range(-8, 9):
                                nx, ny = x + dx, y + dy
                                if (0 <= nx < self.width and 0 <= ny < self.height):
                                    distance = abs(dx) + abs(dy)
                                    if distance <= 8:
                                        pollution_reduction = max(0, 1.0 - distance * 0.125)
                                        self.pollution[ny][nx] = max(0, self.pollution[ny][nx] - pollution_reduction)
    
    def cleanup_zone_data(self):
        """Ensure zone_density and population are 0 for non-zone cells"""
        zone_types = {CellType.RESIDENCE, CellType.COMMERCIAL, CellType.INDUSTRIAL, CellType.AGRICULTURAL}
        
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] not in zone_types:
                    self.zone_density[y][x] = 0
                    self.population_map[y][x] = 0
                else:
                    if self.zone_density[y][x] > 3:
                        self.zone_density[y][x] = 3
                    if self.population_map[y][x] < 0:
                        self.population_map[y][x] = 0
    
    def update_power_grid(self):
        """Optimized power grid update - use BFS instead of distance calculation"""
        # Reset power grid
        self.power_grid = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.power_map = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Find all power sources and use BFS
        power_sources = []
        power_facilities = {
            CellType.POWERPLANT: {'range': 20, 'strength': 100},
            CellType.NUCLEAR: {'range': 30, 'strength': 150},
            CellType.GAS: {'range': 15, 'strength': 80},
            CellType.SOLAR: {'range': 10, 'strength': 50},
            CellType.WIND: {'range': 8, 'strength': 30}
        }
        
        # Collect power sources
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] in power_facilities:
                    power_info = power_facilities[self.grid[y][x]]
                    power_sources.append((x, y, power_info['range'], power_info['strength']))
        
        # BFS from each power source
        for px, py, prange, strength in power_sources:
            queue = deque([(px, py, 0)])
            visited = set()
            visited.add((px, py))
            
            while queue:
                x, y, dist = queue.popleft()
                
                if dist <= prange:
                    self.power_grid[y][x] = True
                    self.power_map[y][x] = max(self.power_map[y][x], strength * (1 - dist / prange))
                    
                    # Add neighbors only if they are roads or buildings
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            # Power can only spread through roads or buildings
                            cell_type = self.grid[ny][nx]
                            if (nx, ny) not in visited and dist + 1 <= prange:
                                # Allow power transmission through roads, railways and buildings
                                if (cell_type in {CellType.ROAD, CellType.RAILWAY} or 
                                    cell_type in {CellType.RESIDENCE, CellType.COMMERCIAL, CellType.INDUSTRIAL, 
                                                 CellType.AGRICULTURAL, CellType.PARK, CellType.SHRINE,
                                                 CellType.TRAIN_STATION, CellType.HOSPITAL, CellType.FIRE_STATION,
                                                 CellType.POLICE_STATION, CellType.UNIVERSITY, CellType.AIRPORT, CellType.SEAPORT} or
                                    cell_type in power_facilities):
                                    visited.add((nx, ny))
                                    queue.append((nx, ny, dist + 1))
    
    def take_census(self):
        self.res_population = 0
        self.com_population = 0
        self.ind_population = 0
        
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == CellType.RESIDENCE:
                    self.res_population += self.population_map[y][x]
                elif self.grid[y][x] == CellType.COMMERCIAL:
                    self.com_population += self.population_map[y][x]
                elif self.grid[y][x] == CellType.INDUSTRIAL:
                    self.ind_population += self.population_map[y][x]
        
        self.total_population = self.res_population + self.com_population + self.ind_population
    
    def grow_residential_zone(self, x, y):
        # Power check
        if not self.power_grid[y][x]:
            self.population_map[y][x] = max(0, self.population_map[y][x] - 1)
            return
        
        # Road distance check using cache
        road_distance = self._get_distance_to_road_fast(x, y)
        if road_distance > 3:
            self.population_map[y][x] = max(0, self.population_map[y][x] - 1)
            return
        
        growth_rate = 0
        
        if self.res_demand > 0:
            growth_rate += 1
        
        if self.land_value[y][x] > 60:
            growth_rate += 1
        
        if self.pollution[y][x] < 20:
            growth_rate += 1
        
        # Use fast nearby counting
        nearby_commercial = self.count_nearby_type_fast(x, y, CellType.COMMERCIAL, 3)
        if nearby_commercial > 0:
            growth_rate += 1
        
        # Public service bonuses
        if self.hospital_coverage[y][x] > 50:
            growth_rate += 1  # Health services boost growth
        if self.police_coverage[y][x] > 50:
            growth_rate += 1  # Safety boosts growth
        if self.education_coverage[y][x] > 50:
            growth_rate += 1  # Education attracts residents
        
        if random.randint(0, 10) < growth_rate:
            self.population_map[y][x] = min(self.population_map[y][x] + 1, 255)
            
            # Cellular automaton density growth
            current_density = self.zone_density[y][x]
            if current_density < 3:
                # Check if we should grow to next density level
                target_density = current_density + 1
                
                # For density 2 and 3, check if we have enough same-type neighbors
                if target_density >= 2:
                    if self._can_expand_to_density(x, y, self.grid[y][x], target_density):
                        self.zone_density[y][x] = target_density
                        self._expand_building(x, y, self.grid[y][x], target_density)
                else:
                    # Density 1 growth is always allowed
                    self.zone_density[y][x] = target_density
    
    def grow_commercial_zone(self, x, y):
        if not self.power_grid[y][x]:
            self.population_map[y][x] = max(0, self.population_map[y][x] - 1)
            return
        
        road_distance = self._get_distance_to_road_fast(x, y)
        if road_distance > 3:
            self.population_map[y][x] = max(0, self.population_map[y][x] - 1)
            return
        
        growth_rate = 0
        
        if self.com_demand > 0:
            growth_rate += 1
        
        # Use building clusters for fast counting
        nearby_residential = self.count_nearby_type_fast(x, y, CellType.RESIDENCE, 5)
        if nearby_residential > 4:
            growth_rate += 2
        
        if self.traffic_density[y][x] > 10:
            growth_rate += 1
        
        if random.randint(0, 10) < growth_rate:
            self.population_map[y][x] = min(self.population_map[y][x] + 2, 255)
            
            # Cellular automaton density growth for commercial
            current_density = self.zone_density[y][x]
            if current_density < 3:
                target_density = current_density + 1
                
                if target_density >= 2:
                    if self._can_expand_to_density(x, y, self.grid[y][x], target_density):
                        self.zone_density[y][x] = target_density
                        self._expand_building(x, y, self.grid[y][x], target_density)
                else:
                    self.zone_density[y][x] = target_density
    
    def grow_industrial_zone(self, x, y):
        if not self.power_grid[y][x]:
            self.population_map[y][x] = max(0, self.population_map[y][x] - 1)
            return
        
        road_distance = self._get_distance_to_road_fast(x, y)
        if road_distance > 3:
            self.population_map[y][x] = max(0, self.population_map[y][x] - 1)
            return
        
        growth_rate = 0
        
        if self.ind_demand > 0:
            growth_rate += 2
        
        nearby_residential = self.count_nearby_type_fast(x, y, CellType.RESIDENCE, 5)
        if nearby_residential > 2:
            growth_rate += 1
        
        if self.traffic_density[y][x] > 5:
            growth_rate += 1
        
        if random.randint(0, 10) < growth_rate:
            self.population_map[y][x] = min(self.population_map[y][x] + 2, 255)
            
            # Cellular automaton density growth for industrial
            current_density = self.zone_density[y][x]
            if current_density < 3:
                target_density = current_density + 1
                
                if target_density >= 2:
                    if self._can_expand_to_density(x, y, self.grid[y][x], target_density):
                        self.zone_density[y][x] = target_density
                        self._expand_building(x, y, self.grid[y][x], target_density)
                else:
                    self.zone_density[y][x] = target_density
    
    def grow_agricultural_zone(self, x, y):
        if not self.power_grid[y][x]:
            return
        
        growth_rate = 2
        
        road_distance = self._get_distance_to_road_fast(x, y)
        if road_distance <= 3:
            growth_rate += 1
        
        nearby_agricultural = self.count_nearby_type_fast(x, y, CellType.AGRICULTURAL, 2)
        if nearby_agricultural > 0:
            growth_rate += 1
        
        if random.randint(0, 10) < growth_rate:
            self.population_map[y][x] = min(self.population_map[y][x] + 1, 100)
            self.zone_density[y][x] = min(self.zone_density[y][x] + 1, 3)
    
    def update_traffic(self):
        """Ultra-simplified traffic update"""
        # Clear traffic density every 8th update
        if self.phase_counter % 8 == 0:
            self.traffic_density = [[0 for _ in range(self.width)] for _ in range(self.height)]
            
            # Only process 1/8 of residential zones
            residential = list(self.building_clusters.get(CellType.RESIDENCE, set()))
            if residential:
                section_size = max(1, len(residential) // 8)
                start_idx = (self.phase_counter // 8) % 8 * section_size
                end_idx = min(start_idx + section_size, len(residential))
                
                for i in range(start_idx, end_idx):
                    x, y = residential[i]
                    if self.population_map[y][x] > 0:
                        # Very simple traffic spreading
                        for dx in [-2, -1, 0, 1, 2]:
                            for dy in [-2, -1, 0, 1, 2]:
                                nx, ny = x + dx, y + dy
                                if 0 <= nx < self.width and 0 <= ny < self.height:
                                    if self.grid[ny][nx] == CellType.ROAD:
                                        distance = max(abs(dx), abs(dy)) + 1
                                        self.traffic_density[ny][nx] += self.population_map[y][x] / distance
    
    def update_pollution_optimized(self):
        """True cellular automaton pollution update with neighbor diffusion"""
        # Create a copy for double buffering
        new_pollution = [[0.0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Step 1: Decay and diffusion from neighbors
        for y in range(self.height):
            for x in range(self.width):
                current_pollution = self.pollution[y][x]
                
                # Natural decay
                new_pollution[y][x] = current_pollution * 0.95
                
                # Diffusion from neighbors (cellular automaton)
                neighbor_sum = 0
                neighbor_count = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            neighbor_sum += self.pollution[ny][nx]
                            neighbor_count += 1
                
                if neighbor_count > 0:
                    # Diffusion: 10% of average neighbor pollution flows in
                    diffusion = (neighbor_sum / neighbor_count) * 0.1
                    new_pollution[y][x] += diffusion
        
        # Step 2: Add pollution from sources
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == CellType.POWERPLANT:
                    new_pollution[y][x] = min(100.0, new_pollution[y][x] + 15.0)
                elif self.grid[y][x] == CellType.GAS:
                    new_pollution[y][x] = min(100.0, new_pollution[y][x] + 8.0)
                elif self.grid[y][x] == CellType.NUCLEAR:
                    new_pollution[y][x] = min(100.0, new_pollution[y][x] + 2.0)
                elif self.grid[y][x] == CellType.INDUSTRIAL:
                    if self.population_map[y][x] > 0:
                        pollution_amount = min(5.0, self.population_map[y][x] * 0.1)
                        new_pollution[y][x] = min(100.0, new_pollution[y][x] + pollution_amount)
        
        # Apply the new pollution state
        self.pollution = new_pollution
    
    def update_land_value_optimized(self):
        """Cellular automaton land value calculation with neighbor influence"""
        # Only update 1/4 of the map each tick to maintain performance
        section = self.phase_counter % 4
        start_y = (self.height // 4) * section
        end_y = (self.height // 4) * (section + 1)
        
        # Create temporary array for the section being updated
        for y in range(start_y, min(end_y, self.height)):
            for x in range(self.width):
                base_value = 50
                
                # Direct effects
                pollution_effect = -self.pollution[y][x] * 0.5
                power_bonus = 15 if self.power_grid[y][x] else -20
                
                # Neighbor influence (cellular automaton)
                neighbor_avg = 0
                neighbor_count = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            neighbor_avg += self.land_value[ny][nx]
                            neighbor_count += 1
                
                if neighbor_count > 0:
                    neighbor_avg /= neighbor_count
                    # 20% influence from neighbors
                    neighbor_influence = (neighbor_avg - 50) * 0.2
                else:
                    neighbor_influence = 0
                
                # Local bonuses
                commercial_bonus = self.count_nearby_type_fast(x, y, CellType.COMMERCIAL, 2) * 8
                park_bonus = self.count_nearby_type_fast(x, y, CellType.PARK, 3) * 12
                shrine_bonus = self.count_nearby_type_fast(x, y, CellType.SHRINE, 4) * 15
                
                # Distance to center bonus
                distance_to_center = abs(x - self.width // 2) + abs(y - self.height // 2)
                center_bonus = max(0, 15 - distance_to_center * 0.5)
                
                new_value = (base_value + pollution_effect + power_bonus + neighbor_influence + 
                           commercial_bonus + park_bonus + shrine_bonus + center_bonus)
                
                self.land_value[y][x] = max(0, min(100, new_value))
    
    def update_happiness_optimized(self):
        """Optimized happiness calculation"""
        # Only update residential zones
        residential = self.building_clusters.get(CellType.RESIDENCE, set())
        
        for x, y in residential:
            base_happiness = 50
            
            pollution_effect = -self.pollution[y][x] * 0.3
            land_value_effect = self.land_value[y][x] * 0.2
            power_effect = 10 if self.power_grid[y][x] else -20
            
            density_effect = 0
            if self.zone_density[y][x] > 2:
                density_effect = -10
            
            nearby_commercial = self.count_nearby_type_fast(x, y, CellType.COMMERCIAL, 3)
            service_effect = min(20, nearby_commercial * 5)
            
            nearby_parks = self.count_nearby_type_fast(x, y, CellType.PARK, 3)
            nearby_shrines = self.count_nearby_type_fast(x, y, CellType.SHRINE, 4)
            recreation_effect = min(30, nearby_parks * 10 + nearby_shrines * 15)
            
            # Public service effects on happiness
            public_service_effect = 0
            public_service_effect += self.hospital_coverage[y][x] * 0.15  # Health coverage
            public_service_effect += self.police_coverage[y][x] * 0.1   # Safety coverage
            public_service_effect += self.education_coverage[y][x] * 0.2 # Education coverage
            public_service_effect += self.fire_coverage[y][x] * 0.05    # Fire protection
            
            self.happiness[y][x] = max(0, min(100, 
                base_happiness + pollution_effect + land_value_effect + 
                power_effect + density_effect + service_effect + recreation_effect + public_service_effect))
    
    def update_rci_demand(self):
        """Simplified RCI demand calculation"""
        total_res = len(self.building_clusters.get(CellType.RESIDENCE, set()))
        total_com = len(self.building_clusters.get(CellType.COMMERCIAL, set()))
        total_ind = len(self.building_clusters.get(CellType.INDUSTRIAL, set()))
        
        self.res_demand = max(-100, min(100, 
            20 + (total_com + total_ind) * 3 - total_res * 2))
        
        self.com_demand = max(-100, min(100,
            15 + self.res_population // 50 - total_com * 5))
        
        self.ind_demand = max(-100, min(100,
            10 + self.res_population // 100 - total_ind * 3))
    
    def collect_taxes(self):
        if self.god_mode:
            return
        
        tax_rate = 0.08
        tax_revenue = int(self.total_population * tax_rate)
        
        for building_type, count in self.building_counts.items():
            maintenance = self.cell_maintenance.get(building_type, 0)
            tax_revenue -= maintenance * count
        
        self.city_funds += tax_revenue
    
    def can_afford(self, cell_type):
        if self.god_mode:
            return True
        
        cost = self.cell_costs.get(cell_type, 0)
        size = self.building_sizes.get(cell_type, 1)
        total_cost = cost * (size * size)
        
        return self.city_funds >= total_cost
    
    def spend_money(self, cell_type):
        if self.god_mode:
            return
        
        cost = self.cell_costs.get(cell_type, 0)
        size = self.building_sizes.get(cell_type, 1)
        total_cost = cost * (size * size)
        
        self.city_funds -= total_cost
    
    def place_building(self, x, y, building_type):
        """Place a building and update caches"""
        size = self.building_sizes.get(building_type, 1)
        
        # Demolish existing buildings
        if building_type == CellType.EMPTY:
            if self.grid[y][x] != CellType.EMPTY:
                self.grid[y][x] = CellType.EMPTY
                self.zone_density[y][x] = 0
                self.population_map[y][x] = 0
                self.update_building_clusters()
                if building_type == CellType.ROAD:
                    self.road_cache_dirty = True
            return
        
        # Spend money
        self.spend_money(building_type)
        
        # Handle different building sizes
        if size == 1:
            self.grid[y][x] = building_type
            if building_type in {CellType.RESIDENCE, CellType.COMMERCIAL, CellType.INDUSTRIAL}:
                self.zone_density[y][x] = 1
        else:
            # Multi-cell buildings
            for dy in range(size):
                for dx in range(size):
                    self.grid[y + dy][x + dx] = building_type
                    if building_type == CellType.AGRICULTURAL:
                        self.zone_density[y + dy][x + dx] = 1
        
        # Update building count
        self.building_counts[building_type] = self.building_counts.get(building_type, 0) + 1
        
        # Mark road cache as dirty if placing/removing roads
        if building_type == CellType.ROAD:
            self.road_cache_dirty = True
    
    def simulate(self):
        """Run simulation step"""
        self.time += 1
        
        # さらに頻度を下げる
        if self.time % 30 == 0:  # 1秒ごと
            self.simulate_tick()
    
    def can_place_building(self, x, y, building_type):
        """Check if building can be placed at position"""
        size = self.building_sizes.get(building_type, 1)
        
        # Check bounds
        if x < 0 or y < 0 or x + size > self.width or y + size > self.height:
            return False
        
        # Check if player can afford
        if not self.can_afford(building_type):
            return False
        
        # Check if area is clear
        for dy in range(size):
            for dx in range(size):
                px, py = x + dx, y + dy
                if building_type != CellType.EMPTY:
                    if self.terrain_grid[py][px] == TerrainType.WATER:
                        return False
                if self.grid[py][px] != CellType.EMPTY:
                    if building_type == CellType.ROAD and self.grid[py][px] == CellType.ROAD:
                        continue
                    # Allow roads to be built on empty RCI zones
                    if (building_type == CellType.ROAD and 
                        self.grid[py][px] in {CellType.RESIDENCE, CellType.COMMERCIAL, CellType.INDUSTRIAL} and
                        self.population_map[py][px] == 0 and self.zone_density[py][px] == 0):
                        continue
                    if building_type == CellType.EMPTY:
                        continue
                    return False
        
        return True
    
    def _can_expand_building(self, x, y, cell_type, new_density):
        """Check if building can expand to new density (cellular automaton logic)"""
        if new_density <= 1:
            return True
        
        size = new_density
        
        # Check bounds
        if x + size > self.width or y + size > self.height:
            return False
        
        # Check if ALL cells in the expansion area are the SAME zone type
        # This is the key cellular automaton rule: zones can only expand within their own zone
        for dy in range(size):
            for dx in range(size):
                px, py = x + dx, y + dy
                # All cells must be the same zone type for expansion
                if self.grid[py][px] != cell_type:
                    return False
                # Also check that they have sufficient development potential
                # (population > 0 indicates active zone)
                if self.population_map[py][px] == 0:
                    return False
        
        return True
    
    def _can_expand_to_density(self, x, y, cell_type, target_density):
        """Check if zone can expand to target density using cellular automaton rules"""
        if target_density <= 1:
            return True
        
        required_size = target_density
        
        # Check bounds
        if x + required_size > self.width or y + required_size > self.height:
            return False
        
        # Count how many cells of the required area are the same zone type and have some development
        same_type_count = 0
        total_required = required_size * required_size
        
        for dy in range(required_size):
            for dx in range(required_size):
                px, py = x + dx, y + dy
                if (self.grid[py][px] == cell_type and 
                    self.population_map[py][px] > 0):  # Must have some population/activity
                    same_type_count += 1
        
        # We need at least 75% of the area to be the same developed zone type
        required_threshold = int(total_required * 0.75)
        
        # Also check that the core (center) area is well developed
        core_density_sum = 0
        core_cells = 0
        for dy in range(min(2, required_size)):
            for dx in range(min(2, required_size)):
                px, py = x + dx, y + dy
                if self.grid[py][px] == cell_type:
                    core_density_sum += self.zone_density[py][px]
                    core_cells += 1
        
        if core_cells == 0:
            return False
        
        avg_core_density = core_density_sum / core_cells
        
        return (same_type_count >= required_threshold and 
                avg_core_density >= target_density - 1)
    
    def _expand_building(self, x, y, cell_type, new_density):
        """Expand building to new density - only within existing zones"""
        size = new_density
        
        for dy in range(size):
            for dx in range(size):
                px, py = x + dx, y + dy
                # Only expand if the cell is already the same zone type
                if self.grid[py][px] == cell_type:
                    self.zone_density[py][px] = new_density
    
    def _check_building_integrity(self, x, y, expected_type, expected_size):
        """Check if a multi-cell building is intact"""
        if expected_size == 1:
            return True
        
        for dy in range(expected_size):
            for dx in range(expected_size):
                px, py = x + dx, y + dy
                if px >= self.width or py >= self.height:
                    return False
                if self.grid[py][px] != expected_type:
                    return False
        
        return True
    
    # Drawing methods remain the same as original...
    def draw_rect_256(self, x, y, w, h, color_index):
        """Draw rectangle with 256 color index using pset"""
        for py in range(y, y + h):
            for px in range(x, x + w):
                pyxel.pset(px, py, color_index)
    
    def draw(self):
        pyxel.cls(0)
        
        # Draw status bar at top
        self.draw_status_bar()
        
        # Draw palette on right
        self.draw_palette()
        
        # Draw game area with offset
        pyxel.clip(0, self.status_height, self.game_width, self.game_height)
        
        if self.view_mode == ViewMode.NORMAL:
            self.draw_normal_view()
        elif self.view_mode == ViewMode.POLLUTION:
            self.draw_pollution_view()
        elif self.view_mode == ViewMode.POWER:
            self.draw_power_view()
        elif self.view_mode == ViewMode.LAND_VALUE:
            self.draw_land_value_view()
        elif self.view_mode == ViewMode.TRAFFIC:
            self.draw_traffic_view()
        elif self.view_mode == ViewMode.HAPPINESS:
            self.draw_happiness_view()
        elif self.view_mode == ViewMode.DENSITY:
            self.draw_density_view()
        
        # Reset clipping
        pyxel.clip()
        
        # Draw minimap
        self.draw_minimap()
        
        # Draw view mode buttons
        self.draw_view_mode_buttons()
        
        # Draw cursor overlay
        self.draw_cursor()
    
    def draw_normal_view(self):
        # Draw terrain and buildings (same as original)
        for vy in range(self.viewport_height):
            for vx in range(self.viewport_width):
                x = vx + self.camera_x
                y = vy + self.camera_y
                
                if x >= self.width or y >= self.height:
                    continue
                
                draw_x = vx * self.cell_size
                draw_y = vy * self.cell_size + self.status_height
                
                terrain = self.terrain_grid[y][x]
                # Draw terrain based on terrain grid
                terrain = self.terrain_grid[y][x]
                if terrain == TerrainType.WATER:
                    # Check if this is a coastline
                    coastline_pattern = self.terrain_gen.get_coastline_tile(x, y)
                    if coastline_pattern:
                        # This is a coastline water cell
                        north, east, south, west = coastline_pattern
                        coastline_tile_id = self.tile_manager.get_coastline_tile_id(north, east, south, west)
                        self.tile_manager.draw_tile(coastline_tile_id, draw_x, draw_y)
                    else:
                        # Regular water
                        self.tile_manager.draw_tile('terrain_water_animation', draw_x, draw_y)
                elif terrain == TerrainType.GRASS:
                    self.tile_manager.draw_tile('terrain_grass', draw_x, draw_y)
                else:  # SOIL (default)
                    self.tile_manager.draw_tile('terrain_soil', draw_x, draw_y)
        
        # Draw buildings (simplified version of original)
        for vy in range(self.viewport_height):
            for vx in range(self.viewport_width):
                x = vx + self.camera_x
                y = vy + self.camera_y
                
                if x >= self.width or y >= self.height:
                    continue
                
                cell_type = self.grid[y][x]
                if cell_type != CellType.EMPTY:
                    draw_x = vx * self.cell_size
                    draw_y = vy * self.cell_size + self.status_height
                    
                    # 道路タイルの描画
                    if cell_type == CellType.ROAD:
                        # 接続パターンをチェック
                        north = y > 0 and self.grid[y-1][x] == CellType.ROAD
                        south = y < self.height-1 and self.grid[y+1][x] == CellType.ROAD
                        east = x < self.width-1 and self.grid[y][x+1] == CellType.ROAD
                        west = x > 0 and self.grid[y][x-1] == CellType.ROAD
                        
                        road_tile_id = self.tile_manager.get_road_tile_id(north, east, south, west)
                        self.tile_manager.draw_tile(road_tile_id, draw_x, draw_y)
                    
                    # 大型建物の描画
                    elif cell_type == CellType.POWERPLANT:
                        # Power plants are 4x4 cells (32px)
                        # Only draw if this is the top-left corner of the power plant
                        is_top_left = True
                        if x > 0 and self.grid[y][x-1] == CellType.POWERPLANT:
                            is_top_left = False
                        if y > 0 and self.grid[y-1][x] == CellType.POWERPLANT:
                            is_top_left = False
                        
                        if is_top_left:
                            # Draw the power plant tile (it will be clipped if needed)
                            self.tile_manager.draw_tile('power_powerplant', draw_x, draw_y)
                    
                    elif cell_type == CellType.AGRICULTURAL:
                        # Agricultural zones are 3x3 cells
                        # Only draw if this is the top-left corner
                        is_top_left = True
                        if x > 0 and self.grid[y][x-1] == CellType.AGRICULTURAL:
                            is_top_left = False
                        if y > 0 and self.grid[y-1][x] == CellType.AGRICULTURAL:
                            is_top_left = False
                        
                        if is_top_left:
                            has_power = self.power_grid[y][x]
                            if has_power and self.population_map[y][x] > 0:
                                # Draw the 3x3 agricultural field as a single tile
                                self.tile_manager.draw_tile('agricultural_field', draw_x, draw_y)
                            else:
                                # Draw empty agricultural lot (3x3)
                                for dy in range(3):
                                    for dx in range(3):
                                        if y + dy < self.height and x + dx < self.width and vx + dx < self.viewport_width and vy + dy < self.viewport_height:
                                            self.tile_manager.draw_tile('agricultural_empty', 
                                                                      draw_x + dx * self.cell_size, 
                                                                      draw_y + dy * self.cell_size)
                    
                    elif cell_type == CellType.NUCLEAR:
                        # Nuclear plants are 4x4 cells
                        is_top_left = True
                        if x > 0 and self.grid[y][x-1] == CellType.NUCLEAR:
                            is_top_left = False
                        if y > 0 and self.grid[y-1][x] == CellType.NUCLEAR:
                            is_top_left = False
                        
                        if is_top_left:
                            # Draw the nuclear plant tile (it will be clipped if needed)
                            self.tile_manager.draw_tile('power_nuclear', draw_x, draw_y)
                    
                    elif cell_type == CellType.GAS:
                        # Gas plants are 4x4 cells
                        is_top_left = True
                        if x > 0 and self.grid[y][x-1] == CellType.GAS:
                            is_top_left = False
                        if y > 0 and self.grid[y-1][x] == CellType.GAS:
                            is_top_left = False
                        
                        if is_top_left:
                            # Draw the gas plant tile (it will be clipped if needed)
                            self.tile_manager.draw_tile('power_gas', draw_x, draw_y)
                    
                    elif cell_type == CellType.SOLAR:
                        # Solar panels are 2x2 cells
                        is_top_left = True
                        if x > 0 and self.grid[y][x-1] == CellType.SOLAR:
                            is_top_left = False
                        if y > 0 and self.grid[y-1][x] == CellType.SOLAR:
                            is_top_left = False
                        
                        if is_top_left:
                            # Check if the 2x2 building is within viewport bounds
                            if vx + 2 <= self.viewport_width and vy + 2 <= self.viewport_height:
                                self.tile_manager.draw_tile('power_solar', draw_x, draw_y)
                    
                    elif cell_type == CellType.WIND:
                        self.tile_manager.draw_tile('power_wind_animation', draw_x, draw_y)
                    
                    elif cell_type == CellType.PARK:
                        self.tile_manager.draw_tile('park_small_park', draw_x, draw_y)
                    
                    elif cell_type == CellType.SHRINE:
                        self.tile_manager.draw_tile('public_shrine', draw_x, draw_y)
                    
                    # ゾーン建物の描画
                    elif cell_type == CellType.RESIDENCE:
                        has_power = self.power_grid[y][x]
                        density = self.zone_density[y][x]
                        tile_id = self.tile_manager.get_building_tile_id('residential', density, has_power)
                        if tile_id:
                            self.tile_manager.draw_tile(tile_id, draw_x, draw_y)
                    
                    elif cell_type == CellType.COMMERCIAL:
                        has_power = self.power_grid[y][x]
                        density = self.zone_density[y][x]
                        tile_id = self.tile_manager.get_building_tile_id('commercial', density, has_power)
                        if tile_id:
                            self.tile_manager.draw_tile(tile_id, draw_x, draw_y)
                    
                    elif cell_type == CellType.INDUSTRIAL:
                        has_power = self.power_grid[y][x]
                        density = self.zone_density[y][x]
                        tile_id = self.tile_manager.get_building_tile_id('industrial', density, has_power)
                        if tile_id:
                            self.tile_manager.draw_tile(tile_id, draw_x, draw_y)
                    
                    # 鉄道システム
                    elif cell_type == CellType.RAILWAY:
                        # Railway tracks with connection patterns
                        north = y > 0 and self.grid[y-1][x] in {CellType.RAILWAY, CellType.TRAIN_STATION}
                        east = x < self.width-1 and self.grid[y][x+1] in {CellType.RAILWAY, CellType.TRAIN_STATION}
                        south = y < self.height-1 and self.grid[y+1][x] in {CellType.RAILWAY, CellType.TRAIN_STATION}
                        west = x > 0 and self.grid[y][x-1] in {CellType.RAILWAY, CellType.TRAIN_STATION}
                        
                        railway_tile_id = self.get_railway_tile_id(north, east, south, west)
                        pyxel.rect(draw_x + 2, draw_y + 3, 4, 2, 8)  # Railway tracks (temporary)
                    
                    elif cell_type == CellType.TRAIN_STATION:
                        # Train stations are 2x2 cells
                        is_top_left = True
                        if x > 0 and self.grid[y][x-1] == CellType.TRAIN_STATION:
                            is_top_left = False
                        if y > 0 and self.grid[y-1][x] == CellType.TRAIN_STATION:
                            is_top_left = False
                        
                        if is_top_left:
                            # Draw station building (temporary colored rectangle)
                            pyxel.rect(draw_x, draw_y, 16, 16, 12)
                            pyxel.rectb(draw_x, draw_y, 16, 16, 7)
                    
                    # 公共サービス施設
                    elif cell_type == CellType.HOSPITAL:
                        # Hospitals are 3x3 cells
                        is_top_left = True
                        if x > 0 and self.grid[y][x-1] == CellType.HOSPITAL:
                            is_top_left = False
                        if y > 0 and self.grid[y-1][x] == CellType.HOSPITAL:
                            is_top_left = False
                        
                        if is_top_left:
                            # Draw hospital (temporary red cross)
                            pyxel.rect(draw_x, draw_y, 24, 24, 7)
                            pyxel.rectb(draw_x, draw_y, 24, 24, 8)
                            # Red cross symbol
                            pyxel.rect(draw_x + 10, draw_y + 6, 4, 12, 8)
                            pyxel.rect(draw_x + 6, draw_y + 10, 12, 4, 8)
                    
                    elif cell_type == CellType.FIRE_STATION:
                        # Fire stations are 2x2 cells
                        is_top_left = True
                        if x > 0 and self.grid[y][x-1] == CellType.FIRE_STATION:
                            is_top_left = False
                        if y > 0 and self.grid[y-1][x] == CellType.FIRE_STATION:
                            is_top_left = False
                        
                        if is_top_left:
                            # Draw fire station (red building)
                            pyxel.rect(draw_x, draw_y, 16, 16, 8)
                            pyxel.rectb(draw_x, draw_y, 16, 16, 7)
                    
                    elif cell_type == CellType.POLICE_STATION:
                        # Police stations are 2x2 cells
                        is_top_left = True
                        if x > 0 and self.grid[y][x-1] == CellType.POLICE_STATION:
                            is_top_left = False
                        if y > 0 and self.grid[y-1][x] == CellType.POLICE_STATION:
                            is_top_left = False
                        
                        if is_top_left:
                            # Draw police station (blue building)
                            pyxel.rect(draw_x, draw_y, 16, 16, 5)
                            pyxel.rectb(draw_x, draw_y, 16, 16, 7)
                    
                    elif cell_type == CellType.UNIVERSITY:
                        # Universities are 3x3 cells
                        is_top_left = True
                        if x > 0 and self.grid[y][x-1] == CellType.UNIVERSITY:
                            is_top_left = False
                        if y > 0 and self.grid[y-1][x] == CellType.UNIVERSITY:
                            is_top_left = False
                        
                        if is_top_left:
                            # Draw university (academic building)
                            pyxel.rect(draw_x, draw_y, 24, 24, 6)
                            pyxel.rectb(draw_x, draw_y, 24, 24, 7)
                            # Simple tower/spire
                            pyxel.rect(draw_x + 10, draw_y + 2, 4, 8, 7)
                    
                    # 大型交通施設
                    elif cell_type == CellType.AIRPORT:
                        # Airports are 6x6 cells
                        is_top_left = True
                        if x > 0 and self.grid[y][x-1] == CellType.AIRPORT:
                            is_top_left = False
                        if y > 0 and self.grid[y-1][x] == CellType.AIRPORT:
                            is_top_left = False
                        
                        if is_top_left:
                            # Draw airport (large gray structure)
                            pyxel.rect(draw_x, draw_y, 48, 48, 13)
                            pyxel.rectb(draw_x, draw_y, 48, 48, 7)
                            # Runway pattern
                            pyxel.rect(draw_x + 8, draw_y + 20, 32, 8, 6)
                    
                    elif cell_type == CellType.SEAPORT:
                        # Seaports are 4x4 cells
                        is_top_left = True
                        if x > 0 and self.grid[y][x-1] == CellType.SEAPORT:
                            is_top_left = False
                        if y > 0 and self.grid[y-1][x] == CellType.SEAPORT:
                            is_top_left = False
                        
                        if is_top_left:
                            # Draw seaport (blue and brown)
                            pyxel.rect(draw_x, draw_y, 32, 32, 5)
                            pyxel.rectb(draw_x, draw_y, 32, 32, 7)
                            # Dock pattern
                            pyxel.rect(draw_x + 4, draw_y + 24, 24, 6, 4)
    
    def draw_pollution_view(self):
        for vy in range(self.viewport_height):
            for vx in range(self.viewport_width):
                x = vx + self.camera_x
                y = vy + self.camera_y
                
                if x >= self.width or y >= self.height:
                    continue
                
                draw_x = vx * self.cell_size
                draw_y = vy * self.cell_size + self.status_height
                
                pollution_level = self.pollution[y][x]
                
                if pollution_level > 0:
                    # Use red gradient colors 16-47
                    color_index = 16 + min(31, int(pollution_level / 100 * 31))
                else:
                    color_index = 0
                
                self.draw_rect_256(draw_x, draw_y, self.cell_size, self.cell_size, color_index)
    
    def draw_power_view(self):
        for vy in range(self.viewport_height):
            for vx in range(self.viewport_width):
                x = vx + self.camera_x
                y = vy + self.camera_y
                
                if x >= self.width or y >= self.height:
                    continue
                
                draw_x = vx * self.cell_size
                draw_y = vy * self.cell_size + self.status_height
                
                if self.power_grid[y][x]:
                    color = 10
                else:
                    color = 1
                
                pyxel.rect(draw_x, draw_y, self.cell_size, self.cell_size, color)
    
    def draw_land_value_view(self):
        for vy in range(self.viewport_height):
            for vx in range(self.viewport_width):
                x = vx + self.camera_x
                y = vy + self.camera_y
                
                if x >= self.width or y >= self.height:
                    continue
                
                draw_x = vx * self.cell_size
                draw_y = vy * self.cell_size + self.status_height
                
                land_val = self.land_value[y][x]
                
                if land_val > 0:
                    # Use green gradient colors 48-79
                    color_index = 48 + min(31, int(land_val / 100 * 31))
                else:
                    color_index = 0
                
                self.draw_rect_256(draw_x, draw_y, self.cell_size, self.cell_size, color_index)
    
    def draw_traffic_view(self):
        for vy in range(self.viewport_height):
            for vx in range(self.viewport_width):
                x = vx + self.camera_x
                y = vy + self.camera_y
                
                if x >= self.width or y >= self.height:
                    continue
                
                draw_x = vx * self.cell_size
                draw_y = vy * self.cell_size + self.status_height
                
                traffic_level = self.traffic_density[y][x]
                
                if self.grid[y][x] == CellType.ROAD and traffic_level > 0:
                    # Use traffic gradient colors 80-111
                    color_index = 80 + min(31, int(traffic_level / 240 * 31))
                    self.draw_rect_256(draw_x, draw_y, self.cell_size, self.cell_size, color_index)
    
    def draw_happiness_view(self):
        for vy in range(self.viewport_height):
            for vx in range(self.viewport_width):
                x = vx + self.camera_x
                y = vy + self.camera_y
                
                if x >= self.width or y >= self.height:
                    continue
                
                draw_x = vx * self.cell_size
                draw_y = vy * self.cell_size + self.status_height
                
                happiness_level = self.happiness[y][x]
                
                if self.grid[y][x] == CellType.RESIDENCE and happiness_level > 0:
                    # Use purple gradient colors 192-207 for happiness
                    color_index = 192 + min(15, int(happiness_level / 100 * 15))
                    self.draw_rect_256(draw_x, draw_y, self.cell_size, self.cell_size, color_index)
    
    def draw_density_view(self):
        for vy in range(self.viewport_height):
            for vx in range(self.viewport_width):
                x = vx + self.camera_x
                y = vy + self.camera_y
                
                if x >= self.width or y >= self.height:
                    continue
                
                draw_x = vx * self.cell_size
                draw_y = vy * self.cell_size + self.status_height
                
                pop = self.population_map[y][x]
                
                if pop > 0:
                    # Map population (0-255) to color indices 240-254
                    color_index = 240 + min(14, int(pop / 255 * 14))
                    self.draw_rect_256(draw_x, draw_y, self.cell_size, self.cell_size, color_index)
    
    def draw_status_bar(self):
        pyxel.rect(0, 0, self.screen_width, self.status_height, 1)
        pyxel.rectb(0, 0, self.screen_width, self.status_height, 7)
        
        if self.use_bdf_font:
            funds_text = "∞" if self.god_mode else f"{self.city_funds:,}"
            status_text = f"人口:{self.total_population:,}人 資金:{funds_text}円"
            self.font_small.draw_text(4, 4, status_text, 7)
            
            demand_text = f"需要 住:{int(self.res_demand//10):+3d} 商:{int(self.com_demand//10):+3d} 工:{int(self.ind_demand//10):+3d}"
            self.font_small.draw_text(200, 4, demand_text, 7)
            
            mode_text = f"表示:{self.get_mode_name_jp()}"
            self.font_small.draw_text(320, 4, mode_text, 11)
            
            tool_text = f"ツール:{self.get_tool_name_jp_by_type(self.selected_type)}"
            self.font_small.draw_text(320, 14, tool_text, 11)
            
            if self.paused:
                self.font_small.draw_text(200, 14, "一時停止", 8)
            else:
                self.font_small.draw_text(200, 14, f"速度: {self.speed}x", 11)
        else:
            funds_text = "INF" if self.god_mode else f"${self.city_funds:,}"
            pyxel.text(4, 4, f"Pop:{self.total_population:,} {funds_text}", 7)
            pyxel.text(4, 12, f"RCI:{self.res_demand//10:+2d}/{self.com_demand//10:+2d}/{self.ind_demand//10:+2d}", 7)
            pyxel.text(100, 4, f"View:{self.view_mode.name}", 11)
            pyxel.text(100, 12, f"Tool:{self.selected_type.name}", 11)
            
            if self.paused:
                pyxel.text(200, 4, "PAUSED", 8)
            else:
                pyxel.text(200, 4, f"Speed: {self.speed}x", 11)
    
    def draw_minimap(self):
        minimap_scale = 2
        minimap_width = self.width // minimap_scale
        minimap_height = self.height // minimap_scale
        # Position minimap at the bottom of the tool palette area
        minimap_x = self.game_width + 4
        minimap_y = self.screen_height - minimap_height - 8
        
        pyxel.rect(minimap_x - 1, minimap_y - 1, 
                  minimap_width + 2, minimap_height + 2, 0)
        
        for my in range(minimap_height):
            for mx in range(minimap_width):
                real_x = mx * minimap_scale
                real_y = my * minimap_scale
                
                terrain = self.terrain_grid[real_y][real_x]
                cell = self.grid[real_y][real_x]
                
                if cell != CellType.EMPTY:
                    if cell == CellType.RESIDENCE:
                        color = 11
                    elif cell == CellType.COMMERCIAL:
                        color = 12
                    elif cell == CellType.INDUSTRIAL:
                        color = 10
                    elif cell == CellType.ROAD:
                        color = 5
                    elif cell in [CellType.POWERPLANT, CellType.NUCLEAR, CellType.GAS]:
                        color = 8
                    elif cell in [CellType.SOLAR, CellType.WIND]:
                        color = 14
                    elif cell == CellType.AGRICULTURAL:
                        color = 11
                    elif cell == CellType.PARK:
                        color = 3
                    elif cell == CellType.SHRINE:
                        color = 9
                    else:
                        color = 7
                else:
                    if terrain == TerrainType.WATER:
                        color = 5
                    elif terrain == TerrainType.GRASS:
                        color = 11
                    else:
                        color = 4
                
                pyxel.pset(minimap_x + mx, minimap_y + my, color)
        
        vp_x = minimap_x + (self.camera_x // minimap_scale)
        vp_y = minimap_y + (self.camera_y // minimap_scale)
        vp_w = self.viewport_width // minimap_scale
        vp_h = self.viewport_height // minimap_scale
        
        for i in range(vp_w):
            if i % 2 == 0:
                pyxel.pset(vp_x + i, vp_y, 7)
                pyxel.pset(vp_x + i, vp_y + vp_h - 1, 7)
        for i in range(vp_h):
            if i % 2 == 0:
                pyxel.pset(vp_x, vp_y + i, 7)
                pyxel.pset(vp_x + vp_w - 1, vp_y + i, 7)
    
    def draw_palette(self):
        pyxel.rect(self.game_width, self.status_height, self.palette_width, self.game_height, 2)
        pyxel.rectb(self.game_width, self.status_height, self.palette_width, self.game_height, 7)
        
        title_y = self.status_height + 8
        if self.hovered_tool is not None:
            if self.use_bdf_font:
                tool_name = self.get_tool_name_jp_by_type(self.hovered_tool)
                self.font_small.draw_text(self.game_width + 8, title_y, tool_name, 11)
            else:
                pyxel.text(self.game_width + 8, title_y, self.hovered_tool.name, 11)
        else:
            if self.use_bdf_font:
                self.font_small.draw_text(self.game_width + 8, title_y, "ツール", 6)
            else:
                pyxel.text(self.game_width + 8, title_y, "TOOLS", 6)
        
        icon_size = 12  # Half size: 24 -> 12
        button_size = 16  # Smaller buttons to match: 28 -> 16
        margin = 6  # Reduced margin for 3 columns
        cols = 3
        x_start = self.game_width + margin
        y_start = self.status_height + margin + 24
        
        tools = [
            CellType.RESIDENCE, CellType.COMMERCIAL,
            CellType.INDUSTRIAL, CellType.ROAD,
            CellType.RAILWAY, CellType.TRAIN_STATION,
            CellType.POWERPLANT, CellType.AGRICULTURAL,
            CellType.SOLAR, CellType.WIND,
            CellType.NUCLEAR, CellType.GAS,
            CellType.HOSPITAL, CellType.FIRE_STATION,
            CellType.POLICE_STATION, CellType.UNIVERSITY,
            CellType.AIRPORT, CellType.SEAPORT,
            CellType.PARK, CellType.SHRINE,
            CellType.EMPTY
        ]
        
        for i, tool_type in enumerate(tools):
            row = i // cols
            col = i % cols
            x = x_start + col * (button_size + margin)
            y = y_start + row * (button_size + margin)
            
            if self.selected_type == tool_type:
                pyxel.rect(x - 1, y - 1, button_size + 2, button_size + 2, 11)
            elif self.hovered_tool == tool_type:
                pyxel.rect(x - 1, y - 1, button_size + 2, button_size + 2, 13)
            
            pyxel.rect(x, y, button_size, button_size, 1)
            
            if self.tool_icons_loaded:
                # Use the index in the tools array, not CellType enum order
                tool_index = i  # i is already the correct index in the tools array
                icon_x = (tool_index % 8) * icon_size
                icon_y = (tool_index // 8) * icon_size
                draw_x = x + (button_size - icon_size) // 2
                draw_y = y + (button_size - icon_size) // 2
                pyxel.blt(draw_x, draw_y, 1, icon_x, icon_y, icon_size, icon_size, 0)
            else:
                pyxel.rect(x + 2, y + 2, button_size - 4, button_size - 4, 7)
        
        tool_rows = (len(tools) + cols - 1) // cols
        y_modes = y_start + tool_rows * (button_size + margin) + 16
        if self.use_bdf_font:
            self.font_small.draw_text(x_start, y_modes, "表示切替[M]", 6)
            self.font_small.draw_text(x_start, y_modes + 10, "一時停止[SPACE]", 6)
            self.font_small.draw_text(x_start, y_modes + 20, "速度[1-3]", 6)
        else:
            pyxel.text(x_start, y_modes, "Mode[M]", 6)
            pyxel.text(x_start, y_modes + 10, "Pause[SPACE]", 6)
            pyxel.text(x_start, y_modes + 20, "Speed[1-3]", 6)
    
    def draw_cursor(self):
        if pyxel.mouse_x < self.game_width and pyxel.mouse_y >= self.status_height:
            world_x = (pyxel.mouse_x // self.cell_size) + self.camera_x
            world_y = ((pyxel.mouse_y - self.status_height) // self.cell_size) + self.camera_y
            
            if 0 <= world_x < self.width and 0 <= world_y < self.height:
                # Draw drag area for RCI zones
                if (self.is_dragging and 
                    self.selected_type in {CellType.RESIDENCE, CellType.COMMERCIAL, CellType.INDUSTRIAL}):
                    self.draw_drag_area(world_x, world_y)
                else:
                    # Normal cursor for single building
                    size = self.building_sizes.get(self.selected_type, 1)
                    
                    screen_x = (world_x - self.camera_x) * self.cell_size
                    screen_y = (world_y - self.camera_y) * self.cell_size + self.status_height
                    
                    if self.can_place_building(world_x, world_y, self.selected_type):
                        color = 11
                    else:
                        color = 8
                    
                    pyxel.rectb(screen_x, screen_y, 
                               size * self.cell_size, size * self.cell_size, color)
                    
                    for dy in range(size):
                        for dx in range(size):
                            if (dx + dy) % 2 == 0:
                                pyxel.rect(screen_x + dx * self.cell_size, 
                                         screen_y + dy * self.cell_size,
                                         self.cell_size, self.cell_size, color)
        
        pyxel.mouse(True)
    
    def draw_drag_area(self, current_world_x, current_world_y):
        """Draw the dragged area for RCI zone placement"""
        min_x = min(self.drag_start_x, current_world_x)
        max_x = max(self.drag_start_x, current_world_x)
        min_y = min(self.drag_start_y, current_world_y)
        max_y = max(self.drag_start_y, current_world_y)
        
        # Draw outline of the dragged area
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                if (0 <= x < self.width and 0 <= y < self.height and
                    min(x - self.camera_x, self.viewport_width - 1) >= 0 and
                    min(y - self.camera_y, self.viewport_height - 1) >= 0):
                    
                    screen_x = (x - self.camera_x) * self.cell_size
                    screen_y = (y - self.camera_y) * self.cell_size + self.status_height
                    
                    # Check if current cell can be placed
                    if self.can_place_building(x, y, self.selected_type):
                        color = 11  # Green for valid
                    else:
                        color = 8   # Red for invalid
                    
                    # Draw outline for border cells
                    is_border = (x == min_x or x == max_x or y == min_y or y == max_y)
                    if is_border:
                        pyxel.rectb(screen_x, screen_y, self.cell_size, self.cell_size, color)
                    else:
                        # Fill inner cells with transparent pattern
                        if (x + y) % 2 == 0:
                            pyxel.rect(screen_x, screen_y, self.cell_size, self.cell_size, color)
    
    def draw_view_mode_buttons(self):
        """Draw view mode buttons on the left side"""
        button_width = 60
        button_height = 16
        margin = 4
        start_x = 8
        start_y = self.screen_height - (len(ViewMode) * (button_height + margin)) - 8
        
        view_mode_names = {
            ViewMode.NORMAL: "通常",
            ViewMode.POLLUTION: "汚染",
            ViewMode.POWER: "電力",
            ViewMode.LAND_VALUE: "地価",
            ViewMode.TRAFFIC: "交通",
            ViewMode.HAPPINESS: "幸福",
            ViewMode.DENSITY: "密度"
        }
        
        for i, mode in enumerate(ViewMode):
            button_x = start_x
            button_y = start_y + i * (button_height + margin)
            
            # Button background
            if self.view_mode == mode:
                button_color = 11  # Selected - bright green
            else:
                button_color = 5   # Normal - dark blue
            
            pyxel.rect(button_x, button_y, button_width, button_height, button_color)
            pyxel.rectb(button_x, button_y, button_width, button_height, 7)
            
            # Button text
            text = view_mode_names.get(mode, f"Mode{mode}")
            text_x = button_x + 4
            text_y = button_y + 4
            
            if self.use_bdf_font:
                self.font_small.draw_text(text_x, text_y, text, 7)
            else:
                pyxel.text(text_x, text_y, text, 7)
    
    def handle_view_mode_buttons(self):
        """Handle clicks on view mode buttons"""
        if not pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            return
            
        button_width = 60
        button_height = 16
        margin = 4
        start_x = 8
        start_y = self.screen_height - (len(ViewMode) * (button_height + margin)) - 8
        
        for i, mode in enumerate(ViewMode):
            button_x = start_x
            button_y = start_y + i * (button_height + margin)
            
            if (button_x <= pyxel.mouse_x < button_x + button_width and
                button_y <= pyxel.mouse_y < button_y + button_height):
                self.view_mode = mode
                break
    
    def handle_palette_interaction(self):
        tools = [
            CellType.RESIDENCE, CellType.COMMERCIAL,
            CellType.INDUSTRIAL, CellType.ROAD,
            CellType.RAILWAY, CellType.TRAIN_STATION,
            CellType.POWERPLANT, CellType.AGRICULTURAL,
            CellType.SOLAR, CellType.WIND,
            CellType.NUCLEAR, CellType.GAS,
            CellType.HOSPITAL, CellType.FIRE_STATION,
            CellType.POLICE_STATION, CellType.UNIVERSITY,
            CellType.AIRPORT, CellType.SEAPORT,
            CellType.PARK, CellType.SHRINE,
            CellType.EMPTY
        ]
        
        icon_size = 12  # Half size: 24 -> 12
        button_size = 16  # Smaller buttons to match: 28 -> 16
        margin = 6  # Reduced margin for 3 columns
        cols = 3
        x_start = self.game_width + margin
        y_start = self.status_height + margin + 24
        
        self.hovered_tool = None
        
        for i, tool_type in enumerate(tools):
            row = i // cols
            col = i % cols
            x = x_start + col * (button_size + margin)
            y = y_start + row * (button_size + margin)
            
            if (x <= pyxel.mouse_x < x + button_size and 
                y <= pyxel.mouse_y < y + button_size):
                self.hovered_tool = tool_type
                if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                    self.selected_type = tool_type
                break
    
    def get_tool_name_jp_by_type(self, cell_type):
        names = {
            CellType.EMPTY: "削除",
            CellType.RESIDENCE: "住宅",
            CellType.COMMERCIAL: "商業",
            CellType.INDUSTRIAL: "工業", 
            CellType.ROAD: "道路",
            CellType.RAILWAY: "鉄道",
            CellType.TRAIN_STATION: "駅",
            CellType.POWERPLANT: "発電所",
            CellType.AGRICULTURAL: "農業",
            CellType.SOLAR: "太陽光",
            CellType.WIND: "風力",
            CellType.NUCLEAR: "原子力",
            CellType.GAS: "ガス",
            CellType.HOSPITAL: "病院",
            CellType.FIRE_STATION: "消防署",
            CellType.POLICE_STATION: "警察署",
            CellType.UNIVERSITY: "大学",
            CellType.AIRPORT: "空港",
            CellType.SEAPORT: "港",
            CellType.PARK: "公園",
            CellType.SHRINE: "神社"
        }
        return names.get(cell_type, "不明")
    
    def get_railway_tile_id(self, north=False, east=False, south=False, west=False):
        """Get railway tile ID based on connections (similar to road system)"""
        patterns = {
            (False, False, False, False): 'railway_alone',
            (False, True, False, True): 'railway_horizontal',
            (True, False, True, False): 'railway_vertical',
            (False, True, True, False): 'railway_corner_ne',
            (False, False, True, True): 'railway_corner_se',
            (True, False, False, True): 'railway_corner_sw',
            (True, True, False, False): 'railway_corner_nw',
            (True, True, True, False): 'railway_t_east',
            (True, False, True, True): 'railway_t_west',
            (False, True, True, True): 'railway_t_south',
            (True, True, False, True): 'railway_t_north',
            (True, True, True, True): 'railway_cross',
        }
        return patterns.get((north, east, south, west), 'railway_alone')
    
    def get_mode_name_jp(self):
        names = {
            ViewMode.NORMAL: "通常",
            ViewMode.POLLUTION: "汚染",
            ViewMode.POWER: "電力",
            ViewMode.LAND_VALUE: "地価",
            ViewMode.TRAFFIC: "交通",
            ViewMode.HAPPINESS: "幸福度",
            ViewMode.DENSITY: "人口密度"
        }
        return names.get(self.view_mode, "不明")

if __name__ == "__main__":
    city = City()