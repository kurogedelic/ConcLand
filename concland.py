#!/usr/bin/env python3
"""
ConcLand - Minimal City Simulation Game
Based on original SimCity (1989) mechanics
Game Boy resolution: 160x144

主要機能 / Main Features:
- 100x100タイルマップで都市建設
- RCI（住宅/商業/工業）ゾーニングシステム
- セルオートマトン方式の汚染・地価シミュレーション
- 電力・水道インフラ管理
- リアルタイムシミュレーション（60 FPS）
"""

# ========================================
# 基本ライブラリのインポート
# Core library imports
# ========================================
import pyxel  # ゲームエンジン / Game engine
import random  # ランダム要素用 / For random elements
import sys  # システム操作 / System operations
import os  # ファイルシステム操作 / File system operations
import json  # 設定ファイル読み書き / Config file I/O
import pickle  # セーブデータのシリアライズ / Save data serialization
from enum import Enum  # 列挙型定義 / Enumeration definitions
from dataclasses import dataclass, asdict  # データ構造定義 / Data structure definitions
from typing import List, Tuple, Optional  # 型ヒント / Type hints

# ========================================
# カスタムモジュールのインポート
# Custom module imports
# ========================================
from image_tile_system import ImageTileSystem  # タイル描画システム / Tile rendering system
from terrain_generator import VoronoiTerrainGenerator, TerrainType  # 地形生成 / Terrain generation
from diagonal_coastline_system import DiagonalCoastlineSystem  # 海岸線処理 / Coastline processing
from train_system import TrainSystem, Train, TrainDirection  # 鉄道システム / Railway system

# ========================================
# PYTHONPATH設定（高度システム用）
# PYTHONPATH setup for advanced systems
# ========================================
# miscシステム用のパス設定（economic_systemが依存）
sys.path.append(os.path.join(os.path.dirname(__file__), 'misc'))

# ========================================
# 高度システムのインポート（統合準備）
# Advanced system imports (integration ready)
# ========================================
# 注意：これらのシステムは統合作業中のため、一時的にコメントアウト
# Note: These systems are temporarily commented out during integration
from traffic_system import AdvancedTrafficSystem  # Traffic system integrated
from economic_system import ConcLandEconomicSystem  # Economic system integrated
from disaster_system import DisasterSystem  # Disaster system integrated
from advanced_ui import AdvancedUI, UIPanel  # UI system integrated
from title_menu_system import GameLauncher

# ========================================
# フォントサポート設定
# Font support configuration
# ========================================
# 日本語フォント（BDF形式）を複数のパスから検索
# Search for Japanese fonts (BDF format) from multiple paths
font_paths = [
    os.path.join(os.path.dirname(__file__), 'assets'),  # assetsフォルダ
    os.path.dirname(__file__)  # プロジェクトルート
]
for path in font_paths:
    sys.path.append(path)

# 日本語フォントレンダラーのインポート試行
# Attempt to import Japanese font renderer
try:
    from font.bdfrenderer import BDFRenderer
    FONT_AVAILABLE = True
except ImportError:
    try:
        # フォールバック: プロジェクトルートから試行
        # Fallback: try from project root
        from bdfrenderer_fixed import BDFRenderer
        FONT_AVAILABLE = True
    except ImportError:
        FONT_AVAILABLE = False
        print("Warning: Japanese font not available")

# ========================================
# 画面・マップ設定
# Screen and map configuration
# ========================================
# 8x8タイル用に最適化された設定
# Settings optimized for 8x8 tiles
SCREEN_WIDTH = 320  # 画面幅（ピクセル） / Screen width (pixels)
SCREEN_HEIGHT = 288  # 画面高さ（ピクセル） / Screen height (pixels)
WINDOW_SCALE = 1  # ウィンドウスケール / Window scale
MAP_SIZE = 100  # マップサイズ: 100x100タイル = 800x800ワールド / Map size: 100x100 tiles = 800x800 world
TILE_SIZE = 8  # タイルサイズ（PNGタイルサイズと一致） / Tile size (matches PNG tile size)

class CellType(Enum):
    """
    セルタイプの定義
    Cell type definitions
    
    各セルが持つことができる建物・地形のタイプを定義
    Defines the types of buildings and terrain that each cell can have
    """
    # ========================================
    # 基本ゾーン / Basic zones
    # ========================================
    EMPTY = 0  # 空地 / Empty land
    RESIDENTIAL = 1  # 住宅ゾーン / Residential zone
    COMMERCIAL = 2  # 商業ゾーン / Commercial zone
    INDUSTRIAL = 3  # 工業ゾーン / Industrial zone
    ROAD = 4
    RAIL = 5
    WIRE = 6
    PARK = 7
    WATER = 8
    COAL_PLANT = 9
    OIL_PLANT = 10
    NUCLEAR_PLANT = 11
    GAS_PLANT = 12
    WIND_PLANT = 13
    POLICE = 14
    FIRE = 15
    HOSPITAL = 16
    SCHOOL = 17
    UNIVERSITY = 18
    PARK_MIDDLE = 19
    SEWAGE_PLANT = 20
    WATER_PLANT = 21
    PUMP = 22
    WASTELAND = 23  # Bulldozed land
    AGRICULTURAL = 24  # Agricultural zone (farms)
    # New public facilities
    LIBRARY = 25
    LABORATORY = 26
    MILITARY = 27
    PRISON = 28
    SHRINE = 29
    SPACE = 30
    # Port facilities
    AIRPORT = 31
    HELIPORT = 32
    SEAPORT = 33
    # Additional power
    SOLAR_PLANT = 34
    # Waste management
    INCINERATOR = 35
    WASTE_FACILITY = 36
    # Special
    ONSEN = 37
    PACHINKO = 38
    STATION = 39  # Train station

class ItemMode(Enum):
    BULLDOZE = 0
    RESIDENTIAL = 1
    COMMERCIAL = 2
    INDUSTRIAL = 3
    ROAD = 4
    RAIL = 5
    WIRE = 6
    PARK = 7
    COAL_PLANT = 8
    NUCLEAR_PLANT = 9
    GAS_PLANT = 10
    WIND_PLANT = 11
    POLICE = 12
    FIRE = 13
    HOSPITAL = 14
    SCHOOL = 15
    UNIVERSITY = 16
    PARK_MIDDLE = 17
    SEWAGE_PLANT = 18
    WATER_PLANT = 19
    PUMP = 20
    AGRICULTURAL = 21
    # New public facilities
    LIBRARY = 22
    LABORATORY = 23
    MILITARY = 24
    PRISON = 25
    SHRINE = 26
    SPACE = 27
    STATION = 28  # Train station
    # Port facilities
    AIRPORT = 29
    HELIPORT = 30
    SEAPORT = 31
    # Additional power
    SOLAR_PLANT = 32
    OIL_PLANT = 33
    # Waste management
    INCINERATOR = 34
    WASTE_FACILITY = 35
    # Special
    ONSEN = 36
    PACHINKO = 37

@dataclass
class SimData:
    """Simulation data for each cell"""
    population: int = 0
    pollution: int = 0
    land_value: int = 128  # 0-255
    power: bool = False
    water: bool = False  # Water supply status
    water_pollution: int = 0  # Water pollution level 0-255
    traffic: int = 0
    density: int = 0  # Building density 0-4 for RCI zones (0 = empty/undeveloped)
    building_variant: int = 0  # Building variation (0-2 for low density buildings)
    under_construction: int = 0  # Construction timer (counts down to 0)
    building_id: int = 0  # For tracking 3x3 buildings
    crime: int = 0  # Crime level 0-100
    fire_risk: int = 0  # Fire risk 0-100
    original_terrain: Optional['CellType'] = None  # For bridges
    has_road: bool = False  # For road/rail overlap
    has_rail: bool = False  # For road/rail overlap
    has_wire: bool = False  # For wire overlay on roads/rails
    merged_size: int = 1  # Size of merged building (1, 2, or 3 for 1x1, 2x2, 3x3)
    merged_top_left: Optional[Tuple[int, int]] = None  # Top-left corner of merged building

class ConcLandMini:
    def __init__(self, skip_pyxel_init=False):
        # Initialize Pyxel with doubled resolution
        # Initialize Pyxel (256-color palette will be loaded by tile system)
        # Skip initialization if already done by GameLauncher
        if not skip_pyxel_init:
            pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="ConcLand", fps=60)
        
        # Development mode flags
        self.dev_mode = True  # Development flag
        self.infinite_funds = True  # Infinite funds in dev mode
        self.always_show_minimap = True  # Always show minimap (can be toggled with M key)
        
        # Game state
        self.running = True
        self.camera_x = 0
        self.camera_y = 0
        self.cursor_x = 8  # Start at center
        self.cursor_y = 8
        self.current_item = ItemMode.RESIDENTIAL
        self.funds = 10000 if not self.infinite_funds else 999999
        self.simulation_tick = 0
        self.next_building_id = 1  # For tracking 3x3 buildings
        
        # Item cycling groups for key shortcuts
        self.item_cycles = {
            'power': [ItemMode.COAL_PLANT, ItemMode.NUCLEAR_PLANT, ItemMode.GAS_PLANT, 
                     ItemMode.WIND_PLANT, ItemMode.SOLAR_PLANT, ItemMode.OIL_PLANT],
            'public': [ItemMode.POLICE, ItemMode.FIRE, ItemMode.HOSPITAL, ItemMode.SCHOOL,
                      ItemMode.UNIVERSITY, ItemMode.LIBRARY, ItemMode.LABORATORY,
                      ItemMode.INCINERATOR, ItemMode.WASTE_FACILITY],
            'special': [ItemMode.MILITARY, ItemMode.PRISON, ItemMode.SHRINE, ItemMode.SPACE,
                       ItemMode.ONSEN, ItemMode.PACHINKO],
            'port': [ItemMode.AIRPORT, ItemMode.HELIPORT, ItemMode.SEAPORT],
            'park': [ItemMode.PARK, ItemMode.PARK_MIDDLE],
            'water': [ItemMode.WATER_PLANT, ItemMode.SEWAGE_PLANT, ItemMode.PUMP],
            'rail': [ItemMode.RAIL, ItemMode.STATION]  # Rail and station cycle
        }
        self.cycle_indices = {key: 0 for key in self.item_cycles.keys()}
        
        # Maps
        self.grid = [[CellType.EMPTY for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
        self.sim_data = [[SimData() for _ in range(MAP_SIZE)] for _ in range(MAP_SIZE)]
        
        # RCIA Demand (-100 to 100)
        self.res_demand = 50
        self.com_demand = 30
        self.ind_demand = 20
        self.agr_demand = 40  # Agricultural demand
        
        # Economic factors
        self.tax_rate = 7  # Tax rate 0-20%
        self.total_population = 0
        self.employment_rate = 0.0
        self.gdp = 0
        
        # Quality of Life metrics (0-100)
        self.living_standard = 50  # Based on wealth and services
        self.education_level = 30  # Based on schools and universities
        self.safety_level = 40     # Based on police and fire coverage
        
        # Date/Time
        self.year = 2025
        self.month = 1
        self.day = 1
        
        # View mode
        self.view_mode = 0  # 0=normal, 1=pollution, 2=land_value, 3=power
        
        # Coastline mapping
        self.coastline_map = {}  # Store coastline tile mapping
        
        # Input state
        self.key_repeat_timer = 0
        self.key_repeat_delay = 5  # Moderate cursor speed
        
        # Item palette state
        self.palette_mode = False  # True when cursor is in palette
        self.palette_cursor = 0  # Current item selection in palette (2D grid index)
        self.just_selected_item = False  # Flag to prevent immediate placement after selection
        
        # Confirmation dialogs for save/load
        self.save_confirm = False  # First press of save key
        self.load_confirm = False  # First press of load key
        self.confirm_timer = 0  # Timer for confirmation timeout
        
        # UI Messages
        self.show_message = ""
        self.message_timer = 0
        
        # Minimap display state
        self.is_moving = False  # Flag to show minimap when camera moves
        self.move_timer = 0  # Timer to keep minimap visible briefly after movement stops
        self.prev_camera_x = 0  # To detect camera movement
        self.prev_camera_y = 0
        
        # Balance graph display state
        self.show_balance_graph = True  # Show balance graph by default

        # ========================================
        # 簡素化されたヘルプシステム
        # Simplified help system
        # ========================================
        self.help_visible = False  # ヘルプ表示フラグ / Help visibility flag
        self.help_timer = 0  # ヘルプ自動消去タイマー / Help auto-hide timer
        self.show_startup_help = True  # 起動時ヘルプ表示フラグ / Show help on startup

        # ========================================
        # 高度システムの初期化（統合準備）
        # Advanced systems initialization (integration ready)
        # ========================================
        # 注意：これらのシステムは統合作業中のため、一時的にコメントアウト
        # Note: These systems are temporarily commented out during integration
        self.traffic_system = AdvancedTrafficSystem(MAP_SIZE)  # Traffic system integrated
        self.economic_system = ConcLandEconomicSystem()  # Economic system integrated
        self.disaster_system = DisasterSystem(MAP_SIZE)  # Disaster system integrated
        self.ui_system = AdvancedUI(SCREEN_WIDTH, SCREEN_HEIGHT)  # UI system integrated
        self.ui_data_needs_update = False  # Flag for UI update optimization

        # Initialize game world
        self._init_world()

        # Sync existing economic variables with economic_system
        self._sync_economic_data_initial()
        
        # Load assets (will be created later)
        self._init_assets()
        
        # Initialize Japanese font
        self._init_font()
        
        # Auto-load savegame if exists
        if os.path.exists("savegame.dat"):
            print("🏙️ Loading saved city from savegame.dat...")
            self.load_city("savegame.dat")
            print("✅ City loaded successfully!")
        else:
            # Show startup tutorial for new players
            self._show_startup_tutorial()

        # Start game loop (only if not using GameLauncher)
        if not skip_pyxel_init:
            pyxel.run(self.update, self.draw)

    def _show_startup_tutorial(self):
        """起動時にチュートリアルを表示 / Show tutorial on startup"""
        print("=" * 70)
        print("🎮 ようこそ ConcLand へ！ Welcome to ConcLand!")
        print("=" * 70)
        print()
        print("🎮 はじめてプレイされる方向けに、基本操作を紹介します。")
        print()
        print("📋 やること:")
        print()
        print("1. まずは道路を作りましょう")
        print("   → R キーを押して「道路」を選択")
        print("   → カーソルを移動して「スペース」キーで配置")
        print()
        print("2. 住宅を作りましょう")
        print("   → Q キーを押して「住宅」を選択")
        print("   → 道路に隣接する場所に「スペース」キーで配置")
        print()
        print("3. 発電所を建てましょう")
        print("   → I キーを押して「発電所」を選択")
        print("   → 資金が足りない場合は、待機してから")
        print()
        print("4. 時間が経つと都市が発展します")
        print("   → 人口が増えると税収入が増えます")
        print("   → さらに多くの施設を建てられるようになります")
        print()
        print("🆘 ヘルプ:")
        print("・ゲーム中に「H」キーを押すと、いつでも操作ガイドが表示されます")
        print("・「V」キーで表示モードを切り替えて、都市の状態を確認できます")
        print()
        print("✨ それでは、楽しい都市建設を！ Have fun!")
        print("=" * 70)
        print()

    def _init_world(self):
        """Initialize the game world with Voronoi-generated terrain"""
        # Check if we should load from saved terrain (prioritize 100x100 terrain)
        if os.path.exists("terrain_100.dat"):
            print("🗺️ Loading saved 100x100 terrain from terrain_100.dat...")
            self._load_terrain("terrain_100.dat")
            return
        elif os.path.exists("terrain.dat"):
            print("🗺️ Loading saved terrain from terrain.dat...")
            self._load_terrain("terrain.dat")
            return
        
        print("🌍 Generating new Voronoi terrain...")
        
        # Generate terrain using Voronoi diagrams
        terrain_gen = VoronoiTerrainGenerator(MAP_SIZE, MAP_SIZE)
        terrain_gen.generate_random_seeds(20)  # 20 seed points for good variety
        voronoi_terrain = terrain_gen.generate_terrain()
        terrain_gen.print_terrain_stats(voronoi_terrain)
        
        # Generate detailed coastlines
        coastlined_terrain, coastline_map = terrain_gen.generate_detailed_coastlines(voronoi_terrain)
        self.coastline_map = coastline_map  # Store for rendering
        
        # Convert Voronoi terrain to game grid
        terrain_mapping = {
            TerrainType.WATER: CellType.WATER,
            TerrainType.SAND: CellType.EMPTY,  # Sand becomes buildable land
            TerrainType.GRASS: CellType.EMPTY,  # Grass becomes buildable land  
            TerrainType.SOIL: CellType.EMPTY,   # Soil becomes buildable land
            TerrainType.COASTLINE: CellType.EMPTY  # Coastline becomes buildable land
        }
        
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                terrain_type = coastlined_terrain[y][x]
                self.grid[y][x] = terrain_mapping[terrain_type]
        
        # Don't add ANY initial infrastructure - keep map completely clean
        # self._add_initial_infrastructure()  # DISABLED for clean map
        
        # Save the terrain for reuse (press T to save terrain)
        print("💡 Press T to save this terrain for future use")
    
    def _add_initial_infrastructure(self):
        """Add some initial roads and a power plant to generated terrain"""
        # Find a good spot for a power plant (non-water, has some space)
        power_plant_placed = False
        attempts = 0
        while not power_plant_placed and attempts < 20:
            x = random.randint(5, MAP_SIZE - 8)
            y = random.randint(5, MAP_SIZE - 8)
            if self._can_place_4x4_building(x, y):
                self._place_4x4_building(x, y, CellType.COAL_PLANT)
                power_plant_placed = True
                print(f"⚡ Power plant placed at ({x}, {y})")
            attempts += 1
        
        # Create connected road network
        road_count = self._create_road_network()
        print(f"🛣️  Created road network with {road_count} segments")
        self._spread_power()
    
    def _create_road_network(self) -> int:
        """Create a connected road network instead of random roads"""
        road_count = 0
        
        # Find power plant location for road connection
        power_plant_pos = None
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                if self.grid[y][x] == CellType.COAL_PLANT:
                    power_plant_pos = (x, y)
                    break
            if power_plant_pos:
                break
        
        if not power_plant_pos:
            return 0
        
        # Create main roads from power plant
        road_count += self._create_main_roads(power_plant_pos)
        
        # Add some connecting roads
        road_count += self._create_connecting_roads()
        
        return road_count
    
    def _create_main_roads(self, power_plant_pos: tuple) -> int:
        """Create main roads extending from power plant"""
        px, py = power_plant_pos
        road_count = 0
        
        # Create horizontal main road
        for x in range(max(0, px - 15), min(MAP_SIZE, px + 15)):
            if self.grid[py][x] == CellType.EMPTY:
                self.grid[py][x] = CellType.ROAD
                self.sim_data[py][x] = SimData()
                self.sim_data[py][x].power = True
                road_count += 1
        
        # Create vertical main road  
        for y in range(max(0, py - 15), min(MAP_SIZE, py + 15)):
            if self.grid[y][px] == CellType.EMPTY:
                self.grid[y][px] = CellType.ROAD
                self.sim_data[y][px] = SimData()
                self.sim_data[y][px].power = True
                road_count += 1
        
        return road_count
    
    def _create_connecting_roads(self) -> int:
        """Create secondary roads connecting to main roads"""
        road_count = 0
        
        # Find existing roads to extend from
        existing_roads = []
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                if self.grid[y][x] == CellType.ROAD:
                    existing_roads.append((x, y))
        
        # Create a few branch roads
        for _ in range(3):  # 3 branch roads
            if not existing_roads:
                break
                
            # Pick random existing road as starting point
            start_x, start_y = random.choice(existing_roads)
            
            # Choose random direction
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            dx, dy = random.choice(directions)
            
            # Extend road in that direction
            length = random.randint(5, 12)
            for i in range(1, length):
                new_x = start_x + dx * i
                new_y = start_y + dy * i
                
                # Check bounds and availability
                if (0 <= new_x < MAP_SIZE and 0 <= new_y < MAP_SIZE and 
                    self.grid[new_y][new_x] == CellType.EMPTY):
                    
                    self.grid[new_y][new_x] = CellType.ROAD
                    self.sim_data[new_y][new_x] = SimData()
                    self.sim_data[new_y][new_x].power = True
                    existing_roads.append((new_x, new_y))
                    road_count += 1
                else:
                    break  # Stop if blocked
        
        return road_count
    
    def _init_assets(self):
        """Initialize graphics assets with new Individual Tile System"""
        print("🚀 Initializing Individual Tile System for ConcLand")
        
        # Initialize tile manager
        self.tile_manager = ImageTileSystem()
        
        # Initialize the new tile system (loads palette + individual tiles)
        success = self.tile_manager.initialize()
        self.use_graphics = success
        
        # Initialize train system
        self.train_system = TrainSystem(self.grid, MAP_SIZE)
        
        # Log results
        with open('concland_debug.log', 'w') as f:
            f.write("=== ConcLand Individual Tile System ===\n")
            f.write(f"Palette loaded: {'YES' if self.tile_manager.palette_loaded else 'NO'}\n")
            f.write(f"Individual tiles: {len(self.tile_manager.tile_images)}\n")
            f.write(f"Graphics status: {'ENABLED' if success else 'FALLBACK'}\n")
        
        print(f"🎨 Palette: {'✅ 256-color custom' if self.tile_manager.palette_loaded else '⚠️  16-color default'}")
        print(f"🎮 Tiles: {len(self.tile_manager.tile_images)} loaded")
        print(f"📊 Graphics: {'✅ Individual PNGs' if success else '⚠️  Colored fallbacks'}")
        
        # Use palette status from tile manager
        self.palette_loaded = self.tile_manager.palette_loaded
        
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
        # Qキーでの終了を無効化（誤操作防止）
        # if pyxel.btnp(pyxel.KEY_Q):
        #     pyxel.quit()
        
        # Update minimap display timer
        if self.move_timer > 0:
            self.move_timer -= 1
            if self.move_timer == 0:
                self.is_moving = False

        # Update help timer
        if self.help_timer > 0:
            self.help_timer -= 1
            if self.help_timer == 0:
                self.help_visible = False
        
        # Handle confirmation timeout
        if self.confirm_timer > 0:
            self.confirm_timer -= 1
            if self.confirm_timer == 0:
                self.save_confirm = False
                self.load_confirm = False
                self.show_message = ""
        
        # Manual RCI merge trigger (M key) - for testing
        if pyxel.btnp(pyxel.KEY_M):
            print("🔨 Manual RCI merge triggered")
            self._check_rci_merging()
        
        # Force merge at cursor (B key) - for testing
        if pyxel.btnp(pyxel.KEY_B):
            x, y = self.cursor_x, self.cursor_y
            cell_type = self.grid[y][x]
            if cell_type in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL]:
                print(f"🔧 Force merging {cell_type.name} at ({x},{y})")
                if self._can_merge_2x2(x, y, cell_type):
                    self._merge_rci_2x2(x, y, cell_type)
                    print("✅ 2x2 force merge successful")
                elif self._can_merge_3x3(x, y, cell_type):
                    self._merge_rci_3x3(x, y, cell_type)  
                    print("✅ 3x3 force merge successful")
                else:
                    print("❌ Force merge failed - checking conditions:")
                    print(f"   Population: {self.sim_data[y][x].population}")
                    print(f"   Power: {self.sim_data[y][x].power}")
                    print(f"   Land value: {self.sim_data[y][x].land_value}")
                    print(f"   Already merged: {self.sim_data[y][x].merged_size > 1}")
            else:
                print(f"❌ Cannot merge {cell_type.name} - not RCI zone")
        
        # Save with confirmation (N key, changed from M)
        if pyxel.btnp(pyxel.KEY_N):
            if self.save_confirm:
                # Second press - execute save
                self.save_city("savegame.dat")
                self.save_confirm = False
                self.confirm_timer = 0
            else:
                # First press - show confirmation
                self.save_confirm = True
                self.confirm_timer = 120  # 2 seconds at 60 FPS
                self.show_message = "もう一度Mキーでセーブ確定 / Press M again to save"
                self.message_timer = 120
        
        # Load with confirmation (N key)
        if pyxel.btnp(pyxel.KEY_N):
            if self.load_confirm:
                # Second press - execute load
                self.load_city("savegame.dat")
                self.load_confirm = False
                self.confirm_timer = 0
            else:
                # First press - show confirmation
                self.load_confirm = True
                self.confirm_timer = 120  # 2 seconds at 60 FPS
                self.show_message = "もう一度Nキーでロード確定 / Press N again to load"
                self.message_timer = 120
        
        # Terrain save function removed (G key now used for middle park)
        
        # Update tile animations
        if self.use_graphics:
            self.tile_manager.update_animation()
        
        self._handle_input()
        self._update_simulation()

        # Update camera to follow cursor
        self._update_camera()

        # Update UI system (staggered for performance)
        if hasattr(self, 'ui_system') and self.ui_data_needs_update:
            ui_data = self._prepare_ui_data()
            self.ui_system.update(ui_data)
            self.ui_data_needs_update = False

    def _prepare_ui_data(self) -> dict:
        """Prepare data for UI system"""
        ui_data = {
            "population": self.total_population,
            "funds": self.funds,
            "gdp": self.gdp,
            "employment_rate": self.employment_rate,
            "total_traffic": self._get_total_traffic(),
            "avg_pollution": self._get_average_pollution(),
            "avg_land_value": self._get_average_land_value(),
            "residential_demand": self.res_demand,
            "commercial_demand": self.com_demand,
            "industrial_demand": self.ind_demand,
            "tax_rate": self.tax_rate,
            "year": self.year,
            "month": self.month,
            "day": self.day
        }

        # Add advanced system data if available
        if hasattr(self, 'traffic_system'):
            ui_data["traffic_system"] = self.traffic_system.get_traffic_status()
        if hasattr(self, 'economic_system'):
            ui_data["economic_system"] = self.economic_system.get_economic_status()
        if hasattr(self, 'disaster_system'):
            ui_data["disaster_system"] = self.disaster_system.get_disaster_status()

        return ui_data

    def _get_total_traffic(self) -> float:
        """Calculate total traffic for UI"""
        # Simplified traffic calculation
        return sum([sim_data.traffic for row in self.sim_data for sim_data in row])

    def _get_average_pollution(self) -> float:
        """Calculate average pollution for UI"""
        total = sum([sim_data.pollution for row in self.sim_data for sim_data in row])
        return total / (MAP_SIZE * MAP_SIZE) if MAP_SIZE > 0 else 0

    def _get_average_land_value(self) -> float:
        """Calculate average land value for UI"""
        total = sum([sim_data.land_value for row in self.sim_data for sim_data in row])
        return total / (MAP_SIZE * MAP_SIZE) if MAP_SIZE > 0 else 0

    def _sync_economic_data_initial(self):
        """Initial sync of existing economic variables with economic_system"""
        if hasattr(self, 'economic_system'):
            # Sync existing funds to economic_system
            self.economic_system.funds = self.funds
            # Sync existing tax rate (convert from percentage to decimal)
            self.economic_system.tax_policy.residential_rate = self.tax_rate / 100.0
            self.economic_system.tax_policy.commercial_rate = self.tax_rate / 100.0
            self.economic_system.tax_policy.industrial_rate = self.tax_rate / 100.0

    def _sync_economic_data(self):
        """Sync economic data between existing and new systems"""
        if hasattr(self, 'economic_system'):
            # Sync from economic_system to existing variables
            self.funds = self.economic_system.funds
            # Convert tax rate from decimal to percentage
            self.tax_rate = int(self.economic_system.tax_policy.residential_rate * 100)
            # Sync GDP
            self.gdp = self.economic_system.indicators.gdp
            # Sync employment rate (economic_system has unemployment)
            self.employment_rate = 1.0 - self.economic_system.indicators.unemployment

    def _count_buildings_by_type(self) -> dict:
        """Count buildings by type for economic system"""
        buildings = {
            'RESIDENTIAL': 0,
            'COMMERCIAL': 0,
            'INDUSTRIAL': 0,
            'ROAD': 0,
            'RAIL': 0,
            'POWER_PLANT': 0,
            'POLICE': 0,
            'FIRE': 0,
            'HOSPITAL': 0
        }

        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                cell_type = self.grid[y][x]
                if cell_type == CellType.RESIDENTIAL:
                    buildings['RESIDENTIAL'] += 1
                elif cell_type == CellType.COMMERCIAL:
                    buildings['COMMERCIAL'] += 1
                elif cell_type == CellType.INDUSTRIAL:
                    buildings['INDUSTRIAL'] += 1
                elif cell_type == CellType.ROAD:
                    buildings['ROAD'] += 1
                elif cell_type == CellType.RAIL:
                    buildings['RAIL'] += 1
                elif cell_type in [CellType.COAL_PLANT, CellType.NUCLEAR_PLANT, CellType.GAS_PLANT,
                                  CellType.WIND_PLANT, CellType.SOLAR_PLANT, CellType.OIL_PLANT]:
                    buildings['POWER_PLANT'] += 1
                elif cell_type == CellType.POLICE:
                    buildings['POLICE'] += 1
                elif cell_type == CellType.FIRE:
                    buildings['FIRE'] += 1
                elif cell_type == CellType.HOSPITAL:
                    buildings['HOSPITAL'] += 1

        return buildings

    def _handle_input(self):
        """Handle keyboard input with repeat"""
        # Handle UI system shortcuts first
        if hasattr(self, 'ui_system'):
            # Panel switching shortcuts
            if pyxel.btnp(pyxel.KEY_S):
                self.ui_system.set_panel(UIPanel.STATISTICS)
                self.ui_data_needs_update = True
                return  # Skip other input when in UI panel
            elif pyxel.btnp(pyxel.KEY_E):
                self.ui_system.set_panel(UIPanel.ECONOMY)
                self.ui_data_needs_update = True
                return
            elif pyxel.btnp(pyxel.KEY_T):
                self.ui_system.set_panel(UIPanel.TRAFFIC)
                self.ui_data_needs_update = True
                return
            elif pyxel.btnp(pyxel.KEY_D):
                self.ui_system.set_panel(UIPanel.DISASTERS)
                self.ui_data_needs_update = True
                return
            elif pyxel.btnp(pyxel.KEY_P):
                self.ui_system.set_panel(UIPanel.POLICIES)
                self.ui_data_needs_update = True
                return
            elif pyxel.btnp(pyxel.KEY_ESCAPE):
                # Return to main game
                if self.ui_system.current_panel != UIPanel.MAIN_GAME:
                    self.ui_system.set_panel(UIPanel.MAIN_GAME)
                    return

        # If in UI panel, don't process game input
        if hasattr(self, 'ui_system') and self.ui_system.current_panel != UIPanel.MAIN_GAME:
            return

        # Reduce key repeat timer
        if self.key_repeat_timer > 0:
            self.key_repeat_timer -= 1

        # Toggle palette mode with B key
        if pyxel.btnp(pyxel.KEY_B):
            self.palette_mode = not self.palette_mode
            if self.palette_mode:
                # Entering palette mode - set cursor to current tool
                building_items = [
                    ItemMode.RESIDENTIAL, ItemMode.COMMERCIAL, ItemMode.INDUSTRIAL,
                    ItemMode.ROAD, ItemMode.RAIL, ItemMode.PARK, ItemMode.WIRE,
                    ItemMode.COAL_PLANT, ItemMode.NUCLEAR_PLANT, ItemMode.POLICE,
                    ItemMode.BULLDOZE
                ]
                if self.current_item in building_items:
                    self.palette_cursor = building_items.index(self.current_item)
        
        moved = False
        
        if self.palette_mode:
            # Single row palette cursor movement
            total_items = 11  # Total number of items
            
            if pyxel.btn(pyxel.KEY_LEFT):
                if self.key_repeat_timer <= 0:
                    if self.palette_cursor > 0:
                        self.palette_cursor -= 1
                    moved = True
            elif pyxel.btn(pyxel.KEY_RIGHT):
                if self.key_repeat_timer <= 0:
                    if self.palette_cursor < total_items - 1:
                        self.palette_cursor += 1
                    moved = True
            
            # Select item with Space/Z in palette mode
            if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z):
                building_items = [
                    ItemMode.RESIDENTIAL, ItemMode.COMMERCIAL, ItemMode.INDUSTRIAL,
                    ItemMode.ROAD, ItemMode.RAIL, ItemMode.PARK, ItemMode.WIRE,
                    ItemMode.COAL_PLANT, ItemMode.NUCLEAR_PLANT, ItemMode.POLICE,
                    ItemMode.BULLDOZE
                ]
                self.current_item = building_items[self.palette_cursor]
                self.palette_mode = False  # Exit palette mode after selection
                self.just_selected_item = True  # Set flag to prevent immediate placement
            
            # Exit palette mode with Escape
            if pyxel.btnp(pyxel.KEY_ESCAPE):
                self.palette_mode = False
        else:
            # Normal map cursor movement
            # Horizontal movement
            if pyxel.btn(pyxel.KEY_LEFT) and self.cursor_x > 0:
                if self.key_repeat_timer <= 0:
                    self.cursor_x -= 1
                    moved = True
            elif pyxel.btn(pyxel.KEY_RIGHT) and self.cursor_x < MAP_SIZE - 1:
                if self.key_repeat_timer <= 0:
                    self.cursor_x += 1
                    moved = True
            
            # Vertical movement (separate from horizontal for diagonal)
            if pyxel.btn(pyxel.KEY_UP) and self.cursor_y > 0:
                if self.key_repeat_timer <= 0:
                    self.cursor_y -= 1
                    moved = True
            elif pyxel.btn(pyxel.KEY_DOWN) and self.cursor_y < MAP_SIZE - 1:
                if self.key_repeat_timer <= 0:
                    self.cursor_y += 1
                    moved = True
        
        if moved:
            self.key_repeat_timer = 5  # Moderate repeat rate
        
        # Item selection with QWERTY keys
        # Top row - Basic zones and infrastructure
        if pyxel.btnp(pyxel.KEY_Q):
            self.current_item = ItemMode.RESIDENTIAL
        elif pyxel.btnp(pyxel.KEY_W):
            self.current_item = ItemMode.COMMERCIAL
        elif pyxel.btnp(pyxel.KEY_E):
            self.current_item = ItemMode.INDUSTRIAL
        elif pyxel.btnp(pyxel.KEY_R):
            self.current_item = ItemMode.ROAD
        elif pyxel.btnp(pyxel.KEY_T):
            # Cycle through rail and station
            self._cycle_item('rail')
        elif pyxel.btnp(pyxel.KEY_Y):
            # Cycle through park types
            self._cycle_item('park')
        elif pyxel.btnp(pyxel.KEY_U):
            self.current_item = ItemMode.WIRE
        elif pyxel.btnp(pyxel.KEY_I):
            # Cycle through power plants
            self._cycle_item('power')
        elif pyxel.btnp(pyxel.KEY_O):
            # Cycle through port facilities
            self._cycle_item('port')
        elif pyxel.btnp(pyxel.KEY_P):
            # Cycle through public services
            self._cycle_item('public')
        elif pyxel.btnp(pyxel.KEY_8):
            # Cycle through special facilities
            self._cycle_item('special')
        elif pyxel.btnp(pyxel.KEY_9):
            # Cycle through water facilities
            self._cycle_item('water')
        # Bulldozer on backslash
        elif pyxel.btnp(pyxel.KEY_BACKSLASH):
            self.current_item = ItemMode.BULLDOZE
        # Agricultural on A key
        elif pyxel.btnp(pyxel.KEY_A):
            self.current_item = ItemMode.AGRICULTURAL

        # Toggle help display with H key
        elif pyxel.btnp(pyxel.KEY_H):
            self.help_visible = not self.help_visible
            if self.help_visible:
                self.help_timer = 300  # 5秒間表示（60FPS × 5）
            self.show_startup_help = False  # 一度操作したら起動時ヘルプは非表示
        
        # View mode toggle - add water view
        if pyxel.btnp(pyxel.KEY_V):
            self.view_mode = (self.view_mode + 1) % 6  # 6 view modes now (normal, pollution, land_value, power, traffic, water)
        
        # Toggle minimap visibility with TAB key
        if pyxel.btnp(pyxel.KEY_TAB):
            self.always_show_minimap = not self.always_show_minimap
        
        # Toggle balance graph display
        if pyxel.btnp(pyxel.KEY_G):
            self.show_balance_graph = not self.show_balance_graph
        
        # No scrolling needed for fixed 2-row layout
        
        # Mouse click on item palette
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mouse_x = pyxel.mouse_x
            mouse_y = pyxel.mouse_y
            
            # Check if clicking in item palette area (2 rows = 36 pixels)
            if mouse_y < 36:
                # Check for item clicks in 2-row layout
                building_items = [
                    ItemMode.RESIDENTIAL, ItemMode.COMMERCIAL, ItemMode.INDUSTRIAL,
                    ItemMode.ROAD, ItemMode.RAIL, ItemMode.PARK,
                    ItemMode.WIRE, ItemMode.COAL_PLANT, ItemMode.NUCLEAR_PLANT,
                    ItemMode.POLICE, ItemMode.BULLDOZE
                ]
                
                # Calculate which item was clicked (3 rows x 8 columns)
                icon_size = 8
                gap = 2  # 2px gap
                start_x = 64  # After info area
                cols_per_row = 8
                row_height = 11
                start_y = 3
                
                for i, item_mode in enumerate(building_items):
                    row = i // cols_per_row
                    col = i % cols_per_row
                    item_x = start_x + col * (icon_size + gap)
                    item_y = start_y + row * row_height
                    
                    if item_x <= mouse_x < item_x + icon_size and item_y <= mouse_y < item_y + icon_size:
                        self.current_item = item_mode
                        break
        
        # Place/remove buildings (only in map mode, not palette mode)
        if not self.palette_mode:
            # Clear the just_selected_item flag if keys are released
            if self.just_selected_item:
                if not (pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.KEY_Z)):
                    self.just_selected_item = False
            else:
                # Only allow building if we didn't just select a tool
                # Check for continuous building tools (including RCI zones)
                continuous_tools = [ItemMode.BULLDOZE, ItemMode.PARK, ItemMode.ROAD, ItemMode.RAIL,
                                   ItemMode.RESIDENTIAL, ItemMode.COMMERCIAL, ItemMode.INDUSTRIAL, ItemMode.AGRICULTURAL, ItemMode.WIRE]
                
                if self.current_item in continuous_tools:
                    # Continuous building while holding key
                    if pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.KEY_Z):
                        self._place_building()
                else:
                    # Single placement for other tools
                    if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z):
                        self._place_building()
        
        # Remove buildings
        if pyxel.btnp(pyxel.KEY_X):
            self._remove_building()
    
    def _cycle_item(self, group: str):
        """Cycle through items in a group"""
        if group in self.item_cycles:
            items = self.item_cycles[group]
            self.cycle_indices[group] = (self.cycle_indices[group] + 1) % len(items)
            self.current_item = items[self.cycle_indices[group]]
    
    def _place_building(self):
        """Place a building at cursor position"""
        x, y = self.cursor_x, self.cursor_y
        
        if self.current_item == ItemMode.BULLDOZE:
            self._remove_building()
            return
        
        # Check if building on water (but allow bridges for roads/rails/wires)
        if self.grid[y][x] == CellType.WATER:
            if self.current_item not in [ItemMode.ROAD, ItemMode.RAIL, ItemMode.WIRE]:
                return  # Only roads, rails, and wires can build on water (as bridges/cables)
        
        # Get cost for this building
        cost = self._get_building_cost(self.current_item)
        if not self.infinite_funds and self.funds < cost:
            return
        
        new_type = self._tool_to_cell_type(self.current_item)
        if not new_type:
            return
        
        # Check building size and place accordingly
        if new_type == CellType.AIRPORT:
            # Airport is 4x3 (32x24)
            if self._can_place_4x3_building(x, y):
                self._place_4x3_building(x, y, new_type)
                if not self.infinite_funds:
                    self.funds -= cost
        elif new_type == CellType.SOLAR_PLANT:
            # Solar is 2x2 (16x16)
            if self._can_place_2x2_building(x, y):
                self._place_2x2_building(x, y, new_type)
                if not self.infinite_funds:
                    self.funds -= cost
                self._spread_power()
        elif new_type in [CellType.LABORATORY, CellType.SPACE]:
            # Laboratory and Space Center are true 4x4
            if self._can_place_4x4_building(x, y):
                self._place_4x4_building(x, y, new_type)
                if not self.infinite_funds:
                    self.funds -= cost
        # Check if this is a 4x4 building (power plants)
        elif new_type in [CellType.COAL_PLANT, CellType.NUCLEAR_PLANT, CellType.GAS_PLANT, CellType.OIL_PLANT]:
            if self._can_place_4x4_building(x, y):
                self._place_4x4_building(x, y, new_type)
                if not self.infinite_funds:
                    self.funds -= cost
                self._spread_power()
        # Check if this is a 3x3 building (stations, public services and water facilities)
        elif new_type == CellType.STATION:
            # Station is 3x3 (24x24)
            if self._can_place_3x3_building(x, y):
                self._place_3x3_building(x, y, new_type)
                if not self.infinite_funds:
                    self.funds -= cost
                # Try to spawn a train at the new station
                self.train_system.update_network(self.grid, {'STATION': CellType.STATION, 'RAIL': CellType.RAIL})
                self.train_system.spawn_train((x+1, y+1))  # Center of 3x3 station
        elif new_type in [CellType.POLICE, CellType.FIRE, CellType.HOSPITAL, CellType.SCHOOL, CellType.UNIVERSITY, 
                         CellType.SEWAGE_PLANT, CellType.WATER_PLANT, CellType.LIBRARY,
                         CellType.MILITARY, CellType.PRISON, CellType.SHRINE, CellType.HELIPORT, CellType.SEAPORT,
                         CellType.INCINERATOR, CellType.WASTE_FACILITY, CellType.ONSEN, CellType.PACHINKO]:
            if self._can_place_3x3_building(x, y):
                self._place_3x3_building(x, y, new_type)
                if not self.infinite_funds:
                    self.funds -= cost
                # Update water system if water-related building
                if new_type in [CellType.SEWAGE_PLANT, CellType.WATER_PLANT, CellType.PUMP]:
                    self._spread_water()
        else:
            # 1x1 buildings (RCI zones, roads, rails, wires, parks, pump, wind power)
            # Special check for pump - can only be placed on coastline
            if new_type == CellType.PUMP:
                if not self._is_coastline_tile(x, y):
                    return  # Pump can only be placed on coastline
            
            if self._can_place_1x1_building(x, y, new_type):
                current_type = self.grid[y][x]
                
                # Handle road/rail overlap
                if (current_type == CellType.ROAD and new_type == CellType.RAIL) or \
                   (current_type == CellType.RAIL and new_type == CellType.ROAD):
                    # Create a special overlap cell for road/rail
                    self.sim_data[y][x].has_road = current_type == CellType.ROAD or new_type == CellType.ROAD
                    self.sim_data[y][x].has_rail = current_type == CellType.RAIL or new_type == CellType.RAIL
                    # Keep the most recently placed type in grid for simplicity
                    self.grid[y][x] = new_type
                else:
                    # Normal placement
                    if current_type == CellType.WATER:
                        # Store original terrain for bridges
                        self.sim_data[y][x] = SimData()  # Always create new SimData for water
                        self.sim_data[y][x].original_terrain = CellType.WATER
                        # Debug message removed - bridge placed
                    
                    # Normal placement - replace existing
                    self.grid[y][x] = new_type
                    
                    # Ensure SimData exists
                    if not isinstance(self.sim_data[y][x], SimData):
                        self.sim_data[y][x] = SimData()
                    
                    # For RCI zones, start with empty state (no population/density)
                    if new_type in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL]:
                        self.sim_data[y][x].population = 0
                        self.sim_data[y][x].density = 0
                
                if not self.infinite_funds:
                    self.funds -= cost

                # Update systems for relevant buildings
                if new_type in [CellType.COAL_PLANT, CellType.NUCLEAR_PLANT, CellType.WIND_PLANT,
                               CellType.GAS_PLANT, CellType.OIL_PLANT, CellType.SOLAR_PLANT]:
                    self._spread_power()
                elif new_type == CellType.PUMP:
                    self._spread_water()

                # Traffic system integration
                if hasattr(self, 'traffic_system'):
                    # Add traffic lights to roads (10% chance)
                    if new_type == CellType.ROAD and random.random() < 0.1:
                        self.traffic_system.add_traffic_light(x, y)
                    # Add bus stops to commercial/residential zones (5% chance)
                    elif new_type in [CellType.COMMERCIAL, CellType.RESIDENTIAL] and random.random() < 0.05:
                        # Find nearest bus route or create default route
                        route_id = "route_1" if random.random() < 0.5 else "route_2"
                        self.traffic_system.add_bus_stop(x, y, route_id)

                # Disaster system integration - register emergency services
                if hasattr(self, 'disaster_system'):
                    if new_type == CellType.FIRE:
                        self.disaster_system.register_emergency_service(x, y, "FIRE")
                    elif new_type == CellType.POLICE:
                        self.disaster_system.register_emergency_service(x, y, "POLICE")
                    elif new_type == CellType.HOSPITAL:
                        self.disaster_system.register_emergency_service(x, y, "HOSPITAL")
    
    def _can_place_1x1_building(self, x: int, y: int, new_type: CellType) -> bool:
        """Check if a 1x1 building can be placed at position"""
        current_type = self.grid[y][x]
        
        # Can always build on empty land or waste land
        if current_type in [CellType.EMPTY, CellType.WASTELAND]:
            return True
        
        # RCI zones can only be placed on empty or waste land
        if new_type in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL]:
            return current_type in [CellType.EMPTY, CellType.WASTELAND]
        
        # Special handling for water - allow bridges and cables
        if current_type == CellType.WATER:
            if new_type in [CellType.ROAD, CellType.RAIL]:
                # Check if this would be a straight bridge (only horizontal or vertical allowed)
                can_place = self._can_place_bridge(x, y, new_type)
                if not can_place:
                    pass  # Debug message removed - cannot place bridge
                return can_place
            elif new_type == CellType.WIRE:
                # Wires can only be placed on water (undersea cables)
                # For other placements, check in main logic
                return True
            return False
        
        # Allow road/rail overlap
        if (current_type == CellType.ROAD and new_type == CellType.RAIL) or \
           (current_type == CellType.RAIL and new_type == CellType.ROAD):
            return True
        
        # Can't overwrite multi-cell buildings (power plants and police)
        if current_type in [CellType.COAL_PLANT, CellType.NUCLEAR_PLANT, CellType.POLICE]:
            return False
        
        # Wire placement restriction - only on empty or water
        if new_type == CellType.WIRE:
            # Only allow on empty or water (not on roads/rails)
            return current_type in [CellType.EMPTY, CellType.WASTELAND, CellType.WATER]
        
        # Infrastructure replacement rules
        if current_type in [CellType.ROAD, CellType.RAIL, CellType.WIRE, CellType.PARK]:
            # Parks cannot be placed on roads or rails
            if new_type == CellType.PARK and current_type in [CellType.ROAD, CellType.RAIL]:
                return False
            # Roads and rails cannot be placed on parks
            if current_type == CellType.PARK and new_type in [CellType.ROAD, CellType.RAIL]:
                return False
            # Allow replacing same category (infrastructure)
            if current_type == new_type:
                return False  # Can't place same type on itself
            # Only allow road/rail overlap (already handled above)
            if (current_type == CellType.ROAD and new_type == CellType.RAIL) or \
               (current_type == CellType.RAIL and new_type == CellType.ROAD):
                return True  # This case should already be handled above
            return False  # Other combinations not allowed
        
        return False
    
    def _can_place_bridge(self, x: int, y: int, new_type: CellType) -> bool:
        """Check if a bridge can be placed at this water position"""
        # Check if we're actually on water (original terrain)
        is_water_cell = self.grid[y][x] == CellType.WATER or \
                       (hasattr(self.sim_data[y][x], 'original_terrain') and 
                        self.sim_data[y][x].original_terrain == CellType.WATER)
        
        if not is_water_cell:
            # Not on water, use normal placement rules
            return False
        
        # Check if this water already has a bridge
        current_cell = self.grid[y][x]
        if current_cell == CellType.ROAD or current_cell == CellType.RAIL:
            # Already has a bridge - only allow perpendicular road/rail crossing
            if (current_cell == CellType.ROAD and new_type == CellType.RAIL) or \
               (current_cell == CellType.RAIL and new_type == CellType.ROAD):
                return self._check_bridge_overlap_validity(x, y, current_cell, new_type)
            # Same type - never allow (this would create curves/intersections)
            print(f"  ❌ Cannot modify existing {current_cell.name} bridge at ({x},{y})")
            return False
        
        # Check for connections or land nearby
        north_road = False
        south_road = False
        east_road = False
        west_road = False
        
        north_land = False
        south_land = False
        east_land = False
        west_land = False
        
        if y > 0:
            north_road = self.grid[y-1][x] == new_type
            # Land = not water AND not a bridge on water
            north_land = (self.grid[y-1][x] != CellType.WATER and 
                         not (hasattr(self.sim_data[y-1][x], 'original_terrain') and 
                              self.sim_data[y-1][x].original_terrain == CellType.WATER))
        if y < MAP_SIZE-1:
            south_road = self.grid[y+1][x] == new_type
            south_land = (self.grid[y+1][x] != CellType.WATER and
                         not (hasattr(self.sim_data[y+1][x], 'original_terrain') and
                              self.sim_data[y+1][x].original_terrain == CellType.WATER))
        if x < MAP_SIZE-1:
            east_road = self.grid[y][x+1] == new_type
            east_land = (self.grid[y][x+1] != CellType.WATER and
                        not (hasattr(self.sim_data[y][x+1], 'original_terrain') and
                             self.sim_data[y][x+1].original_terrain == CellType.WATER))
        if x > 0:
            west_road = self.grid[y][x-1] == new_type
            west_land = (self.grid[y][x-1] != CellType.WATER and
                        not (hasattr(self.sim_data[y][x-1], 'original_terrain') and
                             self.sim_data[y][x-1].original_terrain == CellType.WATER))
        
        # Allow bridge if:
        # 1. Connected to existing road/rail
        # 2. Next to land (can start a bridge from shore)
        has_connection = north_road or south_road or east_road or west_road
        next_to_land = north_land or south_land or east_land or west_land
        
        if not has_connection and not next_to_land:
            # Debug: Bridge - No road connection and not next to land
            return False
        
        # If next to land but no road, allow starting a bridge
        if next_to_land and not has_connection:
            # Debug: Bridge start - Next to land
            return True
        
        # If has road connection, determine bridge direction
        if has_connection:
            # Check each adjacent bridge's direction
            bridge_directions = set()
            
            if north_road and y > 0:
                if hasattr(self.sim_data[y-1][x], 'original_terrain') and \
                   self.sim_data[y-1][x].original_terrain == CellType.WATER:
                    # Adjacent bridge to north - must be vertical bridge
                    bridge_directions.add('vertical')
            
            if south_road and y < MAP_SIZE-1:
                if hasattr(self.sim_data[y+1][x], 'original_terrain') and \
                   self.sim_data[y+1][x].original_terrain == CellType.WATER:
                    # Adjacent bridge to south - must be vertical bridge
                    bridge_directions.add('vertical')
            
            if east_road and x < MAP_SIZE-1:
                if hasattr(self.sim_data[y][x+1], 'original_terrain') and \
                   self.sim_data[y][x+1].original_terrain == CellType.WATER:
                    # Adjacent bridge to east - must be horizontal bridge
                    bridge_directions.add('horizontal')
            
            if west_road and x > 0:
                if hasattr(self.sim_data[y][x-1], 'original_terrain') and \
                   self.sim_data[y][x-1].original_terrain == CellType.WATER:
                    # Adjacent bridge to west - must be horizontal bridge  
                    bridge_directions.add('horizontal')
            
            # If we have bridges in both directions, that's an intersection - not allowed
            if len(bridge_directions) > 1:
                # Debug: Cannot create intersection on water
                return False
            
            # If extending from a bridge, must continue in same direction
            if bridge_directions:
                direction = list(bridge_directions)[0]
                if direction == 'vertical':
                    # Must only have north/south connections
                    if east_road or west_road:
                        # Debug: Cannot change direction on water (vertical)
                        return False
                    # Debug: Vertical bridge continuation
                    return True
                else:  # horizontal
                    # Must only have east/west connections
                    if north_road or south_road:
                        # Debug: Cannot change direction on water (horizontal)
                        return False
                    # Debug: Horizontal bridge continuation
                    return True
            
            # Starting from land - only one direction allowed
            connection_count = sum([north_road, south_road, east_road, west_road])
            if connection_count > 1:
                # Debug: Multiple connections not allowed when starting bridge
                return False
            
            if north_road or south_road:
                # Debug: Vertical bridge start
                return True
            if east_road or west_road:
                # Debug: Horizontal bridge start
                return True
            
            # Debug: Invalid bridge configuration
        
        return False
    
    def _check_bridge_overlap_validity(self, x: int, y: int, existing_type: CellType, new_type: CellType) -> bool:
        """Check if road/rail overlap on water maintains straight lines"""
        # Check existing bridge direction
        existing_north = y > 0 and self.grid[y-1][x] == existing_type
        existing_south = y < MAP_SIZE-1 and self.grid[y+1][x] == existing_type
        existing_east = x < MAP_SIZE-1 and self.grid[y][x+1] == existing_type
        existing_west = x > 0 and self.grid[y][x-1] == existing_type
        
        # Check new bridge direction
        new_north = y > 0 and self.grid[y-1][x] == new_type
        new_south = y < MAP_SIZE-1 and self.grid[y+1][x] == new_type
        new_east = x < MAP_SIZE-1 and self.grid[y][x+1] == new_type
        new_west = x > 0 and self.grid[y][x-1] == new_type
        
        # Existing must be straight (vertical or horizontal)
        existing_vertical = (existing_north or existing_south) and not (existing_east or existing_west)
        existing_horizontal = (existing_east or existing_west) and not (existing_north or existing_south)
        
        # New must be straight and perpendicular to existing
        new_vertical = (new_north or new_south) and not (new_east or new_west)
        new_horizontal = (new_east or new_west) and not (new_north or new_south)
        
        # Only allow perpendicular crossings
        if existing_vertical and new_horizontal:
            # Debug: Bridge crossing allowed - vertical with horizontal
            return True
        if existing_horizontal and new_vertical:
            # Debug: Bridge crossing allowed - horizontal with vertical
            return True
        
        # Debug: Bridge crossing not allowed - not perpendicular
        return False
    
    def _is_on_water(self, x: int, y: int) -> bool:
        """Check if a position is on water (considering bridges)"""
        if x < 0 or y < 0 or x >= MAP_SIZE or y >= MAP_SIZE:
            return False
        # Check the original terrain type stored when placing bridges
        return hasattr(self.sim_data[y][x], 'original_terrain') and \
               self.sim_data[y][x].original_terrain == CellType.WATER
    
    def _is_water_cell(self, x: int, y: int) -> bool:
        """Check if a cell is water or a bridge over water"""
        if x < 0 or y < 0 or x >= MAP_SIZE or y >= MAP_SIZE:
            return False
        return (self.grid[y][x] == CellType.WATER or 
                (hasattr(self.sim_data[y][x], 'original_terrain') and 
                 self.sim_data[y][x].original_terrain == CellType.WATER))
    
    def _can_place_3x3_building(self, x: int, y: int) -> bool:
        """Check if a 3x3 building can be placed at position"""
        # Check bounds
        if x + 2 >= MAP_SIZE or y + 2 >= MAP_SIZE:
            return False
        
        # Check if all 9 cells are empty, waste, or water
        for dy in range(3):
            for dx in range(3):
                cell_type = self.grid[y + dy][x + dx]
                if cell_type not in [CellType.EMPTY, CellType.WASTELAND, CellType.WATER]:
                    return False
        
        # Can't build on water
        if self.grid[y + 1][x + 1] == CellType.WATER:  # Center must not be water
            return False
            
        return True
    
    def _can_place_2x2_building(self, x: int, y: int) -> bool:
        """Check if a 2x2 building can be placed at position"""
        # Check bounds
        if x + 1 >= MAP_SIZE or y + 1 >= MAP_SIZE:
            return False
        
        # Check if all 4 cells are empty, waste
        for dy in range(2):
            for dx in range(2):
                cell_type = self.grid[y + dy][x + dx]
                if cell_type not in [CellType.EMPTY, CellType.WASTELAND]:
                    return False
        
        return True
    
    def _can_place_4x3_building(self, x: int, y: int) -> bool:
        """Check if a 4x3 building (like airport) can be placed at position"""
        # Check bounds
        if x + 3 >= MAP_SIZE or y + 2 >= MAP_SIZE:
            return False
        
        # Check if all 12 cells are empty, waste
        for dy in range(3):
            for dx in range(4):
                cell_type = self.grid[y + dy][x + dx]
                if cell_type not in [CellType.EMPTY, CellType.WASTELAND]:
                    return False
        
        return True
    
    def _can_place_8x4_building(self, x: int, y: int) -> bool:
        """Check if an 8x4 building can be placed at position"""
        # Check bounds  
        if x + 7 >= MAP_SIZE or y + 3 >= MAP_SIZE:
            return False
        
        # Check if all 32 cells are empty, waste, or water
        for dy in range(4):
            for dx in range(8):
                cell_type = self.grid[y + dy][x + dx]
                if cell_type not in [CellType.EMPTY, CellType.WASTELAND, CellType.WATER]:
                    return False
        
        # Can't build on water (check center cells)
        if self.grid[y + 1][x + 3] == CellType.WATER or self.grid[y + 2][x + 4] == CellType.WATER:
            return False
        
        return True
    
    def _can_place_4x4_building(self, x: int, y: int) -> bool:
        """Check if a 4x4 building can be placed at position"""
        # Check bounds
        if x + 3 >= MAP_SIZE or y + 3 >= MAP_SIZE:
            return False
        
        # Check if all 16 cells are empty, waste, or water
        for dy in range(4):
            for dx in range(4):
                cell_type = self.grid[y + dy][x + dx]
                if cell_type not in [CellType.EMPTY, CellType.WASTELAND, CellType.WATER]:
                    return False
        
        # Can't build on water (check center cells)
        if self.grid[y + 1][x + 1] == CellType.WATER or self.grid[y + 2][x + 2] == CellType.WATER:
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
                # Set initial density for RCI zones
                if building_type in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL]:
                    self.sim_data[y + dy][x + dx].density = 1
                
                # Power plants generate power
                if building_type in [CellType.COAL_PLANT, CellType.NUCLEAR_PLANT]:
                    self.sim_data[y + dy][x + dx].power = True
    
    def _place_2x2_building(self, x: int, y: int, building_type: CellType):
        """Place a 2x2 building"""
        building_id = self.next_building_id
        self.next_building_id += 1
        
        # Place building in all 4 cells
        for dy in range(2):
            for dx in range(2):
                self.grid[y + dy][x + dx] = building_type
                self.sim_data[y + dy][x + dx] = SimData()
                self.sim_data[y + dy][x + dx].building_id = building_id
                
                # Solar plants generate power
                if building_type == CellType.SOLAR_PLANT:
                    self.sim_data[y + dy][x + dx].power = True
    
    def _place_4x3_building(self, x: int, y: int, building_type: CellType):
        """Place a 4x3 building (like airport)"""
        building_id = self.next_building_id
        self.next_building_id += 1
        
        # Place building in all 12 cells
        for dy in range(3):
            for dx in range(4):
                self.grid[y + dy][x + dx] = building_type
                self.sim_data[y + dy][x + dx] = SimData()
                self.sim_data[y + dy][x + dx].building_id = building_id
    
    def _place_8x4_building(self, x: int, y: int, building_type: CellType):
        """Place an 8x4 building at the specified position"""
        building_id = self.next_building_id
        self.next_building_id += 1
        
        for dy in range(4):
            for dx in range(8):
                self.grid[y + dy][x + dx] = building_type
                self.sim_data[y + dy][x + dx] = SimData()
                self.sim_data[y + dy][x + dx].building_id = building_id
                
                # Power plants generate power
                if building_type in [CellType.COAL_PLANT, CellType.NUCLEAR_PLANT]:
                    self.sim_data[y + dy][x + dx].power = True
    
    def _place_4x4_building(self, x: int, y: int, building_type: CellType):
        """Place a 4x4 building"""
        building_id = self.next_building_id
        self.next_building_id += 1
        
        # Place building in all 16 cells
        for dy in range(4):
            for dx in range(4):
                self.grid[y + dy][x + dx] = building_type
                self.sim_data[y + dy][x + dx] = SimData()
                self.sim_data[y + dy][x + dx].building_id = building_id
                
                # Power plants generate power
                if building_type in [CellType.COAL_PLANT, CellType.NUCLEAR_PLANT]:
                    self.sim_data[y + dy][x + dx].power = True
    
    def _remove_building(self):
        """Remove building at cursor position"""
        x, y = self.cursor_x, self.cursor_y
        
        
        if self.grid[y][x] in [CellType.EMPTY, CellType.WATER, CellType.WASTELAND]:
            return  # Can't bulldoze empty, water, or already bulldozed land
        
        cell_type = self.grid[y][x]
        
        # If it's a multi-cell building, remove the entire building
        if cell_type in [CellType.COAL_PLANT, CellType.NUCLEAR_PLANT, CellType.GAS_PLANT, 
                        CellType.OIL_PLANT, CellType.SOLAR_PLANT, CellType.LABORATORY, 
                        CellType.SPACE, CellType.AIRPORT, CellType.POLICE, CellType.FIRE,
                        CellType.HOSPITAL, CellType.SCHOOL, CellType.UNIVERSITY, 
                        CellType.SEWAGE_PLANT, CellType.WATER_PLANT, CellType.LIBRARY,
                        CellType.MILITARY, CellType.PRISON, CellType.SHRINE, 
                        CellType.HELIPORT, CellType.SEAPORT, CellType.INCINERATOR,
                        CellType.WASTE_FACILITY, CellType.ONSEN, CellType.PACHINKO]:
            building_id = self.sim_data[y][x].building_id
            if building_id > 0:
                self._remove_multi_cell_building(building_id)
                self.funds += 10  # Larger refund for 3x3 buildings
            else:
                # Single cell of what should be a 3x3 building
                self.grid[y][x] = CellType.WASTELAND  # Bulldozed land becomes waste
                self.sim_data[y][x] = SimData()
                self.funds += 5
        else:
            # 1x1 building (road, rail, wire, park)
            # Check if this was a bridge over water
            if hasattr(self.sim_data[y][x], 'original_terrain') and self.sim_data[y][x].original_terrain == CellType.WATER:
                # Restore water
                self.grid[y][x] = CellType.WATER
                # Debug: Bridge removed, water restored
            else:
                # Normal ground becomes waste after bulldozing
                self.grid[y][x] = CellType.WASTELAND
            
            self.sim_data[y][x] = SimData()
            self.funds += 2  # Small refund
        
        self._spread_power()
    
    def _remove_multi_cell_building(self, building_id: int):
        """Remove entire multi-cell building by ID (3x3 or 4x4)"""
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                if self.sim_data[y][x].building_id == building_id:
                    self.grid[y][x] = CellType.WASTELAND  # Bulldozed land becomes waste
                    self.sim_data[y][x] = SimData()
    
    def _tool_to_cell_type(self, tool: ItemMode) -> Optional[CellType]:
        """Convert item mode to cell type"""
        mapping = {
            ItemMode.RESIDENTIAL: CellType.RESIDENTIAL,
            ItemMode.COMMERCIAL: CellType.COMMERCIAL,
            ItemMode.INDUSTRIAL: CellType.INDUSTRIAL,
            ItemMode.ROAD: CellType.ROAD,
            ItemMode.RAIL: CellType.RAIL,
            ItemMode.STATION: CellType.STATION,
            ItemMode.WIRE: CellType.WIRE,
            ItemMode.PARK: CellType.PARK,
            ItemMode.COAL_PLANT: CellType.COAL_PLANT,
            ItemMode.NUCLEAR_PLANT: CellType.NUCLEAR_PLANT,
            ItemMode.GAS_PLANT: CellType.GAS_PLANT,
            ItemMode.WIND_PLANT: CellType.WIND_PLANT,
            ItemMode.POLICE: CellType.POLICE,
            ItemMode.FIRE: CellType.FIRE,
            ItemMode.HOSPITAL: CellType.HOSPITAL,
            ItemMode.SCHOOL: CellType.SCHOOL,
            ItemMode.UNIVERSITY: CellType.UNIVERSITY,
            ItemMode.PARK_MIDDLE: CellType.PARK_MIDDLE,
            ItemMode.SEWAGE_PLANT: CellType.SEWAGE_PLANT,
            ItemMode.WATER_PLANT: CellType.WATER_PLANT,
            ItemMode.PUMP: CellType.PUMP,
            ItemMode.AGRICULTURAL: CellType.AGRICULTURAL,
            # New items
            ItemMode.LIBRARY: CellType.LIBRARY,
            ItemMode.LABORATORY: CellType.LABORATORY,
            ItemMode.MILITARY: CellType.MILITARY,
            ItemMode.PRISON: CellType.PRISON,
            ItemMode.SHRINE: CellType.SHRINE,
            ItemMode.SPACE: CellType.SPACE,
            ItemMode.AIRPORT: CellType.AIRPORT,
            ItemMode.HELIPORT: CellType.HELIPORT,
            ItemMode.SEAPORT: CellType.SEAPORT,
            ItemMode.SOLAR_PLANT: CellType.SOLAR_PLANT,
            ItemMode.OIL_PLANT: CellType.OIL_PLANT,
            ItemMode.INCINERATOR: CellType.INCINERATOR,
            ItemMode.WASTE_FACILITY: CellType.WASTE_FACILITY,
            ItemMode.ONSEN: CellType.ONSEN,
            ItemMode.PACHINKO: CellType.PACHINKO
        }
        return mapping.get(tool)
    
    def _get_building_cost(self, tool: ItemMode) -> int:
        """Get the cost of a building"""
        costs = {
            ItemMode.BULLDOZE: 1,
            ItemMode.RESIDENTIAL: 20,  # Cheaper for 1x1
            ItemMode.COMMERCIAL: 30,   # Cheaper for 1x1
            ItemMode.INDUSTRIAL: 25,   # Cheaper for 1x1
            ItemMode.ROAD: 10,
            ItemMode.RAIL: 25,
            ItemMode.STATION: 500,  # Train station
            ItemMode.WIRE: 5,
            ItemMode.PARK: 20,
            ItemMode.COAL_PLANT: 3000,
            ItemMode.NUCLEAR_PLANT: 5000,
            ItemMode.GAS_PLANT: 2500,
            ItemMode.WIND_PLANT: 2000,
            ItemMode.POLICE: 500,
            ItemMode.FIRE: 500,
            ItemMode.HOSPITAL: 800,
            ItemMode.SCHOOL: 400,
            ItemMode.UNIVERSITY: 1200,
            ItemMode.PARK_MIDDLE: 150,
            ItemMode.SEWAGE_PLANT: 1000,
            ItemMode.WATER_PLANT: 1500,
            ItemMode.PUMP: 200,
            ItemMode.AGRICULTURAL: 15,  # Cheap to zone agricultural land
            # New public facilities
            ItemMode.LIBRARY: 600,
            ItemMode.LABORATORY: 2000,
            ItemMode.MILITARY: 3000,
            ItemMode.PRISON: 1500,
            ItemMode.SHRINE: 300,
            ItemMode.SPACE: 10000,
            # Port facilities
            ItemMode.AIRPORT: 5000,
            ItemMode.HELIPORT: 2000,
            ItemMode.SEAPORT: 4000,
            # Additional power
            ItemMode.SOLAR_PLANT: 3500,
            ItemMode.OIL_PLANT: 4500,
            # Waste management
            ItemMode.INCINERATOR: 2000,
            ItemMode.WASTE_FACILITY: 2500,
            # Special
            ItemMode.ONSEN: 3000,
            ItemMode.PACHINKO: 2500
        }
        return costs.get(tool, 0)
    
    def _update_simulation(self):
        """Update simulation with staggered updates to prevent freezing"""
        self.simulation_tick += 1

        # Update train system every frame for smooth movement
        cell_types = {
            'STATION': CellType.STATION,
            'RAIL': CellType.RAIL
        }
        self.train_system.update_network(self.grid, cell_types)
        self.train_system.update()

        # Update traffic system every frame
        if hasattr(self, 'traffic_system'):
            self.traffic_system.update(self.grid, self.sim_data)

        # Stagger heavy operations across different frames
        tick_mod = self.simulation_tick % 60
        
        # Light operations - more frequent
        if tick_mod % 15 == 0:  # Every 0.25 second
            self._update_rci_zones()
            self._calculate_population()
            self._calculate_quality_metrics()
        
        if tick_mod % 15 == 5:  # Offset by 5 frames
            self._update_employment()
            self._update_rci_demand()
        
        # Medium operations - less frequent
        if tick_mod == 3:  # Pollution
            self._spread_pollution()
            self._spread_water_pollution()
        
        if tick_mod == 8:  # Crime
            self._update_crime_and_fire_risk()
        
        if tick_mod == 13:  # Economy
            self._update_economic_factors()
        
        # Heavy operations - spread out evenly (4 chunks for 100x100)
        if tick_mod == 18:  # Land value part 1
            self._calculate_land_value_partial(0, MAP_SIZE // 4)
        
        if tick_mod == 23:  # Land value part 2
            self._calculate_land_value_partial(MAP_SIZE // 4, MAP_SIZE // 2)
        
        if tick_mod == 28:  # Land value part 3
            self._calculate_land_value_partial(MAP_SIZE // 2, MAP_SIZE * 3 // 4)
        
        if tick_mod == 33:  # Land value part 4
            self._calculate_land_value_partial(MAP_SIZE * 3 // 4, MAP_SIZE)
        
        if tick_mod == 38:  # Power
            self._spread_power()
        
        if tick_mod == 43:  # Water
            self._spread_water()
        
        # Traffic calculation - split into smaller chunks
        if tick_mod == 48:  # Traffic part 1
            self._calculate_traffic_partial(0, MAP_SIZE // 4)
        
        if tick_mod == 50:  # Traffic part 2
            self._calculate_traffic_partial(MAP_SIZE // 4, MAP_SIZE // 2)
        
        if tick_mod == 52:  # Traffic part 3
            self._calculate_traffic_partial(MAP_SIZE // 2, MAP_SIZE * 3 // 4)
        
        if tick_mod == 54:  # Traffic part 4
            self._calculate_traffic_partial(MAP_SIZE * 3 // 4, MAP_SIZE)

        # Update economic system (every 5 frames)
        if hasattr(self, 'economic_system') and tick_mod % 5 == 0:
            buildings = self._count_buildings_by_type()
            # Calculate current month (year * 12 + month)
            current_month = (self.year - 2025) * 12 + self.month
            self.economic_system.update(
                self.total_population,
                buildings,
                self.total_employment,
                current_month
            )
            # Sync data back to existing variables
            self._sync_economic_data()

        # Update disaster system (only if active disasters or periodically)
        if hasattr(self, 'disaster_system'):
            if len(self.disaster_system.active_disasters) > 0:
                # Update every frame if there are active disasters
                self.disaster_system.update(self.grid, self.sim_data, self.total_population, self.funds)
            elif tick_mod == 45:  # Check for new disasters periodically
                self.disaster_system.update(self.grid, self.sim_data, self.total_population, self.funds)

        # Update UI data periodically (every 1 second)
        if tick_mod == 0 or tick_mod == 30:  # Every 0.5 and 1 second
            self.ui_data_needs_update = True

        # Memory cleanup (every 1 minute)
        if tick_mod == 10:
            self._cleanup_systems()

    def _cleanup_systems(self):
        """Periodic memory cleanup to prevent memory leaks"""
        # Clean up UI graph data
        if hasattr(self, 'ui_system'):
            for graph in self.ui_system.graphs.values():
                if len(graph.values) > graph.max_values:
                    graph.values = graph.values[-graph.max_values:]

        # Clean up economic system history
        if hasattr(self, 'economic_system'):
            if len(self.economic_system.budget_history) > 1000:
                self.economic_system.budget_history = self.economic_system.budget_history[-500:]

        # Clean up disaster history
        if hasattr(self, 'disaster_system'):
            if len(self.disaster_system.disaster_history) > 100:
                self.disaster_system.disaster_history = self.disaster_system.disaster_history[-50:]

    def _spread_water(self):
        """Spread water from water plants and pumps through roads and buildings"""
        # Reset water supply
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                self.sim_data[y][x].water = False
        
        # Find water sources and mark them
        water_sources = []
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                if self.grid[y][x] in [CellType.WATER_PLANT, CellType.PUMP]:
                    water_sources.append((x, y))
                    self.sim_data[y][x].water = True
        
        # BFS from each water source with distance tracking for roads only
        from collections import deque
        visited = set()
        queue = deque()
        
        # Initialize queue with all water sources
        for x, y in water_sources:
            queue.append((x, y, 0, 'source'))  # x, y, road_distance, last_type
            visited.add((x, y))
        
        # Spread water with distance limit only for roads
        while queue:
            x, y, road_distance, last_type = queue.popleft()
            
            # Check adjacent cells
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE and (nx, ny) not in visited:
                    cell_type = self.grid[ny][nx]
                    
                    # Roads conduct water without limit (water pipes inside roads)
                    if cell_type == CellType.ROAD:
                        self.sim_data[ny][nx].water = True
                        visited.add((nx, ny))
                        queue.append((nx, ny, 0, 'road'))  # No distance limit for roads with water
                    
                    # Buildings conduct water without limit
                    elif cell_type in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL,
                                      CellType.AGRICULTURAL, CellType.POLICE, CellType.FIRE, 
                                      CellType.HOSPITAL, CellType.SCHOOL, CellType.UNIVERSITY,
                                      CellType.SEWAGE_PLANT, CellType.WATER_PLANT, CellType.LIBRARY,
                                      CellType.MILITARY, CellType.PRISON, CellType.SHRINE,
                                      CellType.HELIPORT, CellType.SEAPORT, CellType.INCINERATOR,
                                      CellType.WASTE_FACILITY, CellType.ONSEN, CellType.PACHINKO]:
                        # Buildings get water from any adjacent water-supplied cell
                        if self.sim_data[y][x].water:
                            self.sim_data[ny][nx].water = True
                            visited.add((nx, ny))
                            queue.append((nx, ny, 0, 'building'))  # Reset road distance
    
    def _is_coastline_tile(self, x: int, y: int) -> bool:
        """Check if a tile is on the coastline"""
        return (x, y) in self.coastline_map
    
    def _spread_power(self):
        """Spread power from power plants through infrastructure and buildings"""
        # Reset power grid
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                self.sim_data[y][x].power = False
        
        # Find power sources and mark them
        power_sources = []
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                if self.grid[y][x] in [CellType.COAL_PLANT, CellType.OIL_PLANT, CellType.NUCLEAR_PLANT, 
                                      CellType.GAS_PLANT, CellType.WIND_PLANT, CellType.SOLAR_PLANT]:
                    power_sources.append((x, y))
                    self.sim_data[y][x].power = True
        
        # BFS from each power source with distance tracking for roads only
        from collections import deque
        visited = set()
        queue = deque()
        
        # Initialize queue with all power sources
        for x, y in power_sources:
            queue.append((x, y, 0, 'source'))  # x, y, road_distance, last_type
            visited.add((x, y))
        
        # Spread power with distance limit only for roads
        while queue:
            x, y, road_distance, last_type = queue.popleft()
            
            # Check adjacent cells
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE and (nx, ny) not in visited:
                    cell_type = self.grid[ny][nx]
                    
                    # Wires conduct power without limit
                    if cell_type == CellType.WIRE:
                        self.sim_data[ny][nx].power = True
                        visited.add((nx, ny))
                        queue.append((nx, ny, 0, 'wire'))  # Reset road distance
                    
                    # Rails conduct power without limit
                    elif cell_type == CellType.RAIL:
                        self.sim_data[ny][nx].power = True
                        visited.add((nx, ny))
                        queue.append((nx, ny, 0, 'rail'))  # Reset road distance
                    
                    # Roads conduct power up to 3 cells from source/wire/rail/building
                    elif cell_type == CellType.ROAD:
                        if road_distance < 3:
                            self.sim_data[ny][nx].power = True
                            visited.add((nx, ny))
                            queue.append((nx, ny, road_distance + 1, 'road'))
                    
                    # Buildings conduct power without limit
                    elif cell_type in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL,
                                      CellType.AGRICULTURAL, CellType.POLICE, CellType.FIRE, 
                                      CellType.HOSPITAL, CellType.SCHOOL, CellType.UNIVERSITY,
                                      CellType.SEWAGE_PLANT, CellType.WATER_PLANT, CellType.LIBRARY,
                                      CellType.MILITARY, CellType.PRISON, CellType.SHRINE,
                                      CellType.HELIPORT, CellType.SEAPORT, CellType.INCINERATOR,
                                      CellType.WASTE_FACILITY, CellType.ONSEN, CellType.PACHINKO]:
                        # Buildings get power from any adjacent powered cell
                        if self.sim_data[y][x].power:
                            self.sim_data[ny][nx].power = True
                            visited.add((nx, ny))
                            queue.append((nx, ny, 0, 'building'))  # Reset road distance
    
    def _update_rci_zones(self):
        """Update RCIA zone growth for 1x1 cells"""
        # First, grow the zones normally
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                cell_type = self.grid[y][x]
                if cell_type in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL]:
                    # Update construction timer
                    data = self.sim_data[y][x]
                    if data.under_construction > 0:
                        data.under_construction -= 1
                        continue  # Skip growth while under construction
                    
                    # Skip individual growth for merged buildings
                    if data.merged_size > 1:
                        continue  # Merged buildings don't grow individually
                    
                    # Process each RCI cell individually (only 1x1 buildings)
                    self._update_zone_growth_1x1(x, y, cell_type)
                elif cell_type == CellType.AGRICULTURAL:
                    # Process agricultural zones
                    self._update_agricultural_growth(x, y)
        
        # Old merging system disabled - now using auto-upgrade during growth
        # check_interval = 30 if self.dev_mode else 60  # Every 0.5s in dev mode, 1s normally
        # if pyxel.frame_count % check_interval == 0:
        #     self._check_rci_merging()
    
    def _update_zone_growth_1x1(self, x: int, y: int, zone_type: CellType):
        """Update growth for a single 1x1 RCI cell"""
        data = self.sim_data[y][x]
        
        # No growth without power
        if not data.power:
            data.population = max(0, data.population - 2)
            return
        
        # No growth without road access within 3 cells
        if self._count_nearby_type(x, y, CellType.ROAD, 3) == 0:
            data.population = max(0, data.population - 1)  # Slower decline than no power
            return
        
        # Get demand for this zone type
        demand = 0
        if zone_type == CellType.RESIDENTIAL:
            demand = self.res_demand
        elif zone_type == CellType.COMMERCIAL:
            demand = self.com_demand
        elif zone_type == CellType.INDUSTRIAL:
            demand = self.ind_demand
        
        # Calculate growth probability
        base_chance = 0.3 if demand > 20 else 0.2 if demand > 0 else 0.05
        land_value_factor = max(0.3, data.land_value / 255.0)
        pollution_factor = max(0.2, 1.0 - (data.pollution / 512.0))
        
        # Traffic factor
        traffic_factor = 1.0
        if zone_type == CellType.COMMERCIAL and data.traffic > 50:
            traffic_factor = max(0.5, 1.0 - (data.traffic / 200.0))
        elif zone_type in [CellType.RESIDENTIAL, CellType.INDUSTRIAL] and data.traffic > 75:
            traffic_factor = max(0.7, 1.0 - (data.traffic / 250.0))
        
        # Adjacency bonus for same type (future merging preparation)
        adjacency_bonus = 1.0
        same_type_neighbors = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE:
                if self.grid[ny][nx] == zone_type:
                    same_type_neighbors += 1
        adjacency_bonus = 1.0 + (same_type_neighbors * 0.15)
        
        # Mixed development bonus
        if zone_type == CellType.RESIDENTIAL:
            nearby_commercial = self._count_nearby_type(x, y, CellType.COMMERCIAL, 3)
            nearby_parks = self._count_nearby_type(x, y, CellType.PARK, 2)
            adjacency_bonus += (nearby_commercial * 0.1) + (nearby_parks * 0.2)
        elif zone_type == CellType.COMMERCIAL:
            nearby_residential = self._count_nearby_type(x, y, CellType.RESIDENTIAL, 4)
            adjacency_bonus += (nearby_residential * 0.15)
        
        growth_chance = base_chance * land_value_factor * pollution_factor * traffic_factor * adjacency_bonus
        
        if random.random() < growth_chance:
            # Increase population for 1x1 cell
            max_pop = 250  # Max population per 1x1 cell (increased for higher density buildings)
            if data.population < max_pop:
                growth_amount = random.randint(5, 15)
                data.population = min(data.population + growth_amount, max_pop)
                
                # Update density based on population - more gradual progression
                old_density = data.density
                if data.population >= 200:    # Very high population for max density
                    new_density = 4
                elif data.population >= 140:  # High population for high density
                    new_density = 3
                elif data.population >= 80:   # Medium population for medium density
                    new_density = 2
                elif data.population >= 1:    # Any population means developed (low density)
                    new_density = 1
                    # Assign random variant for low density (only when first developing)
                    if data.building_variant == 0:
                        data.building_variant = random.randint(1, 3)
                
                # Check for auto-upgrade to larger building when reaching HIGH density only
                # Low density (1) and medium density (2) stay as 1x1 buildings
                if new_density >= 3 and data.merged_size == 1:  # High density only (3+)
                    self._try_auto_upgrade_building(x, y, zone_type)
                else:
                    new_density = 0  # No population = empty zone
                
                # Set construction timer only for new construction (0 -> 1)
                if new_density == 1 and old_density == 0:
                    data.under_construction = 60  # 1 second construction time for new buildings only
                data.density = new_density
                
                # Generate tax revenue
                if zone_type == CellType.RESIDENTIAL:
                    self.funds += growth_amount // 20
                elif zone_type == CellType.COMMERCIAL:
                    self.funds += growth_amount // 10
                elif zone_type == CellType.INDUSTRIAL:
                    self.funds += growth_amount // 15
    
    def _check_rci_merging(self):
        """Check for opportunities to merge adjacent RCI zones into larger buildings"""
        # Track already processed cells to avoid double-checking
        processed = set()
        merge_count = 0
        checked_count = 0
        potential_2x2 = 0
        potential_3x3 = 0
        
        for y in range(MAP_SIZE - 2):  # -2 to allow for 3x3 checks
            for x in range(MAP_SIZE - 2):  # -2 to allow for 3x3 checks
                if (x, y) in processed:
                    continue
                
                cell_type = self.grid[y][x]
                if cell_type not in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL]:
                    continue
                
                checked_count += 1
                
                # Skip if already merged
                if self.sim_data[y][x].merged_size > 1:
                    continue
                
                # Try 3x3 merge first (highest priority)
                if self._can_merge_3x3(x, y, cell_type):
                    self._merge_rci_3x3(x, y, cell_type)
                    merge_count += 1
                    potential_3x3 += 1
                    print(f"✅ 3x3 merge: {cell_type.name} at ({x},{y})")
                    # Mark all 9 cells as processed
                    for dy in range(3):
                        for dx in range(3):
                            processed.add((x + dx, y + dy))
                # Try 2x2 merge
                elif self._can_merge_2x2(x, y, cell_type):
                    self._merge_rci_2x2(x, y, cell_type)
                    merge_count += 1
                    potential_2x2 += 1
                    print(f"✅ 2x2 merge: {cell_type.name} at ({x},{y})")
                    # Mark all 4 cells as processed
                    for dy in range(2):
                        for dx in range(2):
                            processed.add((x + dx, y + dy))
                else:
                    # Debug why merge failed
                    if cell_type == CellType.RESIDENTIAL and x < 5 and y < 5:  # Only debug first few to avoid spam
                        data = self.sim_data[y][x]
                        if data.population > 0:
                            print(f"🔍 No merge for {cell_type.name} at ({x},{y}): pop={data.population}, density={data.density}, power={data.power}, land_value={data.land_value}")
        
        # Debug output every 10 seconds
        if pyxel.frame_count % 600 == 0:  # Every 10 seconds
            print(f"RCI Merge Status: checked={checked_count}, merged={merge_count}, 2x2={potential_2x2}, 3x3={potential_3x3}")
    
    def _can_merge_2x2(self, x: int, y: int, zone_type: CellType) -> bool:
        """Check if a 2x2 area can be merged into a medium-density building"""
        if x + 1 >= MAP_SIZE or y + 1 >= MAP_SIZE:
            return False
        
        # Check all 4 cells
        for dy in range(2):
            for dx in range(2):
                cx, cy = x + dx, y + dy
                # Must be same zone type
                if self.grid[cy][cx] != zone_type:
                    return False
                data = self.sim_data[cy][cx]
                # Must not be already merged
                if data.merged_size > 1:
                    return False
                # Must have any population (very relaxed)
                if data.population <= 0:
                    return False
                # Power requirement relaxed for dev mode
                if not self.dev_mode and not data.power:
                    return False
                # Very relaxed land value requirement (or dev mode)
                if not self.dev_mode and data.land_value < 10:  # Dev mode bypasses land value
                    return False
        
        return True
    
    def _can_merge_3x3(self, x: int, y: int, zone_type: CellType) -> bool:
        """Check if a 3x3 area can be merged into a high-density building"""
        if x + 2 >= MAP_SIZE or y + 2 >= MAP_SIZE:
            return False
        
        # Check all 9 cells
        for dy in range(3):
            for dx in range(3):
                cx, cy = x + dx, y + dy
                # Must be same zone type
                if self.grid[cy][cx] != zone_type:
                    return False
                data = self.sim_data[cy][cx]
                # Must not be already merged
                if data.merged_size > 1:
                    return False
                # Must have any population (very relaxed)
                if data.population <= 0:
                    return False
                # Power requirement relaxed for dev mode
                if not self.dev_mode and not data.power:
                    return False
                # Very relaxed land value requirement (or dev mode)
                if not self.dev_mode and data.land_value < 20:  # Dev mode bypasses land value
                    return False
        
        return True
    
    def _merge_rci_2x2(self, x: int, y: int, zone_type: CellType):
        """Merge a 2x2 area into a medium-density building"""
        # Calculate total population
        total_pop = 0
        for dy in range(2):
            for dx in range(2):
                total_pop += self.sim_data[y + dy][x + dx].population
        
        # Assign a unique building ID
        building_id = self.next_building_id
        self.next_building_id += 1
        
        # Update all cells to be part of the merged building
        for dy in range(2):
            for dx in range(2):
                cx, cy = x + dx, y + dy
                data = self.sim_data[cy][cx]
                data.merged_size = 2
                data.merged_top_left = (x, y)
                data.building_id = building_id
                data.density = 3  # Medium-high density
                # Distribute population
                data.population = total_pop // 4
        
        # Add construction animation
        self.sim_data[y][x].under_construction = 30  # 0.5 seconds
    
    def _merge_rci_3x3(self, x: int, y: int, zone_type: CellType):
        """Merge a 3x3 area into a high-density building"""
        # Calculate total population
        total_pop = 0
        for dy in range(3):
            for dx in range(3):
                total_pop += self.sim_data[y + dy][x + dx].population
        
        # Assign a unique building ID
        building_id = self.next_building_id
        self.next_building_id += 1
        
        # Update all cells to be part of the merged building
        for dy in range(3):
            for dx in range(3):
                cx, cy = x + dx, y + dy
                data = self.sim_data[cy][cx]
                data.merged_size = 3
                data.merged_top_left = (x, y)
                data.building_id = building_id
                data.density = 4  # High density
                # Distribute population
                data.population = total_pop // 9
        
        # Add construction animation
        self.sim_data[y][x].under_construction = 60  # 1 second
    
    def _try_auto_upgrade_building(self, x: int, y: int, zone_type: CellType):
        """Try to automatically upgrade a 1x1 building to larger size based on surrounding zones"""
        
        # First try 3x3 upgrade if possible
        if self._can_upgrade_to_3x3(x, y, zone_type):
            self._upgrade_to_3x3(x, y, zone_type)
            print(f"🏗️ Auto-upgraded to 3x3: {zone_type.name} at ({x},{y})")
        # Otherwise try 2x2 upgrade
        elif self._can_upgrade_to_2x2(x, y, zone_type):
            self._upgrade_to_2x2(x, y, zone_type)
            print(f"🏗️ Auto-upgraded to 2x2: {zone_type.name} at ({x},{y})")
    
    def _can_upgrade_to_2x2(self, x: int, y: int, zone_type: CellType) -> bool:
        """Check if we can upgrade to 2x2 building"""
        # Check bounds
        if x + 1 >= MAP_SIZE or y + 1 >= MAP_SIZE:
            return False
        
        # Check all 4 cells
        for dy in range(2):
            for dx in range(2):
                cx, cy = x + dx, y + dy
                if self.grid[cy][cx] != zone_type:
                    return False
                data = self.sim_data[cy][cx]
                # Must not be already merged
                if data.merged_size > 1:
                    return False
                # Must have HIGH population and development - no more low/medium density merging
                min_pop = 100 if self.dev_mode else 120  # Higher requirements
                min_density = 3 if self.dev_mode else 3   # Require high density (3+)
                if data.population < min_pop or data.density < min_density:
                    return False
        
        return True
    
    def _can_upgrade_to_3x3(self, x: int, y: int, zone_type: CellType) -> bool:
        """Check if we can upgrade to 3x3 building"""
        # Check bounds  
        if x + 2 >= MAP_SIZE or y + 2 >= MAP_SIZE:
            return False
        
        # Check all 9 cells
        for dy in range(3):
            for dx in range(3):
                cx, cy = x + dx, y + dy
                if self.grid[cy][cx] != zone_type:
                    return False
                data = self.sim_data[cy][cx]
                # Must not be already merged
                if data.merged_size > 1:
                    return False
                # Must have VERY HIGH population and development for 3x3
                min_pop = 150 if self.dev_mode else 180  # Very high requirements for 3x3
                min_density = 4 if self.dev_mode else 4   # Require max density (4)
                if data.population < min_pop or data.density < min_density:
                    return False
        
        return True
    
    def _upgrade_to_2x2(self, x: int, y: int, zone_type: CellType):
        """Upgrade 2x2 area to medium-density building"""
        # Calculate total population
        total_pop = 0
        for dy in range(2):
            for dx in range(2):
                total_pop += self.sim_data[y + dy][x + dx].population
        
        # Assign building ID
        building_id = self.next_building_id
        self.next_building_id += 1
        
        # Update all cells
        for dy in range(2):
            for dx in range(2):
                cx, cy = x + dx, y + dy
                data = self.sim_data[cy][cx]
                data.merged_size = 2
                data.merged_top_left = (x, y)
                data.building_id = building_id
                data.density = 3  # Medium-high density
                data.population = total_pop // 4  # Distribute population
        
        # Add construction animation
        self.sim_data[y][x].under_construction = 30
    
    def _upgrade_to_3x3(self, x: int, y: int, zone_type: CellType):
        """Upgrade 3x3 area to high-density building"""
        # Calculate total population
        total_pop = 0
        for dy in range(3):
            for dx in range(3):
                total_pop += self.sim_data[y + dy][x + dx].population
        
        # Assign building ID
        building_id = self.next_building_id
        self.next_building_id += 1
        
        # Update all cells
        for dy in range(3):
            for dx in range(3):
                cx, cy = x + dx, y + dy
                data = self.sim_data[cy][cx]
                data.merged_size = 3
                data.merged_top_left = (x, y)
                data.building_id = building_id
                data.density = 4  # High density
                data.population = total_pop // 9  # Distribute population
        
        # Add construction animation
        self.sim_data[y][x].under_construction = 60
    
    def _update_agricultural_growth(self, x: int, y: int):
        """Update growth for agricultural zones (farms)"""
        data = self.sim_data[y][x]
        
        # Agricultural zones don't need power but benefit from it
        power_bonus = 1.2 if data.power else 1.0
        
        # Agricultural zones need water
        if not data.water:
            data.population = max(0, data.population - 1)
            return
        
        # Need road access within 5 cells (farms can be further from roads)
        if self._count_nearby_type(x, y, CellType.ROAD, 5) == 0:
            data.population = max(0, data.population - 1)
            return
        
        # Get agricultural demand
        demand = self.agr_demand
        
        # Calculate growth probability
        base_chance = 0.25 if demand > 20 else 0.15 if demand > 0 else 0.05
        
        # Agricultural zones prefer low pollution areas
        pollution_factor = max(0.1, 1.0 - (data.pollution / 128.0))  # More sensitive to pollution
        
        # Agricultural zones prefer areas with good land value but not too high
        land_value_factor = 0.5
        if 50 < data.land_value < 150:
            land_value_factor = 1.0  # Optimal land value range
        elif data.land_value > 200:
            land_value_factor = 0.3  # Too expensive land is not good for farming
        
        # Adjacency bonus for other agricultural zones
        adjacency_bonus = 1.0
        agr_neighbors = self._count_nearby_type(x, y, CellType.AGRICULTURAL, 2)
        adjacency_bonus = 1.0 + (agr_neighbors * 0.2)
        
        # Distance from industrial zones (farms don't like industrial neighbors)
        industrial_penalty = 1.0
        nearby_industrial = self._count_nearby_type(x, y, CellType.INDUSTRIAL, 3)
        if nearby_industrial > 0:
            industrial_penalty = max(0.3, 1.0 - (nearby_industrial * 0.2))
        
        growth_chance = base_chance * land_value_factor * pollution_factor * power_bonus * adjacency_bonus * industrial_penalty
        
        if random.random() < growth_chance:
            # Agricultural zones have lower population but produce food
            max_pop = 50  # Lower population for farms
            if data.population < max_pop:
                growth_amount = random.randint(2, 8)
                data.population = min(data.population + growth_amount, max_pop)
                
                # Update density based on population (farm development stages)
                if data.population >= 40:
                    data.density = 4  # Large farm/silo
                elif data.population >= 30:
                    data.density = 3  # Orchard
                elif data.population >= 15:
                    data.density = 2  # Field
                elif data.population >= 1:
                    data.density = 1  # Small farm
                else:
                    data.density = 0  # Empty agricultural zone
                
                # Generate tax revenue (lower than other zones)
                self.funds += growth_amount // 30
    
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
        has_water = False
        
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
                    if self.sim_data[y][x].water:
                        has_water = True
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
        
        # No growth without water supply
        if not has_water:
            new_population = max(0, total_population - 3)
            self._set_building_population(building_id, new_population)
            return
        
        # No growth without road access within 3 cells from center
        if self._count_nearby_type(center_x, center_y, CellType.ROAD, 3) == 0:
            new_population = max(0, total_population - 2)  # Slower decline than no power/water
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
        
        # Much higher growth probability for faster gameplay
        base_chance = 0.4 if demand > 20 else 0.25 if demand > 0 else 0.1
        land_value_factor = max(0.3, avg_land_value / 255.0)
        pollution_factor = max(0.2, 1.0 - (avg_pollution / 512.0))  # Less sensitive to pollution
        
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
            max_pop = 3600 if zone_type == CellType.RESIDENTIAL else 2400
            if total_population < max_pop:
                # Much faster growth based on demand
                base_growth = 50 if demand > 50 else 30
                growth_amount = random.randint(base_growth, base_growth * 3)
                new_population = min(total_population + growth_amount, max_pop)
                self._set_building_population(building_id, new_population)
                
                # Generate tax revenue from growth
                if zone_type == CellType.RESIDENTIAL:
                    self.funds += growth_amount // 10
                elif zone_type == CellType.COMMERCIAL:
                    self.funds += growth_amount // 5
                elif zone_type == CellType.INDUSTRIAL:
                    self.funds += growth_amount // 8
    
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
            if pop >= 150:
                self.sim_data[y][x].density = 4
            elif pop >= 100:
                self.sim_data[y][x].density = 3
            elif pop >= 50:
                self.sim_data[y][x].density = 2
            elif pop >= 1:  # Any population means developed
                self.sim_data[y][x].density = 1
            else:
                self.sim_data[y][x].density = 0  # No population = empty zone

    def _update_zone_growth(self, x: int, y: int, zone_type: CellType):
        """Update growth for a specific zone with improved SimCity mechanics"""
        data = self.sim_data[y][x]
        
        # No growth without power, but slower decline
        if not data.power:
            data.population = max(0, data.population - 2)
            return
        
        # No growth without water supply - critical for city development
        if not data.water:
            data.population = max(0, data.population - 1)
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
                
                # Update density based on population
                old_density = data.density
                if data.population >= 300:
                    new_density = 4
                elif data.population >= 150:
                    new_density = 3
                elif data.population >= 70:
                    new_density = 2
                elif data.population >= 1:  # Any population means developed
                    new_density = 1
                    # Assign random variant for low density (only when first developing)
                    if data.building_variant == 0:
                        data.building_variant = random.randint(1, 3)
                else:
                    new_density = 0  # No population = empty zone
                
                # Set construction timer only for new construction (0 -> 1)
                if new_density == 1 and old_density == 0:
                    data.under_construction = 60  # 1 second construction time for new buildings only
                data.density = new_density
    
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
        """Optimized pollution spread calculation for 100x100 map"""
        # Create a temporary pollution map for diffusion (use list comprehension for speed)
        new_pollution = [[0] * MAP_SIZE for _ in range(MAP_SIZE)]
        
        # First pass: Add pollution sources and apply decay
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                current = self.sim_data[y][x].pollution
                
                # Natural decay - stronger decay to prevent infinite spread
                decayed = int(current * 0.7)  # 30% decay per tick
                
                # Add pollution sources (reduced amounts)
                if self.grid[y][x] == CellType.INDUSTRIAL:
                    pollution_amount = 8 + self.sim_data[y][x].density * 3
                    pollution_amount += self.sim_data[y][x].population // 100
                    new_pollution[y][x] = min(255, decayed + pollution_amount)
                elif self.grid[y][x] == CellType.COAL_PLANT:
                    new_pollution[y][x] = min(255, decayed + 40)  # Reduced from 80
                elif self.grid[y][x] == CellType.OIL_PLANT:
                    new_pollution[y][x] = min(255, decayed + 25)  # Reduced from 50
                elif self.grid[y][x] == CellType.NUCLEAR_PLANT:
                    new_pollution[y][x] = min(255, decayed + 3)  # Reduced from 5
                elif self.grid[y][x] == CellType.GAS_PLANT:
                    new_pollution[y][x] = min(255, decayed + 15)  # Cleaner than coal/oil
                elif self.grid[y][x] == CellType.INCINERATOR:
                    new_pollution[y][x] = min(255, decayed + 20)  # Moderate pollution
                elif self.grid[y][x] == CellType.WASTE_FACILITY:
                    new_pollution[y][x] = min(255, decayed + 10)  # Lower pollution
                elif self.grid[y][x] == CellType.ROAD and self.sim_data[y][x].traffic > 50:
                    new_pollution[y][x] = min(255, decayed + max(1, self.sim_data[y][x].traffic // 40))
                elif self.grid[y][x] == CellType.COMMERCIAL and self.sim_data[y][x].density >= 3:
                    new_pollution[y][x] = min(255, decayed + 2)  # Reduced from 5
                else:
                    new_pollution[y][x] = decayed
                
                # Parks and water absorb pollution
                if self.grid[y][x] == CellType.PARK:
                    new_pollution[y][x] = max(0, new_pollution[y][x] - 10)
                elif self.grid[y][x] == CellType.WATER:
                    new_pollution[y][x] = max(0, new_pollution[y][x] - 20)
        
        # Second pass: Limited diffusion (much weaker)
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                if new_pollution[y][x] > 20:  # Only diffuse if pollution is significant
                    # Weak diffusion to adjacent cells
                    diffuse = new_pollution[y][x] // 20  # Only 5% diffusion
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE:
                            # Don't spread to water or parks
                            if self.grid[ny][nx] not in [CellType.WATER, CellType.PARK]:
                                new_pollution[ny][nx] = min(255, new_pollution[ny][nx] + diffuse)
        
        # Apply the new pollution values
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                self.sim_data[y][x].pollution = new_pollution[y][x]
    
    def _spread_water_pollution(self):
        """Water pollution spreading algorithm"""
        # Create temporary water pollution map
        new_water_pollution = [[0] * MAP_SIZE for _ in range(MAP_SIZE)]
        
        # First pass: Add water pollution sources
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                current = self.sim_data[y][x].water_pollution
                
                # Natural decay in water
                decayed = int(current * 0.85)  # 15% decay per tick (slower than air)
                
                # Industrial zones pollute water heavily
                if self.grid[y][x] == CellType.INDUSTRIAL:
                    pollution_amount = 15 + self.sim_data[y][x].density * 5
                    new_water_pollution[y][x] = min(255, decayed + pollution_amount)
                
                # High density residential pollutes water (sewage)
                elif self.grid[y][x] == CellType.RESIDENTIAL:
                    if self.sim_data[y][x].density >= 3:
                        pollution_amount = 3 + self.sim_data[y][x].density * 2
                        pollution_amount += self.sim_data[y][x].population // 200
                        new_water_pollution[y][x] = min(255, decayed + pollution_amount)
                    elif self.sim_data[y][x].density >= 2:
                        pollution_amount = 2 + self.sim_data[y][x].population // 500
                        new_water_pollution[y][x] = min(255, decayed + pollution_amount)
                    else:
                        new_water_pollution[y][x] = decayed
                
                # Waste facilities pollute water
                elif self.grid[y][x] == CellType.WASTE_FACILITY:
                    new_water_pollution[y][x] = min(255, decayed + 25)
                elif self.grid[y][x] == CellType.INCINERATOR:
                    new_water_pollution[y][x] = min(255, decayed + 10)
                
                # Coal and oil plants pollute water (cooling water discharge)
                elif self.grid[y][x] == CellType.COAL_PLANT:
                    new_water_pollution[y][x] = min(255, decayed + 20)
                elif self.grid[y][x] == CellType.OIL_PLANT:
                    new_water_pollution[y][x] = min(255, decayed + 15)
                
                # Agricultural zones can pollute water (fertilizer runoff)
                elif self.grid[y][x] == CellType.AGRICULTURAL:
                    if self.sim_data[y][x].density >= 2:
                        new_water_pollution[y][x] = min(255, decayed + 5)
                    else:
                        new_water_pollution[y][x] = decayed
                else:
                    new_water_pollution[y][x] = decayed
                
                # Sewage treatment plants clean water pollution
                if self.grid[y][x] == CellType.SEWAGE_PLANT:
                    # Clean surrounding water in 5x5 area
                    for dy in range(-2, 3):
                        for dx in range(-2, 3):
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < MAP_SIZE and 0 <= nx < MAP_SIZE:
                                reduction = 30 - abs(dx) * 5 - abs(dy) * 5
                                new_water_pollution[ny][nx] = max(0, new_water_pollution[ny][nx] - reduction)
                
                # Water tiles help dilute pollution
                if self.grid[y][x] == CellType.WATER:
                    new_water_pollution[y][x] = max(0, new_water_pollution[y][x] - 5)
        
        # Second pass: Water pollution spreads through water network and adjacent cells
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                if new_water_pollution[y][x] > 10:  # Only spread if significant
                    # Stronger spread through water connections
                    if self.sim_data[y][x].water:
                        spread_amount = new_water_pollution[y][x] // 10  # 10% spread through water network
                        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE:
                                if self.sim_data[ny][nx].water:  # Spreads through connected water
                                    new_water_pollution[ny][nx] = min(255, 
                                        new_water_pollution[ny][nx] + spread_amount)
                    
                    # Weak spread to adjacent land
                    else:
                        spread_amount = new_water_pollution[y][x] // 30  # 3% spread to land
                        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE:
                                if self.grid[ny][nx] != CellType.WATER:
                                    new_water_pollution[ny][nx] = min(255, 
                                        new_water_pollution[ny][nx] + spread_amount)
        
        # Apply the new water pollution values
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                self.sim_data[y][x].water_pollution = new_water_pollution[y][x]
    
    def _calculate_land_value_partial(self, start_y: int, end_y: int):
        """Calculate land value for a portion of the map to reduce lag"""
        for y in range(start_y, end_y):
            for x in range(MAP_SIZE):
                # Base land value (higher near water and center)
                center_x, center_y = MAP_SIZE // 2, MAP_SIZE // 2
                distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                base_value = max(80, 220 - int(distance * 3))
                
                # Water proximity bonus
                water_bonus = 0
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE:
                            if self.grid[ny][nx] == CellType.WATER:
                                water_bonus += max(0, 20 - abs(dx) * 5 - abs(dy) * 5)
                
                # Pollution reduces land value (less impact)
                pollution_penalty = self.sim_data[y][x].pollution // 2
                
                # Crime reduces land value
                crime_penalty = getattr(self.sim_data[y][x], 'crime', 0) // 3
                
                # Proximity bonuses - optimized with smaller radius
                proximity_bonus = 0
                for dx in range(-3, 4, 2):  # Check every other cell
                    for dy in range(-3, 4, 2):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE:
                            dist = abs(dx) + abs(dy)
                            if self.grid[ny][nx] == CellType.PARK:
                                proximity_bonus += max(0, 12 - dist * 2)
                            elif self.grid[ny][nx] == CellType.COMMERCIAL and self.sim_data[ny][nx].density >= 2:
                                proximity_bonus += max(0, 6 - dist)
                            elif self.grid[ny][nx] in [CellType.POLICE, CellType.SCHOOL, CellType.HOSPITAL]:
                                proximity_bonus += max(0, 8 - dist)
                
                # Traffic accessibility bonus (but not too much traffic)
                traffic_factor = 0
                if 10 < self.sim_data[y][x].traffic < 80:
                    traffic_factor = 10  # Good accessibility
                elif self.sim_data[y][x].traffic >= 80:
                    traffic_factor = -10  # Too congested
                
                # Calculate final land value
                land_value = base_value + water_bonus - pollution_penalty - crime_penalty + proximity_bonus + traffic_factor
                self.sim_data[y][x].land_value = max(0, min(255, land_value))
    
    def _calculate_land_value(self):
        """Full land value calculation - called during initialization"""
        self._calculate_land_value_partial(0, MAP_SIZE)
    
    def _calculate_traffic(self):
        """Full traffic calculation - called during initialization"""
        self._calculate_traffic_partial(0, MAP_SIZE)
    
    def _calculate_population(self):
        """Calculate total population"""
        self.total_population = 0
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                if self.grid[y][x] in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL]:
                    self.total_population += self.sim_data[y][x].population
    
    def _calculate_quality_metrics(self):
        """Calculate quality of life metrics"""
        if self.total_population == 0:
            self.living_standard = 50
            self.education_level = 30
            self.safety_level = 40
            return
        
        # Count service buildings
        police_count = sum(1 for y in range(MAP_SIZE) for x in range(MAP_SIZE) if self.grid[y][x] == CellType.POLICE)
        fire_count = sum(1 for y in range(MAP_SIZE) for x in range(MAP_SIZE) if self.grid[y][x] == CellType.FIRE)
        school_count = sum(1 for y in range(MAP_SIZE) for x in range(MAP_SIZE) if self.grid[y][x] == CellType.SCHOOL)
        university_count = sum(1 for y in range(MAP_SIZE) for x in range(MAP_SIZE) if self.grid[y][x] == CellType.UNIVERSITY)
        hospital_count = sum(1 for y in range(MAP_SIZE) for x in range(MAP_SIZE) if self.grid[y][x] == CellType.HOSPITAL)
        library_count = sum(1 for y in range(MAP_SIZE) for x in range(MAP_SIZE) if self.grid[y][x] == CellType.LIBRARY)
        
        # Calculate coverage (each building serves a certain population)
        police_coverage = min(100, (police_count * 5000 / self.total_population) * 100)
        fire_coverage = min(100, (fire_count * 5000 / self.total_population) * 100)
        school_coverage = min(100, (school_count * 2000 / self.total_population) * 100)
        university_coverage = min(100, (university_count * 5000 / self.total_population) * 100)
        hospital_coverage = min(100, (hospital_count * 3000 / self.total_population) * 100)
        
        # Safety level: based on police and fire coverage
        self.safety_level = int((police_coverage * 0.6 + fire_coverage * 0.4))
        
        # Education level: based on schools and universities
        self.education_level = int((school_coverage * 0.4 + university_coverage * 0.4 + library_count * 2))
        self.education_level = min(100, self.education_level)
        
        # Living standard: based on wealth, services, and pollution
        avg_land_value = sum(self.sim_data[y][x].land_value for y in range(MAP_SIZE) for x in range(MAP_SIZE)) / (MAP_SIZE * MAP_SIZE)
        avg_pollution = sum(self.sim_data[y][x].pollution for y in range(MAP_SIZE) for x in range(MAP_SIZE)) / (MAP_SIZE * MAP_SIZE)
        
        wealth_factor = avg_land_value / 255.0 * 100
        pollution_penalty = min(30, avg_pollution / 255.0 * 50)
        service_bonus = hospital_coverage * 0.2
        
        self.living_standard = int(wealth_factor * 0.5 + service_bonus - pollution_penalty + 25)
        self.living_standard = max(0, min(100, self.living_standard))
    
    def _update_rci_demand(self):
        """Update RCIA demand with sophisticated SimCity-style mechanics"""
        # Count population by zone type
        res_pop = sum(self.sim_data[y][x].population for y in range(MAP_SIZE) for x in range(MAP_SIZE) 
                     if self.grid[y][x] == CellType.RESIDENTIAL)
        com_pop = sum(self.sim_data[y][x].population for y in range(MAP_SIZE) for x in range(MAP_SIZE) 
                     if self.grid[y][x] == CellType.COMMERCIAL)
        ind_pop = sum(self.sim_data[y][x].population for y in range(MAP_SIZE) for x in range(MAP_SIZE) 
                     if self.grid[y][x] == CellType.INDUSTRIAL)
        agr_pop = sum(self.sim_data[y][x].population for y in range(MAP_SIZE) for x in range(MAP_SIZE) 
                     if self.grid[y][x] == CellType.AGRICULTURAL)
        
        # Employment ratios
        employment_ratio = (com_pop + ind_pop) / max(1, res_pop)
        commercial_ratio = com_pop / max(1, res_pop)
        industrial_ratio = ind_pop / max(1, res_pop)
        agricultural_ratio = agr_pop / max(1, res_pop)
        
        # Residential demand: need workers for commercial/industrial (REDUCED)
        if employment_ratio > 0.8:
            self.res_demand = min(60, 30 + (employment_ratio - 0.8) * 100)  # Reduced from 100/200
        else:
            self.res_demand = max(-30, -10 * (0.8 - employment_ratio))  # Reduced from -50/-20
        
        # Commercial demand: based on residential population and food supply (REDUCED)
        food_factor = min(1.3, 1.0 + agricultural_ratio * 0.3)  # Reduced agricultural boost
        if commercial_ratio < 0.15:  # Reduced target ratio from 0.2
            self.com_demand = min(50, int(20 * food_factor + (0.15 - commercial_ratio) * 150))  # Reduced from 100/300
        else:
            self.com_demand = max(-30, -50 * (commercial_ratio - 0.15))  # Reduced from -50/-100
        
        # Industrial demand: supports both residential and commercial (REDUCED)
        if industrial_ratio < 0.2:  # Reduced target ratio from 0.3
            self.ind_demand = min(40, 20 + (0.2 - industrial_ratio) * 100)  # Reduced from 100/200
        else:
            self.ind_demand = max(-30, -40 * (industrial_ratio - 0.2))  # Reduced from -50/-80
        
        # Agricultural demand: based on total population and food needs
        total_pop = res_pop + com_pop + ind_pop
        food_need_ratio = total_pop / max(1, agr_pop * 10)  # Each farm can support 10 people
        
        if food_need_ratio > 2.0:
            self.agr_demand = min(100, 60 + (food_need_ratio - 2.0) * 20)
        elif food_need_ratio > 1.0:
            self.agr_demand = 30 + int((food_need_ratio - 1.0) * 30)
        else:
            self.agr_demand = max(-30, int((food_need_ratio - 1.0) * 50))
        
        # Tax effects
        tax_factor = 1.0 - (self.tax_rate / 20.0)  # Lower taxes increase demand
        self.res_demand = int(self.res_demand * tax_factor)
        self.com_demand = int(self.com_demand * tax_factor)
        self.ind_demand = int(self.ind_demand * tax_factor)
        self.agr_demand = int(self.agr_demand * tax_factor)
    
    def _calculate_traffic_partial(self, start_y: int, end_y: int):
        """Calculate traffic for a portion of the map to reduce lag"""
        # Reset traffic only on first call
        if start_y == 0:
            for y in range(MAP_SIZE):
                for x in range(MAP_SIZE):
                    # Gradual decay with road capacity consideration
                    if self.grid[y][x] == CellType.ROAD:
                        self.sim_data[y][x].traffic = max(0, self.sim_data[y][x].traffic - 15)
                    elif self.grid[y][x] == CellType.RAIL:
                        self.sim_data[y][x].traffic = max(0, self.sim_data[y][x].traffic - 5)  # Rails decay slower
                    else:
                        self.sim_data[y][x].traffic = max(0, self.sim_data[y][x].traffic - 20)
        
        # Rush hour multiplier (more realistic hours)
        hour = (self.simulation_tick // 60) % 24
        if hour in [7, 8, 9]:  # Morning rush
            rush_multiplier = 1.8
        elif hour in [17, 18, 19]:  # Evening rush
            rush_multiplier = 2.0
        elif hour in [12, 13]:  # Lunch hour
            rush_multiplier = 1.3
        elif hour in [0, 1, 2, 3, 4, 5]:  # Night time
            rush_multiplier = 0.3
        else:
            rush_multiplier = 1.0
        
        # Calculate traffic for this portion
        for y in range(start_y, end_y):
            for x in range(MAP_SIZE):
                if self.grid[y][x] == CellType.RESIDENTIAL and self.sim_data[y][x].population > 5:
                    # Residential generates commute traffic
                    traffic_generated = int(self.sim_data[y][x].population * rush_multiplier // 6)
                    self._distribute_traffic(x, y, traffic_generated, [CellType.COMMERCIAL, CellType.INDUSTRIAL])
                    
                elif self.grid[y][x] == CellType.COMMERCIAL and self.sim_data[y][x].population > 5:
                    # Commercial generates customer traffic
                    traffic_generated = int(self.sim_data[y][x].population * rush_multiplier * 0.8 // 8)
                    self._distribute_traffic(x, y, traffic_generated, [CellType.RESIDENTIAL])
                    
                elif self.grid[y][x] == CellType.INDUSTRIAL and self.sim_data[y][x].population > 5:
                    # Industrial generates freight traffic (less affected by rush hour)
                    freight_multiplier = min(1.3, rush_multiplier)
                    traffic_generated = int(self.sim_data[y][x].population * freight_multiplier // 10)
                    self._distribute_traffic(x, y, traffic_generated, [CellType.COMMERCIAL, CellType.SEAPORT, CellType.AIRPORT])
                
                # Agricultural generates delivery traffic to commercial
                elif self.grid[y][x] == CellType.AGRICULTURAL and self.sim_data[y][x].population > 0:
                    traffic_generated = int(self.sim_data[y][x].population // 12)
                    self._distribute_traffic(x, y, traffic_generated, [CellType.COMMERCIAL])
                
                # Stations generate base traffic (hub activity)
                elif self.grid[y][x] == CellType.STATION:
                    # Stations always have some traffic
                    self.sim_data[y][x].traffic = max(20, self.sim_data[y][x].traffic)
                    # Also generate traffic to/from other zones
                    traffic_generated = int(30 * rush_multiplier)
                    self._distribute_traffic(x, y, traffic_generated, [CellType.RESIDENTIAL, CellType.COMMERCIAL])
                
                # Apply traffic pollution (reduced to half)
                if self.grid[y][x] in [CellType.ROAD, CellType.RAIL]:
                    traffic_level = self.sim_data[y][x].traffic
                    if traffic_level > 100:
                        # Heavy traffic generates pollution (reduced by 50%)
                        pollution_generated = (traffic_level - 100) // 20  # Was //10, now //20 for half pollution
                        self.sim_data[y][x].pollution = min(255, self.sim_data[y][x].pollution + pollution_generated)
    
    def _distribute_traffic(self, x: int, y: int, traffic: int, target_types: list):
        """Distribute traffic to nearby destinations using road network"""
        # Find nearest road or rail
        road_x, road_y = self._find_nearest_road(x, y)
        if road_x == -1:
            return  # No road access
        
        # Find destinations with road access - OPTIMIZED
        destinations = []
        search_radius = 12  # Reduced search radius
        
        # Sample fewer cells for performance
        for dy in range(-search_radius, search_radius + 1, 2):  # Skip every other row
            for dx in range(-search_radius, search_radius + 1, 2):  # Skip every other column
                nx, ny = x + dx, y + dy
                if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE:
                    if self.grid[ny][nx] in target_types and self.sim_data[ny][nx].population > 0:
                        # Quick check - don't call _find_nearest_road for every destination
                        distance = abs(dx) + abs(dy)
                        destinations.append((nx, ny, distance))
        
        # Sort by distance and take closest destinations
        destinations.sort(key=lambda d: d[2])
        destinations = destinations[:2]  # Reduce to 2 destinations
        
        # Distribute traffic to each destination
        if destinations:
            traffic_per_dest = traffic // len(destinations)
            for dest_x, dest_y, _ in destinations:
                # Simple traffic distribution without complex pathfinding
                self._add_simple_traffic(road_x, road_y, dest_x, dest_y, traffic_per_dest)
    
    def _find_nearest_road(self, x: int, y: int) -> tuple:
        """Find the nearest road, rail, or station to a position"""
        # Check if already on road/rail/station
        if self.grid[y][x] in [CellType.ROAD, CellType.RAIL, CellType.STATION]:
            return x, y
        
        # Search in expanding circles
        for radius in range(1, 4):  # Max 3 tiles away
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if abs(dx) == radius or abs(dy) == radius:  # Only check perimeter
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE:
                            if self.grid[ny][nx] in [CellType.ROAD, CellType.RAIL, CellType.STATION]:
                                return nx, ny
        return -1, -1  # No road found
    
    def _add_simple_traffic(self, x1: int, y1: int, x2: int, y2: int, traffic: int):
        """Add traffic using simple Manhattan path without complex pathfinding"""
        # Very simple path - just draw a line from source to destination
        steps = abs(x2 - x1) + abs(y2 - y1)
        if steps == 0:
            return
        
        traffic_per_step = max(1, traffic // steps)
        
        cx, cy = x1, y1
        for _ in range(min(steps, 20)):  # Limit to 20 steps for performance
            # Add traffic if on road/rail/station
            if 0 <= cx < MAP_SIZE and 0 <= cy < MAP_SIZE:
                if self.grid[cy][cx] in [CellType.ROAD, CellType.RAIL, CellType.STATION]:
                    self.sim_data[cy][cx].traffic = min(255, self.sim_data[cy][cx].traffic + traffic_per_step)
            
            # Move toward destination
            if cx < x2:
                cx += 1
            elif cx > x2:
                cx -= 1
            elif cy < y2:
                cy += 1
            elif cy > y2:
                cy -= 1
            else:
                break
    
    def _add_traffic_along_roads(self, x1: int, y1: int, x2: int, y2: int, traffic: int):
        """Add traffic along road network using simplified A* pathfinding"""
        from collections import deque
        
        # Quick distance check
        if abs(x2 - x1) + abs(y2 - y1) > 32:
            return  # Too far, skip for performance
        
        # BFS to find path along roads
        queue = deque([(x1, y1, [])])
        visited = set()
        visited.add((x1, y1))
        max_search = 200  # Limit search for performance
        search_count = 0
        
        while queue and search_count < max_search:
            search_count += 1
            cx, cy, path = queue.popleft()
            
            # Check if reached destination area
            if abs(cx - x2) <= 1 and abs(cy - y2) <= 1:
                # Add traffic along the path
                for px, py in path:
                    if self.grid[py][px] in [CellType.ROAD, CellType.RAIL]:
                        # Calculate capacity based on road type
                        capacity = 200 if self.grid[py][px] == CellType.ROAD else 400  # Rails have higher capacity
                        
                        # Add traffic with congestion consideration
                        current_traffic = self.sim_data[py][px].traffic
                        if current_traffic < capacity:
                            added_traffic = min(traffic, capacity - current_traffic)
                            self.sim_data[py][px].traffic = min(255, current_traffic + added_traffic)
                        else:
                            # Road is congested, add less traffic and generate less pollution (reduced by 50%)
                            self.sim_data[py][px].traffic = min(255, current_traffic + traffic // 3)
                            self.sim_data[py][px].pollution = min(255, self.sim_data[py][px].pollution + 2)  # Was +5, now +2
                return
            
            # Explore adjacent roads
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE:
                    if (nx, ny) not in visited:
                        if self.grid[ny][nx] in [CellType.ROAD, CellType.RAIL]:
                            visited.add((nx, ny))
                            new_path = path + [(nx, ny)]
                            # Priority to paths moving toward destination
                            if abs(nx - x2) + abs(ny - y2) < abs(cx - x2) + abs(cy - y2):
                                queue.appendleft((nx, ny, new_path))  # Higher priority
                            else:
                                queue.append((nx, ny, new_path))  # Reached destination
    
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
    
    def _update_employment(self):
        """Calculate employment rate and economic indicators"""
        res_pop = sum(self.sim_data[y][x].population for y in range(MAP_SIZE) for x in range(MAP_SIZE)
                     if self.grid[y][x] == CellType.RESIDENTIAL)
        self.total_employment = sum(self.sim_data[y][x].population for y in range(MAP_SIZE) for x in range(MAP_SIZE)
                          if self.grid[y][x] in [CellType.COMMERCIAL, CellType.INDUSTRIAL])

        if res_pop > 0:
            self.employment_rate = min(1.0, self.total_employment / res_pop)
        else:
            self.employment_rate = 0.0

        # Calculate GDP
        com_revenue = sum(self.sim_data[y][x].population * 2 for y in range(MAP_SIZE) for x in range(MAP_SIZE)
                         if self.grid[y][x] == CellType.COMMERCIAL)
        ind_revenue = sum(self.sim_data[y][x].population * 3 for y in range(MAP_SIZE) for x in range(MAP_SIZE)
                         if self.grid[y][x] == CellType.INDUSTRIAL)
        self.gdp = com_revenue + ind_revenue
    
    def _update_crime_and_fire_risk(self):
        """Optimized crime and fire risk calculation"""
        # Process only every 3rd cell for performance
        offset = self.simulation_tick % 3
        for y in range(offset, MAP_SIZE, 3):
            for x in range(offset, MAP_SIZE, 3):
                # Crime calculation
                crime_level = 0
                if self.grid[y][x] in [CellType.RESIDENTIAL, CellType.COMMERCIAL]:
                    # Base crime from population density
                    crime_level = self.sim_data[y][x].population // 100
                    
                    # Unemployment increases crime
                    if self.employment_rate < 0.8:
                        crime_level += int((0.8 - self.employment_rate) * 10)
                    
                    # Police stations reduce crime - optimized check
                    for dy in range(-4, 5, 2):  # Reduced range and step
                        for dx in range(-4, 5, 2):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE:
                                if self.grid[ny][nx] == CellType.POLICE:
                                    distance = abs(dx) + abs(dy)
                                    crime_level -= max(0, 8 - distance)
                
                # Store crime level (add attribute if not exists)
                if not hasattr(self.sim_data[y][x], 'crime'):
                    self.sim_data[y][x].crime = 0
                self.sim_data[y][x].crime = max(0, min(100, crime_level))
                
                # Fire risk calculation
                fire_risk = 0
                if self.grid[y][x] in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL]:
                    # Dense buildings have higher fire risk
                    fire_risk = self.sim_data[y][x].density * 5
                    
                    # Industrial areas have higher fire risk
                    if self.grid[y][x] == CellType.INDUSTRIAL:
                        fire_risk += 10
                    
                    # Fire stations reduce risk - optimized
                    for dy in range(-3, 4, 2):  # Reduced range
                        for dx in range(-3, 4, 2):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < MAP_SIZE and 0 <= ny < MAP_SIZE:
                                if self.grid[ny][nx] == CellType.FIRE:
                                    distance = abs(dx) + abs(dy)
                                    fire_risk -= max(0, 6 - distance)
                
                # Store fire risk
                if not hasattr(self.sim_data[y][x], 'fire_risk'):
                    self.sim_data[y][x].fire_risk = 0
                self.sim_data[y][x].fire_risk = max(0, min(100, fire_risk))
    
    def _update_economic_factors(self):
        """Update economic simulation factors"""
        # Collect taxes
        tax_revenue = 0
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                if self.grid[y][x] in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL]:
                    if self.sim_data[y][x].population > 0:
                        # Tax based on population and tax rate
                        base_tax = self.sim_data[y][x].population // 50
                        tax_revenue += int(base_tax * (self.tax_rate / 10.0))
        
        # Add tax revenue to funds
        if not self.infinite_funds:
            self.funds += tax_revenue
        
        # Service costs
        service_cost = 0
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                if self.grid[y][x] == CellType.POLICE:
                    service_cost += 20
                elif self.grid[y][x] == CellType.FIRE:
                    service_cost += 15
                elif self.grid[y][x] == CellType.HOSPITAL:
                    service_cost += 25
                elif self.grid[y][x] == CellType.SCHOOL:
                    service_cost += 30
                elif self.grid[y][x] in [CellType.COAL_PLANT, CellType.NUCLEAR_PLANT]:
                    service_cost += 50
                elif self.grid[y][x] == CellType.ROAD:
                    service_cost += 1
        
        # Deduct service costs
        if not self.infinite_funds:
            self.funds -= service_cost
    
    def _update_camera(self):
        """Update camera to center on cursor"""
        # Calculate target camera position
        target_x = self.cursor_x * TILE_SIZE - SCREEN_WIDTH // 2
        target_y = self.cursor_y * TILE_SIZE - SCREEN_HEIGHT // 2
        
        # Clamp camera to map bounds
        max_camera_x = MAP_SIZE * TILE_SIZE - SCREEN_WIDTH
        max_camera_y = MAP_SIZE * TILE_SIZE - SCREEN_HEIGHT
        
        new_camera_x = max(0, min(target_x, max_camera_x))
        new_camera_y = max(0, min(target_y, max_camera_y))
        
        # Check if camera has moved
        if new_camera_x != self.prev_camera_x or new_camera_y != self.prev_camera_y:
            self.is_moving = True
            self.move_timer = 30  # Keep minimap visible for 30 frames (0.5 seconds) after movement stops
            self.prev_camera_x = new_camera_x
            self.prev_camera_y = new_camera_y
        
        self.camera_x = new_camera_x
        self.camera_y = new_camera_y
    
    def save_city(self, filename):
        """Save the current city state to a file"""
        try:
            save_data = {
                'grid': [[cell.value for cell in row] for row in self.grid],
                'sim_data': [[asdict(data) for data in row] for row in self.sim_data],
                'funds': self.funds,
                'total_population': self.total_population,
                'res_demand': self.res_demand,
                'com_demand': self.com_demand,
                'ind_demand': self.ind_demand,
                'employment_rate': self.employment_rate,
                'gdp': self.gdp,
                'next_building_id': self.next_building_id,
                'year': self.year,
                'month': self.month,
                'day': self.day
            }

            # Save advanced system data
            if hasattr(self, 'traffic_system'):
                save_data['traffic_system'] = {
                    'traffic_lights': {(k[0], k[1]): {
                        'state': v.state.value,
                        'timer': v.timer
                    } for k, v in self.traffic_system.traffic_lights.items()},
                    'bus_stops': {(k[0], k[1]): {
                        'route_id': v.route_id,
                        'passengers_waiting': v.passengers_waiting
                    } for k, v in self.traffic_system.bus_stops.items()},
                    'buses': {k: {
                        'route_id': v.route_id,
                        'current_x': v.current_x,
                        'current_y': v.current_y,
                        'target_x': v.target_x,
                        'target_y': v.target_y,
                        'passengers': v.passengers,
                        'next_stop_index': v.next_stop_index
                    } for k, v in self.traffic_system.buses.items()}
                }

            if hasattr(self, 'economic_system'):
                save_data['economic_system'] = self.economic_system.export_save_data()

            if hasattr(self, 'disaster_system'):
                save_data['disaster_system'] = {
                    'total_damage_cost': self.disaster_system.total_damage_cost,
                    'emergency_services': {(k[0], k[1]): {
                        'service_type': v.service_type,
                        'current_load': v.current_load
                    } for k, v in self.disaster_system.emergency_services.items()},
                    'disaster_history': [(d.id, d.disaster_type.value, d.severity.value,
                                        d.center_x, d.center_y, d.radius) for d in self.disaster_system.disaster_history]
                }

            with open(filename, 'wb') as f:
                pickle.dump(save_data, f)

            print(f"💾 City saved to {filename}")
            self.show_message = "City Saved!"
            self.message_timer = 60

        except Exception as e:
            print(f"❌ Failed to save city: {e}")
            self.show_message = "Save Failed!"
            self.message_timer = 60
    
    def save_terrain(self, filename):
        """Save just the terrain (water/empty cells) and coastline data to a file"""
        try:
            terrain_data = []
            for y in range(MAP_SIZE):
                row = []
                for x in range(MAP_SIZE):
                    # Only save terrain types (water/empty)
                    if self.grid[y][x] in [CellType.WATER, CellType.EMPTY]:
                        row.append(self.grid[y][x].value)
                    else:
                        # Convert buildings to empty for terrain save
                        row.append(CellType.EMPTY.value)
                terrain_data.append(row)
            
            # Save both terrain and coastline map
            save_data = {
                'terrain': terrain_data,
                'coastline_map': self.coastline_map
            }
            
            with open(filename, 'wb') as f:
                pickle.dump(save_data, f)
            
            print(f"🗺️ Terrain and coastlines saved to {filename}")
            self.show_message = "Terrain Saved!"
            self.message_timer = 60
            
        except Exception as e:
            print(f"❌ Failed to save terrain: {e}")
            self.show_message = "Save Failed!"
            self.message_timer = 60
    
    def _load_terrain(self, filename):
        """Load terrain data from a file (internal use during init)"""
        try:
            with open(filename, 'rb') as f:
                save_data = pickle.load(f)
            
            # Handle different save formats
            if isinstance(save_data, dict):
                # Check if it's from generate_terrain_100.py (has 'grid' key)
                if 'grid' in save_data:
                    # New 100x100 format from generate_terrain_100.py
                    terrain_grid = save_data['grid']
                    self.coastline_map = save_data.get('coastline_map', {})
                    # Load directly from grid
                    for y in range(MAP_SIZE):
                        for x in range(MAP_SIZE):
                            self.grid[y][x] = terrain_grid[y][x]
                else:
                    # Old format with 'terrain' key
                    terrain_data = save_data['terrain']
                    self.coastline_map = save_data.get('coastline_map', {})
                    # Load terrain into grid
                    for y in range(MAP_SIZE):
                        for x in range(MAP_SIZE):
                            self.grid[y][x] = CellType(terrain_data[y][x])
            else:
                # Very old format - just terrain data
                terrain_data = save_data
                self.coastline_map = {}
                for y in range(MAP_SIZE):
                    for x in range(MAP_SIZE):
                        self.grid[y][x] = CellType(terrain_data[y][x])
            
            # DON'T add initial infrastructure - keep terrain clean
            # User can build their own infrastructure
            
            print(f"🗺️ Terrain loaded from {filename}")
            
            # Debug: Check grid content
            residential_count = sum(1 for y in range(MAP_SIZE) for x in range(MAP_SIZE) if self.grid[y][x] == CellType.RESIDENTIAL)
            water_count = sum(1 for y in range(MAP_SIZE) for x in range(MAP_SIZE) if self.grid[y][x] == CellType.WATER)
            empty_count = sum(1 for y in range(MAP_SIZE) for x in range(MAP_SIZE) if self.grid[y][x] == CellType.EMPTY)
            print(f"Debug - Grid content: Empty={empty_count}, Water={water_count}, Residential={residential_count}")
            
        except Exception as e:
            print(f"❌ Failed to load terrain: {e}")
            # Don't call _init_world() here - it will cause infinite recursion!
            # Just continue with empty map
            print("⚠️ Using empty map instead")
    
    def load_city(self, filename):
        """Load city state from a file"""
        try:
            if not os.path.exists(filename):
                print(f"⚠️ Save file {filename} not found")
                self.show_message = "No Save File"
                self.message_timer = 60
                return
            
            with open(filename, 'rb') as f:
                save_data = pickle.load(f)
            
            # Restore grid
            for y in range(MAP_SIZE):
                for x in range(MAP_SIZE):
                    self.grid[y][x] = CellType(save_data['grid'][y][x])
            
            # Restore sim data
            for y in range(MAP_SIZE):
                for x in range(MAP_SIZE):
                    data_dict = save_data['sim_data'][y][x]
                    self.sim_data[y][x] = SimData(**data_dict)
            
            # Restore other state
            self.funds = save_data['funds']
            self.total_population = save_data['total_population']
            self.res_demand = save_data['res_demand']
            self.com_demand = save_data['com_demand']
            self.ind_demand = save_data['ind_demand']
            self.employment_rate = save_data.get('employment_rate', 0.0)
            self.gdp = save_data.get('gdp', 0)
            self.next_building_id = save_data.get('next_building_id', 1)
            self.year = save_data.get('year', 2025)
            self.month = save_data.get('month', 1)
            self.day = save_data.get('day', 1)

            # Restore advanced system data
            if 'traffic_system' in save_data and hasattr(self, 'traffic_system'):
                traffic_data = save_data['traffic_system']
                # Restore traffic lights
                self.traffic_system.traffic_lights.clear()
                for (x, y), light_data in traffic_data.get('traffic_lights', {}).items():
                    from traffic_system import TrafficLight, TrafficLightState
                    self.traffic_system.traffic_lights[(x, y)] = TrafficLight(
                        x, y, TrafficLightState(light_data['state']), light_data['timer']
                    )
                # Restore bus stops
                self.traffic_system.bus_stops.clear()
                for (x, y), stop_data in traffic_data.get('bus_stops', {}).items():
                    from traffic_system import BusStop
                    self.traffic_system.bus_stops[(x, y)] = BusStop(
                        x, y, stop_data['route_id'], stop_data['passengers_waiting']
                    )
                # Restore buses
                self.traffic_system.buses.clear()
                for bus_id, bus_data in traffic_data.get('buses', {}).items():
                    from traffic_system import Bus
                    self.traffic_system.buses[bus_id] = Bus(
                        bus_id, bus_data['route_id'],
                        bus_data['current_x'], bus_data['current_y'],
                        bus_data['target_x'], bus_data['target_y'],
                        bus_data['passengers'], next_stop_index=bus_data['next_stop_index']
                    )

            if 'economic_system' in save_data and hasattr(self, 'economic_system'):
                self.economic_system.import_save_data(save_data['economic_system'])

            if 'disaster_system' in save_data and hasattr(self, 'disaster_system'):
                disaster_data = save_data['disaster_system']
                self.disaster_system.total_damage_cost = disaster_data.get('total_damage_cost', 0)
                # Restore emergency services
                self.disaster_system.emergency_services.clear()
                for (x, y), service_data in disaster_data.get('emergency_services', {}).items():
                    from disaster_system import EmergencyService, DisasterType
                    self.disaster_system.emergency_services[(x, y)] = EmergencyService(
                        service_data['service_type'], service_data['service_type'],
                        {DisasterType.EARTHQUAKE: 0.5, DisasterType.FIRE: 0.8},  # Simplified
                        10, 3, service_data['current_load']
                    )

            print(f"📂 City loaded from {filename}")
            self.show_message = "City Loaded!"
            self.message_timer = 60
            
        except Exception as e:
            print(f"❌ Failed to load city: {e}")
            self.show_message = "Load Failed!"
            self.message_timer = 60
    
    def draw(self):
        """Main drawing function"""
        pyxel.cls(0)
        
        # Draw map
        self._draw_map()
        
        # Draw cursor
        self._draw_cursor()
        
        # Draw minimap (always show if flag is set, or when moving)
        if self.always_show_minimap or self.is_moving:
            self._draw_minimap()
        
        # Draw demand/supply balance graph
        if self.show_balance_graph:
            self._draw_balance_graph()
            self._draw_quality_graphs()
        
        # Draw UI (must be last to overlay on top)
        self._draw_ui()

        # Draw simplified help overlay (on top of everything)
        self._draw_simplified_help()

        # Draw advanced UI panels (if not in MAIN_GAME mode)
        if hasattr(self, 'ui_system') and self.ui_system.current_panel != UIPanel.MAIN_GAME:
            ui_data = self._prepare_ui_data()
            self.ui_system.draw(ui_data)

    def _draw_map(self):
        """Draw the game map"""
        # Calculate visible tile range
        start_x = max(0, self.camera_x // TILE_SIZE)
        start_y = max(0, self.camera_y // TILE_SIZE)
        end_x = min(MAP_SIZE, (self.camera_x + SCREEN_WIDTH) // TILE_SIZE + 1)
        end_y = min(MAP_SIZE, (self.camera_y + SCREEN_HEIGHT) // TILE_SIZE + 1)
        
        # Store large buildings to draw later
        large_buildings = []
        
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                # Calculate screen position (offset by item panel height)
                screen_x = x * TILE_SIZE - self.camera_x
                screen_y = y * TILE_SIZE - self.camera_y + 24  # Offset for reduced item panel
                
                # Skip if off screen
                if screen_x < -TILE_SIZE or screen_x >= SCREEN_WIDTH:
                    continue
                if screen_y < -TILE_SIZE or screen_y >= SCREEN_HEIGHT:
                    continue
                
                cell_type = self.grid[y][x]
                data = self.sim_data[y][x]
                
                # Check if this is a large building that should be drawn later
                if cell_type in [CellType.COAL_PLANT, CellType.NUCLEAR_PLANT, CellType.GAS_PLANT, CellType.SOLAR_PLANT,
                                CellType.POLICE, CellType.FIRE, CellType.HOSPITAL, CellType.SCHOOL, CellType.UNIVERSITY,
                                CellType.SEWAGE_PLANT, CellType.WATER_PLANT, CellType.LIBRARY, CellType.LABORATORY,
                                CellType.MILITARY, CellType.PRISON, CellType.SHRINE, CellType.SPACE,
                                CellType.AIRPORT, CellType.HELIPORT, CellType.SEAPORT, CellType.STATION]:
                    building_id = data.building_id
                    if building_id > 0:
                        # Check if this is the top-left cell
                        is_top_left = True
                        if x > 0 and self.sim_data[y][x-1].building_id == building_id:
                            is_top_left = False
                        if y > 0 and self.sim_data[y-1][x].building_id == building_id:
                            is_top_left = False
                        
                        if is_top_left:
                            # Store for later drawing
                            large_buildings.append((x, y, screen_x, screen_y, cell_type, data))
                        continue  # Skip drawing this tile for now
                
                # Draw regular tiles (but not wire overlays yet)
                self._draw_tile(x, y, screen_x, screen_y, draw_wire=False)
        
        # Draw trains (before wire overlays, only in normal map view)
        if self.view_mode == 0:
            self._draw_trains(start_x, start_y, end_x, end_y)
        
        
        # Now draw large buildings on top
        for x, y, screen_x, screen_y, cell_type, data in large_buildings:
            self._draw_large_building(x, y, screen_x, screen_y, cell_type, data)
    
    def _draw_trains(self, start_x: int, start_y: int, end_x: int, end_y: int):
        """Draw trains on the visible portion of the map"""
        for train in self.train_system.trains:
            # Check if train is in visible area
            if start_x <= train.x < end_x and start_y <= train.y < end_y:
                screen_x = int(train.x * TILE_SIZE - self.camera_x)
                screen_y = int(train.y * TILE_SIZE - self.camera_y + 24)  # Offset for UI
                
                # Choose sprite based on train direction
                if train.direction in [TrainDirection.NORTH, TrainDirection.SOUTH]:
                    train_sprite = 'train_vertical'
                else:
                    train_sprite = 'train_horizontal'
                
                # Draw the train - make it more visible
                if self.use_graphics and train_sprite in self.tile_manager.tile_images:
                    # Draw the train sprite normally first
                    self.tile_manager.draw_tile(train_sprite, screen_x, screen_y, transparent_color=0)
                    # Add a larger visible indicator
                    if train.direction in [TrainDirection.NORTH, TrainDirection.SOUTH]:
                        # Vertical train - draw elongated rectangle
                        pyxel.rect(screen_x + 3, screen_y + 1, 2, 6, 9)  # Yellow vertical bar
                        pyxel.rect(screen_x + 3, screen_y + 1, 2, 2, 10)  # Orange front
                    else:
                        # Horizontal train - draw elongated rectangle  
                        pyxel.rect(screen_x + 1, screen_y + 3, 6, 2, 9)  # Yellow horizontal bar
                        pyxel.rect(screen_x + 1, screen_y + 3, 2, 2, 10)  # Orange front
                else:
                    # Fallback: draw as larger colored rectangle
                    pyxel.rect(screen_x + 1, screen_y + 1, 6, 6, 9)  # Yellow rectangle
                    pyxel.rectb(screen_x + 1, screen_y + 1, 6, 6, 10)  # Orange border
    
    def _draw_large_building(self, x: int, y: int, screen_x: int, screen_y: int, cell_type: CellType, data):
        """Draw a large building (3x3 or 4x4)"""
        
        # Determine building size for proper coloring in non-normal views
        building_width = 0
        building_height = 0
        
        # 4x4 buildings
        if cell_type in [CellType.COAL_PLANT, CellType.NUCLEAR_PLANT, CellType.GAS_PLANT, 
                        CellType.OIL_PLANT, CellType.LABORATORY, CellType.SPACE]:
            building_width = 4
            building_height = 4
        # 4x3 buildings
        elif cell_type == CellType.AIRPORT:
            building_width = 4
            building_height = 3
        # 2x2 buildings
        elif cell_type == CellType.SOLAR_PLANT:
            building_width = 2
            building_height = 2
        # 3x3 buildings
        else:
            building_width = 3
            building_height = 3
        
        # In normal view mode, draw the graphics
        if self.view_mode == 0:
            # Draw the actual building graphics
            if cell_type == CellType.COAL_PLANT:
                # Coal plant has 2-frame animation (32x32 px per frame, 64x32 px total)
                if 'coal_plant' in self.tile_manager.tile_images:
                    img = self.tile_manager.tile_images['coal_plant']
                    # Select frame based on time (slow animation)
                    frame = (pyxel.frame_count // 30) % 2  # Switch every 0.5 seconds
                    # Draw the selected frame (each frame is 32x32)
                    pyxel.blt(screen_x, screen_y, img, frame * 32, 0, 32, 32, 0)
                else:
                    # Fallback if image not loaded
                    self.tile_manager.draw_tile('coal_plant', screen_x, screen_y)
            elif cell_type == CellType.NUCLEAR_PLANT:
                # Nuclear plant has 2-frame animation (32x32 px per frame, 64x32 px total)
                if 'nuclear_plant' in self.tile_manager.tile_images:
                    img = self.tile_manager.tile_images['nuclear_plant']
                    # Select frame based on time (slow animation)
                    frame = (pyxel.frame_count // 30) % 2  # Switch every 0.5 seconds
                    # Draw the selected frame (each frame is 32x32)
                    pyxel.blt(screen_x, screen_y, img, frame * 32, 0, 32, 32, 0)
                else:
                    # Fallback if image not loaded
                    self.tile_manager.draw_tile('nuclear_plant', screen_x, screen_y)
            elif cell_type == CellType.GAS_PLANT:
                self.tile_manager.draw_tile('gas', screen_x, screen_y)
            elif cell_type == CellType.OIL_PLANT:
                self.tile_manager.draw_tile('oil', screen_x, screen_y)
            elif cell_type == CellType.SOLAR_PLANT:
                self.tile_manager.draw_tile('solar', screen_x, screen_y)
            elif cell_type == CellType.LABORATORY:
                self.tile_manager.draw_tile('laboratory', screen_x, screen_y)
            elif cell_type == CellType.SPACE:
                self.tile_manager.draw_tile('space', screen_x, screen_y)
            elif cell_type == CellType.AIRPORT:
                self.tile_manager.draw_tile('airport', screen_x, screen_y)
            elif cell_type == CellType.POLICE:
                self.tile_manager.draw_tile('police', screen_x, screen_y)
            elif cell_type == CellType.FIRE:
                self.tile_manager.draw_tile('fire', screen_x, screen_y)
            elif cell_type == CellType.HOSPITAL:
                self.tile_manager.draw_tile('hospital', screen_x, screen_y)
            elif cell_type == CellType.SCHOOL:
                self.tile_manager.draw_tile('school', screen_x, screen_y)
            elif cell_type == CellType.UNIVERSITY:
                self.tile_manager.draw_tile('university', screen_x, screen_y)
            elif cell_type == CellType.SEWAGE_PLANT:
                self.tile_manager.draw_tile('sewage_plant', screen_x, screen_y)
            elif cell_type == CellType.WATER_PLANT:
                self.tile_manager.draw_tile('water_plant', screen_x, screen_y)
            elif cell_type == CellType.LIBRARY:
                self.tile_manager.draw_tile('library', screen_x, screen_y)
            elif cell_type == CellType.MILITARY:
                self.tile_manager.draw_tile('military', screen_x, screen_y)
            elif cell_type == CellType.PRISON:
                self.tile_manager.draw_tile('prison', screen_x, screen_y)
            elif cell_type == CellType.SHRINE:
                self.tile_manager.draw_tile('shrine', screen_x, screen_y)
            elif cell_type == CellType.HELIPORT:
                self.tile_manager.draw_tile('heliport', screen_x, screen_y)
            elif cell_type == CellType.SEAPORT:
                if 'seaport' in self.tile_manager.tile_images:
                    self.tile_manager.draw_tile('seaport', screen_x, screen_y)
                else:
                    self.tile_manager.draw_tile('port', screen_x, screen_y)
            elif cell_type == CellType.INCINERATOR:
                self.tile_manager.draw_tile('incinerator', screen_x, screen_y)
            elif cell_type == CellType.WASTE_FACILITY:
                self.tile_manager.draw_tile('waste', screen_x, screen_y)
            elif cell_type == CellType.ONSEN:
                self.tile_manager.draw_tile('onsen', screen_x, screen_y)
            elif cell_type == CellType.PACHINKO:
                self.tile_manager.draw_tile('pachinko', screen_x, screen_y)
            elif cell_type == CellType.STATION:
                # Station is 3x3 (24x24px)
                self.tile_manager.draw_tile('station', screen_x, screen_y)
                
            # Show power/water overlays for certain building types
            if cell_type in [CellType.POLICE, CellType.FIRE, CellType.HOSPITAL, CellType.SCHOOL, 
                           CellType.UNIVERSITY, CellType.LIBRARY, CellType.INCINERATOR, CellType.WASTE_FACILITY]:
                if not data.power:
                    if pyxel.frame_count % 60 < 30:
                        for dy in range(building_height):
                            for dx in range(building_width):
                                overlay_x = screen_x + dx * 8
                                overlay_y = screen_y + dy * 8
                                self.tile_manager.draw_tile('no_power_overlay', overlay_x, overlay_y, transparent_color=0)
                                
            elif cell_type in [CellType.SEWAGE_PLANT, CellType.WATER_PLANT]:
                if not data.power and not data.water:
                    if pyxel.frame_count % 60 < 15:
                        for dy in range(building_height):
                            for dx in range(building_width):
                                overlay_x = screen_x + dx * 8
                                overlay_y = screen_y + dy * 8
                                self.tile_manager.draw_tile('no_power_overlay', overlay_x, overlay_y, transparent_color=0)
                    elif pyxel.frame_count % 60 < 30:
                        for dy in range(building_height):
                            for dx in range(building_width):
                                overlay_x = screen_x + dx * 8
                                overlay_y = screen_y + dy * 8
                                self.tile_manager.draw_tile('no_water_overlay', overlay_x, overlay_y, transparent_color=0)
                elif not data.power:
                    if pyxel.frame_count % 60 < 30:
                        for dy in range(building_height):
                            for dx in range(building_width):
                                overlay_x = screen_x + dx * 8
                                overlay_y = screen_y + dy * 8
                                self.tile_manager.draw_tile('no_power_overlay', overlay_x, overlay_y, transparent_color=0)
                elif not data.water:
                    if pyxel.frame_count % 60 < 30:
                        for dy in range(building_height):
                            for dx in range(building_width):
                                overlay_x = screen_x + dx * 8
                                overlay_y = screen_y + dy * 8
                                self.tile_manager.draw_tile('no_water_overlay', overlay_x, overlay_y, transparent_color=0)
        
        else:
            # For other view modes, draw colored rectangles for the entire building
            color = 0  # Default black
            
            if self.view_mode == 1:  # Pollution view
                pollution_level = data.pollution
                if pollution_level == 0:
                    color = 3  # Green
                elif pollution_level < 64:
                    color = 11  # Light green
                elif pollution_level < 128:
                    color = 10  # Yellow
                elif pollution_level < 192:
                    color = 9   # Orange
                else:
                    color = 8   # Red
                    
            elif self.view_mode == 2:  # Land value view
                land_value = data.land_value
                if land_value < 64:
                    color = 1   # Dark
                elif land_value < 128:
                    color = 2   # Purple
                elif land_value < 192:
                    color = 12  # Light blue
                else:
                    color = 7   # White
                    
            elif self.view_mode == 3:  # Power view
                # Power plants always show as cyan
                if cell_type in [CellType.COAL_PLANT, CellType.NUCLEAR_PLANT, CellType.GAS_PLANT, 
                                CellType.OIL_PLANT, CellType.WIND_PLANT, CellType.SOLAR_PLANT]:
                    color = 12  # Cyan for power sources
                else:
                    color = 11 if data.power else 8  # Green if powered, red if not
                    
            elif self.view_mode == 4:  # Traffic view
                # Special handling for water
                if cell_type == CellType.WATER:
                    color = 5  # Dark blue for water
                else:
                    traffic_level = data.traffic
                    # Show congestion levels based on road capacity
                    if cell_type == CellType.ROAD:
                        capacity = 200
                    elif cell_type == CellType.RAIL:
                        capacity = 400
                    else:
                        capacity = 100
                    
                    congestion_ratio = traffic_level / capacity if capacity > 0 else 0
                    
                    if traffic_level == 0:
                        color = 1   # Dark gray for no traffic
                    elif congestion_ratio < 0.25:
                        color = 3   # Green - free flowing
                    elif congestion_ratio < 0.5:
                        color = 11  # Light green - light traffic
                    elif congestion_ratio < 0.75:
                        color = 10  # Yellow - moderate traffic
                    elif congestion_ratio < 1.0:
                        color = 9   # Orange - heavy traffic
                    else:
                        color = 8   # Red - congested/over capacity
                    
            elif self.view_mode == 5:  # Water view with pollution overlay
                water_pollution = data.water_pollution
                # Water (ocean/lake) shows pollution level
                if cell_type == CellType.WATER:
                    if water_pollution > 150:
                        color = 2  # Dark brown for polluted water
                    elif water_pollution > 100:
                        color = 9  # Orange for polluted
                    elif water_pollution > 50:
                        color = 10  # Yellow
                    else:
                        color = 1  # Dark blue for clean ocean
                # Water plants show as cyan
                elif cell_type in [CellType.WATER_PLANT, CellType.SEWAGE_PLANT, CellType.PUMP]:
                    color = 12  # Cyan for water sources
                # Show water supply and pollution
                elif data.water:
                    if water_pollution > 100:
                        color = 9  # Orange - has water but polluted
                    elif water_pollution > 50:
                        color = 10  # Yellow - has water, slightly polluted
                    else:
                        color = 12  # Light blue - has clean water
                else:
                    color = 8  # Red - no water supply
            
            
            # Draw the colored rectangle for the entire building
            pyxel.rect(screen_x, screen_y, building_width * 8, building_height * 8, color)
    
    def _draw_tile(self, x: int, y: int, screen_x: int, screen_y: int, draw_wire: bool = True):
        """Draw a single tile"""
        cell_type = self.grid[y][x]
        data = self.sim_data[y][x]
        
        if self.view_mode == 0 and self.use_graphics:  # Normal view with graphics
            # Check if this position has a coastline tile
            coastline_tile = self.coastline_map.get((x, y))
            
            # Draw base terrain first (tile_id, x, y order)
            # Check if this is a bridge over water
            is_bridge = hasattr(data, 'original_terrain') and data.original_terrain == CellType.WATER
            
            if is_bridge:
                # Draw water under bridges
                self.tile_manager.draw_animated_tile('water', screen_x, screen_y)
            elif cell_type == CellType.WATER:
                self.tile_manager.draw_animated_tile('water', screen_x, screen_y)
            elif coastline_tile:
                # Draw appropriate coastline tile
                self.tile_manager.draw_tile(coastline_tile, screen_x, screen_y)
            elif cell_type == CellType.EMPTY:
                self.tile_manager.draw_tile('empty', screen_x, screen_y)
            elif cell_type == CellType.WASTELAND:
                self.tile_manager.draw_tile('wasteland', screen_x, screen_y)
            else:
                # Check if this cell is part of a merged building
                if (cell_type in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL] and 
                    data.merged_size > 1):
                    # For merged buildings, don't draw grass - the building will cover this area
                    pass
                else:
                    self.tile_manager.draw_tile('grass', screen_x, screen_y)
            
            # Check for road/rail overlap
            has_road = (cell_type == CellType.ROAD or 
                       (hasattr(data, 'has_road') and data.has_road))
            has_rail = (cell_type == CellType.RAIL or 
                       (hasattr(data, 'has_rail') and data.has_rail))
            
            # Draw the actual tile based on type (don't redraw background)
            if has_road and has_rail:
                # Draw road/rail crossing
                # Check road connections
                road_north = y > 0 and (self.grid[y-1][x] == CellType.ROAD or 
                                       (hasattr(self.sim_data[y-1][x], 'has_road') and self.sim_data[y-1][x].has_road))
                road_south = y < MAP_SIZE-1 and (self.grid[y+1][x] == CellType.ROAD or 
                                               (hasattr(self.sim_data[y+1][x], 'has_road') and self.sim_data[y+1][x].has_road))
                road_east = x < MAP_SIZE-1 and (self.grid[y][x+1] == CellType.ROAD or 
                                              (hasattr(self.sim_data[y][x+1], 'has_road') and self.sim_data[y][x+1].has_road))
                road_west = x > 0 and (self.grid[y][x-1] == CellType.ROAD or 
                                     (hasattr(self.sim_data[y][x-1], 'has_road') and self.sim_data[y][x-1].has_road))
                
                # Check rail connections
                rail_north = y > 0 and (self.grid[y-1][x] == CellType.RAIL or 
                                       (hasattr(self.sim_data[y-1][x], 'has_rail') and self.sim_data[y-1][x].has_rail))
                rail_south = y < MAP_SIZE-1 and (self.grid[y+1][x] == CellType.RAIL or 
                                               (hasattr(self.sim_data[y+1][x], 'has_rail') and self.sim_data[y+1][x].has_rail))
                rail_east = x < MAP_SIZE-1 and (self.grid[y][x+1] == CellType.RAIL or 
                                              (hasattr(self.sim_data[y][x+1], 'has_rail') and self.sim_data[y][x+1].has_rail))
                rail_west = x > 0 and (self.grid[y][x-1] == CellType.RAIL or 
                                     (hasattr(self.sim_data[y][x-1], 'has_rail') and self.sim_data[y][x-1].has_rail))
                
                # Determine crossing type
                if (road_north and road_south and not road_east and not road_west and
                    rail_east and rail_west and not rail_north and not rail_south):
                    # Vertical road, horizontal rail - use vertical PNG
                    self.tile_manager.draw_tile('road_rail_vertical', screen_x, screen_y)
                elif (road_east and road_west and not road_north and not road_south and
                      rail_north and rail_south and not rail_east and not rail_west):
                    # Horizontal road, vertical rail - use horizontal PNG
                    self.tile_manager.draw_tile('road_rail_horizontal', screen_x, screen_y)
                else:
                    # Complex crossing - draw rail on top of road for now
                    road_tile = self.tile_manager.get_road_tile_id(road_north, road_east, road_south, road_west)
                    rail_tile = self.tile_manager.get_rail_tile_id(rail_north, rail_east, rail_south, rail_west)
                    self.tile_manager.draw_tile(road_tile, screen_x, screen_y)
                    self.tile_manager.draw_tile(rail_tile, screen_x, screen_y, transparent_color=0)
                    
                    # Draw traffic overlay on complex crossings too (animated)
                    if data.traffic > 150:
                        # For crossings, use horizontal overlay as default
                        if 'traffic_overlay_horizontal' in self.tile_manager.tile_images:
                            frame = (pyxel.frame_count // 15) % 2
                            traffic_img = self.tile_manager.tile_images['traffic_overlay_horizontal']
                            pyxel.blt(screen_x, screen_y, traffic_img, frame * 8, 0, 8, 8, 0)  # 0 = black transparent
            
            elif cell_type == CellType.ROAD or has_road:
                # Check connections for roads
                north = y > 0 and (self.grid[y-1][x] == CellType.ROAD or 
                                 (hasattr(self.sim_data[y-1][x], 'has_road') and self.sim_data[y-1][x].has_road))
                south = y < MAP_SIZE-1 and (self.grid[y+1][x] == CellType.ROAD or 
                                          (hasattr(self.sim_data[y+1][x], 'has_road') and self.sim_data[y+1][x].has_road))
                east = x < MAP_SIZE-1 and (self.grid[y][x+1] == CellType.ROAD or 
                                         (hasattr(self.sim_data[y][x+1], 'has_road') and self.sim_data[y][x+1].has_road))
                west = x > 0 and (self.grid[y][x-1] == CellType.ROAD or 
                                (hasattr(self.sim_data[y][x-1], 'has_road') and self.sim_data[y][x-1].has_road))
                
                road_tile = self.tile_manager.get_road_tile_id(north, east, south, west)
                self.tile_manager.draw_tile(road_tile, screen_x, screen_y)
                
                # Draw traffic overlay if congested (animated)
                if data.traffic > 150:  # Heavy traffic threshold
                    # Determine road orientation
                    is_vertical = (north or south) and not (east or west)
                    is_horizontal = (east or west) and not (north or south)
                    
                    # Choose appropriate overlay
                    if is_vertical and 'traffic_overlay_vertical' in self.tile_manager.tile_images:
                        overlay_key = 'traffic_overlay_vertical'
                    elif is_horizontal and 'traffic_overlay_horizontal' in self.tile_manager.tile_images:
                        overlay_key = 'traffic_overlay_horizontal'
                    elif 'traffic_overlay_horizontal' in self.tile_manager.tile_images:
                        overlay_key = 'traffic_overlay_horizontal'  # Default for intersections
                    else:
                        overlay_key = None
                    
                    if overlay_key:
                        # Animate cars (2 frames side by side in 16x8 image)
                        frame = (pyxel.frame_count // 15) % 2
                        traffic_img = self.tile_manager.tile_images[overlay_key]
                        # Draw using blt with frame offset (each frame is 8x8)
                        pyxel.blt(screen_x, screen_y, traffic_img, frame * 8, 0, 8, 8, 0)  # 0 = black transparent
                
            elif cell_type == CellType.RAIL or has_rail:
                # Check connections for rails
                north = y > 0 and (self.grid[y-1][x] == CellType.RAIL or 
                                 (hasattr(self.sim_data[y-1][x], 'has_rail') and self.sim_data[y-1][x].has_rail))
                south = y < MAP_SIZE-1 and (self.grid[y+1][x] == CellType.RAIL or 
                                          (hasattr(self.sim_data[y+1][x], 'has_rail') and self.sim_data[y+1][x].has_rail))
                east = x < MAP_SIZE-1 and (self.grid[y][x+1] == CellType.RAIL or 
                                         (hasattr(self.sim_data[y][x+1], 'has_rail') and self.sim_data[y][x+1].has_rail))
                west = x > 0 and (self.grid[y][x-1] == CellType.RAIL or 
                                (hasattr(self.sim_data[y][x-1], 'has_rail') and self.sim_data[y][x-1].has_rail))
                
                rail_tile = self.tile_manager.get_rail_tile_id(north, east, south, west)
                self.tile_manager.draw_tile(rail_tile, screen_x, screen_y)
                # No traffic overlay for rails - trains are handled by TrainSystem
                
            elif cell_type in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL, CellType.AGRICULTURAL]:
                # Draw RCIA zones - empty if undeveloped, buildings if developed
                building_type = {
                    CellType.RESIDENTIAL: 'residential',
                    CellType.COMMERCIAL: 'commercial', 
                    CellType.INDUSTRIAL: 'industrial',
                    CellType.AGRICULTURAL: 'agricultural'
                }[cell_type]
                
                # Check if this is part of a merged building
                if data.merged_size > 1 and data.merged_top_left:
                    # Only draw if this is the top-left corner of the merged building
                    if (x, y) == data.merged_top_left:
                        # Draw the merged building
                        if data.under_construction > 0:
                            # Draw construction animation for merged building
                            for dy in range(data.merged_size):
                                for dx in range(data.merged_size):
                                    const_x = screen_x + dx * TILE_SIZE
                                    const_y = screen_y + dy * TILE_SIZE
                                    self.tile_manager.draw_tile(f'const_{building_type}', const_x, const_y)
                        else:
                            # Draw the large merged building
                            if data.merged_size == 2:
                                # 2x2 medium density building (16x16 pixels)
                                # Use {type}_2 which maps to middle_1.png (16x16)
                                tile_id = f'{building_type}_2'
                                self.tile_manager.draw_tile(tile_id, screen_x, screen_y)
                            elif data.merged_size == 3:
                                # 3x3 high density building
                                # Use {type}_3 or {type}_4 which map to high_1.png (32x32)
                                # The 32x32 asset will extend 4 pixels beyond the 3x3 area (24x24)
                                tile_id = f'{building_type}_4'
                                self.tile_manager.draw_tile(tile_id, screen_x, screen_y)
                    # For non-top-left cells of merged buildings, don't draw building
                    # but continue to draw other overlays (power, wire, etc.)
                    else:
                        pass  # Continue to draw overlays but skip the building itself
                # Regular 1x1 building drawing
                elif data.merged_size == 1:  # Only draw 1x1 buildings
                    # Check if zone is developed (has population) or just zoned
                    if data.under_construction > 0 and cell_type != CellType.AGRICULTURAL:
                        # Draw construction site (not for agricultural)
                        const_tile_id = f'const_{building_type}'
                        self.tile_manager.draw_tile(const_tile_id, screen_x, screen_y)
                    elif data.population > 0 and data.density > 0:
                        # Draw developed building/farm
                        if cell_type == CellType.AGRICULTURAL:
                            # Different tiles for agricultural development stages
                            if data.density >= 4:
                                self.tile_manager.draw_tile('silo', screen_x, screen_y)
                            elif data.density >= 3:
                                self.tile_manager.draw_tile('orchard', screen_x, screen_y)
                            elif data.density >= 2:
                                self.tile_manager.draw_tile('field', screen_x, screen_y)
                            else:
                                self.tile_manager.draw_tile('farm', screen_x, screen_y)
                        else:
                            # Use variant for low density buildings
                            if data.density == 1 and data.building_variant > 0:
                                tile_id = f'{building_type}_1_v{data.building_variant}'
                            else:
                                tile_id = self.tile_manager.get_building_tile_id(building_type, data.density)
                            self.tile_manager.draw_tile(tile_id, screen_x, screen_y)
                    else:
                        # Draw empty zone (just zoned, not developed yet)
                        empty_tile_id = f'empty_{building_type}'
                        self.tile_manager.draw_tile(empty_tile_id, screen_x, screen_y)
                
                # Show unpowered/no water buildings with blinking overlay
                if not data.power and not data.water:
                    # Alternate between power and water warning
                    if pyxel.frame_count % 120 < 30:  # Power overlay
                        self.tile_manager.draw_tile('no_power_overlay', screen_x, screen_y, transparent_color=0)
                    elif pyxel.frame_count % 120 < 60:  # Water overlay
                        self.tile_manager.draw_tile('no_water_overlay', screen_x, screen_y, transparent_color=0)
                elif not data.power:
                    # Blink every 30 frames (0.5 seconds)
                    if pyxel.frame_count % 60 < 30:
                        # Use black (color 0) as transparent for 16-color overlay
                        self.tile_manager.draw_tile('no_power_overlay', screen_x, screen_y, transparent_color=0)
                elif not data.water:
                    # Blink water warning
                    if pyxel.frame_count % 60 < 30:
                        self.tile_manager.draw_tile('no_water_overlay', screen_x, screen_y, transparent_color=0)
                    
            elif cell_type == CellType.WIRE:
                # Draw wire tiles with proper connections and transparency
                north = y > 0 and self.grid[y-1][x] == CellType.WIRE
                south = y < MAP_SIZE-1 and self.grid[y+1][x] == CellType.WIRE
                east = x < MAP_SIZE-1 and self.grid[y][x+1] == CellType.WIRE
                west = x > 0 and self.grid[y][x-1] == CellType.WIRE
                
                # Get the appropriate wire tile pattern
                wire_tile = self.tile_manager.get_wire_tile_id(north, east, south, west, overlay=False)
                
                # Draw wire with transparency - black background (color 0) is transparent
                self.tile_manager.draw_tile(wire_tile, screen_x, screen_y, transparent_color=0)
            elif cell_type == CellType.PARK:
                self.tile_manager.draw_tile('park', screen_x, screen_y)
            elif cell_type == CellType.PARK_MIDDLE:
                self.tile_manager.draw_tile('park_middle', screen_x, screen_y)
            elif cell_type == CellType.PUMP:
                self.tile_manager.draw_tile('pump', screen_x, screen_y)
            elif cell_type == CellType.WIND_PLANT:
                # Wind power is a 1x1 animated tile
                frame = (pyxel.frame_count // 20) % 2  # 2 frame animation, slower
                if 'wind_animation' in self.tile_manager.tile_images:
                    # Draw the animated wind turbine
                    img = self.tile_manager.tile_images['wind_animation']
                    # The PNG has 4 frames horizontally, each 8x8
                    pyxel.blt(screen_x, screen_y, img, frame * 8, 0, 8, 8, 0)
                else:
                    # Fallback to static wind tile
                    self.tile_manager.draw_tile('wind', screen_x, screen_y)
            elif cell_type == CellType.COAL_PLANT:
                # Large buildings are drawn separately, skip here
                pass
            elif cell_type == CellType.OIL_PLANT:
                self.tile_manager.draw_tile('oil_plant', screen_x, screen_y)
            elif cell_type == CellType.NUCLEAR_PLANT:
                # Large buildings are drawn separately, skip here
                pass
            elif cell_type == CellType.POLICE:
                # Large buildings are drawn separately, skip here
                pass
            elif cell_type == CellType.FIRE:
                # Large buildings are drawn separately, skip here
                pass
            elif cell_type == CellType.HOSPITAL:
                # Large buildings are drawn separately, skip here
                pass
            elif cell_type == CellType.SCHOOL:
                self.tile_manager.draw_tile('school', screen_x, screen_y)
                if not data.power:
                    # Blink every 30 frames
                    if pyxel.frame_count % 60 < 30:
                        # Use black (color 0) as transparent for 16-color overlay
                        self.tile_manager.draw_tile('no_power_overlay', screen_x, screen_y, transparent_color=0)
            
            # Wire overlay drawing moved to separate pass (after trains)
            
            # Draw water view overlay if in water view mode
            if self.view_mode == 5:
                # Semi-transparent overlay to show water status
                if data.water:
                    # Blue overlay for water supply
                    pyxel.rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE, 12)
                    pyxel.rectb(screen_x, screen_y, TILE_SIZE, TILE_SIZE, 5)
                else:
                    # Red overlay for no water
                    pyxel.rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE, 8)
                    pyxel.rectb(screen_x, screen_y, TILE_SIZE, TILE_SIZE, 2)
            
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
                # Show powered areas as green, unpowered as red
                if self.grid[y][x] in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL,
                                       CellType.POLICE, CellType.FIRE, CellType.HOSPITAL, CellType.SCHOOL]:
                    color = 11 if data.power else 8  # Green if powered, red if not
                elif self.grid[y][x] in [CellType.ROAD, CellType.WIRE]:
                    color = 10 if data.power else 2  # Yellow if powered, dark red if not
                elif self.grid[y][x] in [CellType.COAL_PLANT, CellType.OIL_PLANT, CellType.NUCLEAR_PLANT]:
                    color = 12  # Cyan for power plants
                else:
                    color = 1  # Dark for empty/non-electric cells
                
            elif self.view_mode == 4:  # Traffic view
                # Special handling for water and empty cells
                if cell_type == CellType.WATER:
                    color = 5  # Dark blue for water
                elif cell_type == CellType.EMPTY:
                    color = 1  # Dark gray for empty land
                else:
                    traffic_level = data.traffic
                    # Show congestion levels based on road capacity
                    if self.grid[y][x] == CellType.ROAD:
                        capacity = 200
                    elif self.grid[y][x] == CellType.RAIL:
                        capacity = 400
                    else:
                        capacity = 100
                    
                    congestion_ratio = traffic_level / capacity if capacity > 0 else 0
                    
                    if traffic_level == 0:
                        color = 1   # Dark gray for no traffic
                    elif congestion_ratio < 0.25:
                        color = 3   # Green - free flowing
                    elif congestion_ratio < 0.5:
                        color = 11  # Light green - light traffic
                    elif congestion_ratio < 0.75:
                        color = 10  # Yellow - moderate traffic
                    elif congestion_ratio < 1.0:
                        color = 9   # Orange - heavy traffic
                    else:
                        color = 8   # Red - congested/over capacity
                    
            elif self.view_mode == 5:  # Water view with pollution overlay
                water_pollution = data.water_pollution
                if cell_type == CellType.WATER:
                    # Ocean/lake shows pollution level
                    if water_pollution > 150:
                        color = 2  # Dark brown for polluted water
                    elif water_pollution > 100:
                        color = 9  # Orange for polluted
                    elif water_pollution > 50:
                        color = 10  # Yellow
                    else:
                        color = 1  # Dark blue for clean ocean
                elif data.water:
                    # Has water supply - show pollution level
                    if water_pollution > 100:
                        color = 9  # Orange - has water but polluted
                    elif water_pollution > 50:
                        color = 10  # Yellow - has water, slightly polluted
                    else:
                        color = 12  # Light blue - has clean water
                else:
                    color = 8  # Red - no water supply
            
            # Draw the tile
            pyxel.rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE, color)
            
            # Draw border for certain tile types
            if cell_type == CellType.WATER and self.view_mode == 0:
                pyxel.rectb(screen_x, screen_y, TILE_SIZE, TILE_SIZE, 1)
    
    def _draw_cursor(self):
        """Draw the cursor - 3x3 for buildings, 1x1 for infrastructure"""
        # Don't draw map cursor in palette mode
        if self.palette_mode:
            return
            
        cursor_screen_x = self.cursor_x * TILE_SIZE - self.camera_x
        cursor_screen_y = self.cursor_y * TILE_SIZE - self.camera_y + 24  # Offset for reduced item panel
        
        # Determine cursor size based on current item
        
        # 4x4 cursor for coal and nuclear plants
        if self.current_item in [ItemMode.COAL_PLANT, ItemMode.NUCLEAR_PLANT]:
            cursor_width = TILE_SIZE * 4  # 8 * 4 = 32 pixels
            cursor_height = TILE_SIZE * 4  # 8 * 4 = 32 pixels
            
            # Check if 4x4 can be placed
            can_place = self._can_place_4x4_building(self.cursor_x, self.cursor_y)
            cursor_color = 11 if can_place else 8  # Green if can place, red if cannot
        elif self.current_item in [ItemMode.GAS_PLANT, ItemMode.OIL_PLANT]:
            # 4x4 cursor for gas/oil plant
            cursor_width = TILE_SIZE * 4  # 8 * 4 = 32 pixels
            cursor_height = TILE_SIZE * 4  # 8 * 4 = 32 pixels
            
            # Check if 4x4 can be placed
            can_place = self._can_place_4x4_building(self.cursor_x, self.cursor_y)
            cursor_color = 11 if can_place else 8  # Green if can place, red if cannot
        elif self.current_item == ItemMode.WIND_PLANT:
            # 1x1 cursor for wind plant (animated)
            cursor_width = TILE_SIZE  # 8 pixels
            cursor_height = TILE_SIZE  # 8 pixels
            
            # Check if 1x1 can be placed
            new_type = self._tool_to_cell_type(self.current_item)
            can_place = self._can_place_1x1_building(self.cursor_x, self.cursor_y, new_type)
            cursor_color = 11 if can_place else 8  # Green if can place, red if cannot
        elif self.current_item in [ItemMode.STATION, ItemMode.POLICE, ItemMode.FIRE, ItemMode.HOSPITAL, ItemMode.SCHOOL, ItemMode.UNIVERSITY, ItemMode.SEWAGE_PLANT, ItemMode.WATER_PLANT, ItemMode.LIBRARY, ItemMode.MILITARY, ItemMode.PRISON, ItemMode.SHRINE, ItemMode.HELIPORT, ItemMode.SEAPORT, ItemMode.INCINERATOR, ItemMode.WASTE_FACILITY, ItemMode.ONSEN, ItemMode.PACHINKO]:
            # 3x3 cursor for stations, public services and special buildings
            cursor_width = TILE_SIZE * 3
            cursor_height = TILE_SIZE * 3
            
            # Check if 3x3 can be placed
            can_place = self._can_place_3x3_building(self.cursor_x, self.cursor_y)
            cursor_color = 11 if can_place else 8  # Green if can place, red if cannot
        else:
            # 1x1 cursor for RCI zones, roads, rails, etc.
            cursor_width = TILE_SIZE
            cursor_height = TILE_SIZE
            
            # Check if 1x1 can be placed
            if self.current_item == ItemMode.BULLDOZE:
                cursor_color = 8  # Red for bulldoze
            else:
                new_type = self._tool_to_cell_type(self.current_item)
                can_place = self._can_place_1x1_building(self.cursor_x, self.cursor_y, new_type) if new_type else False
                cursor_color = 11 if can_place else 8  # Green if can place, red if cannot
        
        # Only draw if cursor is visible
        if (cursor_screen_x < SCREEN_WIDTH and cursor_screen_y < SCREEN_HEIGHT and
            cursor_screen_x + cursor_width > 0 and cursor_screen_y + cursor_height > 0):
            pyxel.rectb(cursor_screen_x, cursor_screen_y, cursor_width, cursor_height, cursor_color)
            pyxel.rectb(cursor_screen_x + 1, cursor_screen_y + 1, cursor_width - 2, cursor_height - 2, 0)
    
    def _draw_9slice_window(self, x: int, y: int, width: int, height: int):
        """Draw a 9-slice window border using window_9slice.png"""
        # 9-slice assumes 8x8 corner/edge pieces
        slice_size = 8
        
        # Fill background first
        pyxel.rect(x + slice_size, y + slice_size, width - slice_size * 2, height - slice_size * 2, 0)
        
        # Draw using the 9-slice image if available
        if 'window_9slice' in self.tile_manager.tile_images:
            # Get the Image object directly for ImageTileSystem
            img = self.tile_manager.tile_images['window_9slice']
            
            # The 9-slice image should be 24x24 (3x3 grid of 8x8 tiles)
            # Layout: [TL][T][TR]
            #         [L] [C][R]
            #         [BL][B][BR]
            
            # Draw corners (8x8 each)
            pyxel.blt(x, y, img, 0, 0, slice_size, slice_size, 0)  # Top-left
            pyxel.blt(x + width - slice_size, y, img, slice_size * 2, 0, slice_size, slice_size, 0)  # Top-right
            pyxel.blt(x, y + height - slice_size, img, 0, slice_size * 2, slice_size, slice_size, 0)  # Bottom-left
            pyxel.blt(x + width - slice_size, y + height - slice_size, img, slice_size * 2, slice_size * 2, slice_size, slice_size, 0)  # Bottom-right
            
            # Draw edges (stretched)
            # Top edge
            for i in range(x + slice_size, x + width - slice_size, slice_size):
                w = min(slice_size, x + width - slice_size - i)
                pyxel.blt(i, y, img, slice_size, 0, w, slice_size, 0)
            
            # Bottom edge
            for i in range(x + slice_size, x + width - slice_size, slice_size):
                w = min(slice_size, x + width - slice_size - i)
                pyxel.blt(i, y + height - slice_size, img, slice_size, slice_size * 2, w, slice_size, 0)
            
            # Left edge
            for i in range(y + slice_size, y + height - slice_size, slice_size):
                h = min(slice_size, y + height - slice_size - i)
                pyxel.blt(x, i, img, 0, slice_size, slice_size, h, 0)
            
            # Right edge
            for i in range(y + slice_size, y + height - slice_size, slice_size):
                h = min(slice_size, y + height - slice_size - i)
                pyxel.blt(x + width - slice_size, i, img, slice_size * 2, slice_size, slice_size, h, 0)
            
            # Fill center if needed (using center tile)
            for cy in range(y + slice_size, y + height - slice_size, slice_size):
                for cx in range(x + slice_size, x + width - slice_size, slice_size):
                    w = min(slice_size, x + width - slice_size - cx)
                    h = min(slice_size, y + height - slice_size - cy)
                    pyxel.blt(cx, cy, img, slice_size, slice_size, w, h, 0)
        else:
            # Fallback to simple border
            pyxel.rectb(x, y, width, height, 7)
            pyxel.rectb(x + 1, y + 1, width - 2, height - 2, 1)
    
    def _draw_item_panel(self):
        """Draw two-row item selection panel at top of screen"""
        # Panel dimensions - reduced height for 2 rows
        panel_height = 24  # 2 rows of 8px icons + 8px spacing
        
        # Draw 9-slice window for entire panel
        self._draw_9slice_window(0, 0, SCREEN_WIDTH, panel_height)
        
        # Item info area (left side) with 9-slice window
        info_width = 50  # Slightly smaller
        self._draw_9slice_window(0, 0, info_width, panel_height)
        
        # Building tools arranged in 2 rows x 12 columns using 8x8 icons
        building_items = [
            # First row - zones, infrastructure, and basic services
            (ItemMode.RESIDENTIAL, 'icon_residential', "住宅"),
            (ItemMode.COMMERCIAL, 'icon_commercial', "商業"),
            (ItemMode.INDUSTRIAL, 'icon_industrial', "工業"),
            (ItemMode.AGRICULTURAL, 'icon_agricultural', "農業"),
            (ItemMode.ROAD, 'icon_road', "道路"),
            (ItemMode.RAIL, 'icon_rail', "鉄道"),
            (ItemMode.STATION, 'icon_station', "駅"),
            (ItemMode.WIRE, 'icon_wire', "電線"),
            (ItemMode.PARK, 'icon_park', "公園"),
            (ItemMode.POLICE, 'icon_police', "警察"),
            (ItemMode.FIRE, 'icon_fire', "消防"),
            (ItemMode.HOSPITAL, 'icon_hospital', "病院"),
            (ItemMode.BULLDOZE, 'icon_bulldozer', "撤去"),
            # Second row - power plants and utilities
            (ItemMode.COAL_PLANT, 'icon_coal_plant', "石炭"),
            (ItemMode.NUCLEAR_PLANT, 'icon_nuclear_plant', "原子力"),
            (ItemMode.GAS_PLANT, 'icon_gas_plant', "ガス"),
            (ItemMode.WIND_PLANT, 'icon_wind_plant', "風力"),
            (ItemMode.WATER_PLANT, 'icon_water_plant', "浄水"),
            (ItemMode.SEWAGE_PLANT, 'icon_sewage_plant', "下水"),
            (ItemMode.PUMP, 'icon_pump', "ポンプ"),
            (ItemMode.SCHOOL, 'icon_school', "学校"),
            (ItemMode.UNIVERSITY, 'icon_university', "大学"),
            (ItemMode.PARK_MIDDLE, 'icon_park_middle', "中公園"),
            (None, None, ""),  # Empty slots
            (None, None, "")
        ]
        
        # Display current item info
        current_item_info = None
        for item_info in building_items:
            if item_info[0] == self.current_item:
                current_item_info = item_info
                break
        
        if current_item_info:
            item_name = current_item_info[2]
            item_cost = self._get_building_cost(self.current_item)
            
            # Draw item name and cost (black text)
            if self.font_loaded:
                self._draw_japanese_text(3, 4, item_name, 0)  # Black text
                if item_cost > 0:
                    # Use smaller font for cost with yen symbol
                    cost_text = f"¥{item_cost}"
                    pyxel.text(3, 15, cost_text, 0)  # Small font for cost
            else:
                pyxel.text(3, 4, item_name[:8], 0)  # Black text
                if item_cost > 0:
                    pyxel.text(3, 15, f"¥{item_cost}", 0)  # Small font with yen
        
        # 2 rows x 12 columns layout
        icon_size = 8
        gap = 2  # 2px gap between icons
        start_x = info_width + 4
        cols_per_row = 12  # More columns to fit in 2 rows
        row_height = 10  # 8px icon + 2px spacing (reduced)
        start_y = 3  # Top padding
        
        # Draw items in 2 rows
        for i, item_data in enumerate(building_items):
            item_mode = item_data[0]
            tile_id = item_data[1]
            item_name = item_data[2] if len(item_data) > 2 else ""
            
            if item_mode is None:  # Skip empty slots
                continue
            
            # Calculate position (2 rows, 12 columns)
            row = i // cols_per_row
            col = i % cols_per_row
            x = start_x + col * (icon_size + gap)
            y = start_y + row * row_height
            
            # Highlight selected item or palette cursor (compact)
            if self.palette_mode and i == self.palette_cursor:
                # Palette cursor (flashing)
                color = 10 if pyxel.frame_count % 20 < 10 else 11
                pyxel.rectb(x - 1, y - 1, icon_size + 2, icon_size + 2, color)
            elif self.current_item == item_mode:
                # Selected item
                pyxel.rectb(x - 1, y - 1, icon_size + 2, icon_size + 2, 11)
            
            # Draw building tile
            if self.use_graphics:
                self.tile_manager.draw_tile(tile_id, x, y)
            else:
                # Fallback colored rectangle
                color = self.tile_colors.get(item_mode, 7)
                pyxel.rect(x, y, icon_size, icon_size, color)
            
            # No text labels to keep compact
        
        # Draw map bar (right side of item palette)
        self._draw_map_bar(panel_height)
    
    def _draw_map_bar(self, panel_height: int):
        """Draw map view mode selection bar"""
        # Map bar position - right side of screen
        map_bar_width = 112  # 6 icons with 18px spacing: 2 + 6*18 = 110px needed
        map_bar_x = SCREEN_WIDTH - map_bar_width - 2
        
        # Draw 9-slice window for map bar
        self._draw_9slice_window(map_bar_x, 0, map_bar_width, panel_height)
        
        # Map view modes (index, Japanese name, English name)
        view_modes = [
            (0, "地図", "MAP"),     # Normal
            (1, "汚染", "POL"),     # Pollution
            (2, "地価", "VAL"),     # Land Value
            (3, "電力", "PWR"),     # Power
            (4, "交通", "TRF"),     # Traffic
            (5, "水道", "WTR"),     # Water
        ]
        
        # Draw map icons from map_kind.png (16x16 icons)
        if 'map_kind' in self.tile_manager.tile_images:
            # Get the Image object for map_kind
            img = self.tile_manager.tile_images['map_kind']
            
            for i, (mode, jp_name, en_name) in enumerate(view_modes):
                # Position for each 16x16 icon
                # Simple uniform spacing
                icon_x = map_bar_x + 2 + i * 18  # 2px padding + icon index * (16px icon + 2px gap)
                icon_y = (panel_height - 16) // 2  # Center vertically
                
                # Highlight current view mode
                if self.view_mode == mode:
                    pyxel.rectb(icon_x - 1, icon_y - 1, 18, 18, 11)
                
                # Draw the icon from the strip (each icon is 16px wide)
                # map_kind.png has 6 icons in a row, each 16x16
                pyxel.blt(icon_x, icon_y, img, i * 16, 0, 16, 16)  # No transparency
        else:
            # Fallback: draw colored rectangles with text
            for i, (mode, jp_name, en_name) in enumerate(view_modes):
                icon_x = map_bar_x + 4 + i * 17
                icon_y = (panel_height - 16) // 2
                
                # Different colors for each mode
                colors = [3, 8, 10, 9, 12, 12]  # Green, Red, Yellow, Orange, Blue, Light Blue
                pyxel.rect(icon_x, icon_y, 16, 16, colors[i])
                
                # Highlight current mode
                if self.view_mode == mode:
                    pyxel.rectb(icon_x - 1, icon_y - 1, 18, 18, 11)
                
                # Draw abbreviated text
                pyxel.text(icon_x + 1, icon_y + 5, en_name[:3], 7)
    
    def _draw_9slice_panel(self, x, y, width, height):
        """Draw a 9-slice panel using window_9slice.png"""
        if not self.use_graphics:
            # Fallback to simple rectangle
            pyxel.rect(x, y, width, height, 0)
            pyxel.rectb(x, y, width, height, 7)
            return
        
        # 9-slice is 24x24, each slice is 8x8
        slice_size = 8
        
        # Draw corners (8x8 each)
        # Top-left
        self.tile_manager.draw_tile('window_9slice', x, y)
        # Top-right (need to manually draw from specific position)
        # Bottom-left
        # Bottom-right
        
        # For now, use simple bordered rectangle as fallback
        pyxel.rect(x, y, width, height, 0)
        pyxel.rectb(x, y, width, height, 7)
        pyxel.rectb(x+1, y+1, width-2, height-2, 5)
    
    def _draw_balance_graph(self):
        """Draw simple demand/supply balance meter"""
        # Compact position and size
        graph_x = SCREEN_WIDTH - 44  # Right side, smaller
        graph_y = 28  # Below reduced item panel (24px)
        graph_width = 40
        graph_height = 24
        
        # Calculate total supply and demand
        total_zones = sum(1 for y in range(MAP_SIZE) for x in range(MAP_SIZE) 
                         if self.grid[y][x] in [CellType.RESIDENTIAL, CellType.COMMERCIAL, 
                                               CellType.INDUSTRIAL, CellType.AGRICULTURAL])
        
        # Weighted average of demands
        total_demand = (self.res_demand + self.com_demand + self.ind_demand + 
                       (self.agr_demand if hasattr(self, 'agr_demand') else 0)) // 4
        
        # Calculate balance ratio (-100 to +100)
        max_zones = MAP_SIZE * MAP_SIZE // 8  # Reasonable maximum coverage
        supply_ratio = min(100, total_zones * 100 // max_zones) if max_zones > 0 else 0
        balance = total_demand - supply_ratio // 2  # Balance calculation
        
        # Draw compact frame
        pyxel.rectb(graph_x, graph_y, graph_width, graph_height, 1)
        pyxel.rect(graph_x + 1, graph_y + 1, graph_width - 2, graph_height - 2, 0)
        
        # Draw balance meter
        center = graph_width // 2
        meter_y = graph_y + graph_height // 2 - 3
        meter_height = 6
        
        # Draw center line
        pyxel.line(graph_x + center, meter_y, graph_x + center, meter_y + meter_height, 13)
        
        # Draw balance indicator
        if balance > 0:  # Need more zones
            width = min(center - 2, abs(balance) * (center - 2) // 100)
            pyxel.rect(graph_x + center + 1, meter_y, width, meter_height, 11)  # Green = growth needed
        elif balance < 0:  # Oversupply
            width = min(center - 2, abs(balance) * (center - 2) // 100)
            pyxel.rect(graph_x + center - width, meter_y, width, meter_height, 8)  # Red = oversupply
        
        # Simple label
        if self.font_loaded:
            self._draw_japanese_text(graph_x + 2, graph_y + 2, "需給", 7)
        else:
            pyxel.text(graph_x + 2, graph_y + 2, "D/S", 7)
        
        # Show numeric value
        pyxel.text(graph_x + 2, graph_y + graph_height - 8, f"{balance:+3d}", 
                  11 if balance > 0 else 8 if balance < 0 else 7)
    
    def _draw_quality_graphs(self):
        """Draw quality of life metrics below balance graph"""
        # Position below balance graph
        graph_x = SCREEN_WIDTH - 44
        graph_y = 56  # Below balance graph (28 + 24 + 4 gap)
        graph_width = 40
        bar_height = 4
        spacing = 6
        
        # Draw frame
        total_height = spacing * 3 + 8
        pyxel.rectb(graph_x, graph_y, graph_width, total_height, 1)
        pyxel.rect(graph_x + 1, graph_y + 1, graph_width - 2, total_height - 2, 0)
        
        # Draw each metric
        metrics = [
            ("生活", "LV", self.living_standard, 10),  # Yellow
            ("教育", "ED", self.education_level, 12),   # Blue
            ("治安", "SF", self.safety_level, 11)       # Green
        ]
        
        for i, (jp_name, en_name, value, color) in enumerate(metrics):
            y_pos = graph_y + 2 + i * spacing
            
            # Draw label (use JP if font loaded, EN otherwise)
            if self.font_loaded:
                # Draw smaller text by using pyxel.text for now
                pyxel.text(graph_x + 2, y_pos, en_name, 7)
            else:
                pyxel.text(graph_x + 2, y_pos, en_name, 7)
            
            # Draw bar
            bar_x = graph_x + 14
            bar_width = max(0, min(24, value * 24 // 100))
            pyxel.rect(bar_x, y_pos, bar_width, bar_height, color)
            pyxel.rectb(bar_x, y_pos, 24, bar_height, 5)
            
            # Show percentage
            pyxel.text(bar_x + 26, y_pos, f"{value}", 7)

    def _draw_simplified_help(self):
        """簡素化されたオンスクリーンヘルプを描画 / Draw simplified on-screen help"""

        # 初回起動時は常にヘルプを表示
        if self.show_startup_help:
            self.help_visible = True
            self.help_timer = 600  # 10秒間表示（初回のみ）

        if not self.help_visible:
            return

        help_width = 260
        help_height = 200

        # 背景（半透明黒）
        overlay_x = (SCREEN_WIDTH - help_width) // 2
        overlay_y = (SCREEN_HEIGHT - help_height) // 2

        # 外枠
        pyxel.rect(overlay_x, overlay_y, help_width, help_height, 0)
        pyxel.rectb(overlay_x, overlay_y, help_width, help_height, 7)

        # タイトル
        title = "操作ガイド - Hで閉じる"
        title_x = (SCREEN_WIDTH - len(title) * 4) // 2
        pyxel.text(title_x, overlay_y + 8, title, 7)

        # 内容
        y = overlay_y + 25

        # 移動
        pyxel.text(overlay_x + 10, y, "【移動】", 6)
        y += 12
        pyxel.text(overlay_x + 15, y, "矢印キー または K/J/H/L", 7)
        y += 18

        # アクション
        pyxel.text(overlay_x + 10, y, "【アクション】", 6)
        y += 12
        pyxel.text(overlay_x + 15, y, "スペース: 建物配置", 7)
        y += 10
        pyxel.text(overlay_x + 15, y, "X: 削除", 7)
        y += 18

        # ツール選択（簡易版）
        pyxel.text(overlay_x + 10, y, "【ツール選択】", 6)
        y += 12

        # ItemModeから主要なツールを表示
        tools = [
            ("Q", "住宅", ItemMode.RESIDENTIAL),
            ("W", "商業", ItemMode.COMMERCIAL),
            ("E", "工業", ItemMode.INDUSTRIAL),
            ("R", "道路", ItemMode.ROAD),
            ("T", "鉄道", ItemMode.RAIL),
            ("Y", "公園", ItemMode.PARK),
            ("U", "電線", ItemMode.WIRE),
            ("I", "発電所", ItemMode.COAL_PLANT),
            ("P", "公共", ItemMode.POLICE),
            ("A", "農業", ItemMode.AGRICULTURAL),
            ("\\", "削除", ItemMode.BULLDOZE),
        ]

        for key, name, item in tools:
            is_selected = (self.current_item == item)

            # 選択中のツールを強調
            if is_selected:
                pyxel.rect(overlay_x + 8, y - 2, help_width - 16, 10, 6)

            # キーとツール名
            pyxel.text(overlay_x + 12, y, key, 10 if is_selected else 7)
            pyxel.text(overlay_x + 30, y, name, 10 if is_selected else 6)

            y += 11

        y += 10

        # その他機能
        pyxel.text(overlay_x + 10, y, "【その他】", 6)
        y += 12
        pyxel.text(overlay_x + 15, y, "V: 表示切替", 7)
        y += 10
        pyxel.text(overlay_x + 15, y, "S/E/T/D/P: 詳細UI", 7)
        y += 10
        pyxel.text(overlay_x + 15, y, f"資金: ¥{self.funds:,}", 11)

        # 終了方法
        y += 15
        pyxel.text(overlay_x + 10, y, "【終了】", 6)
        y += 10
        pyxel.text(overlay_x + 15, y, "H キーで閉じる", 7)


    def _draw_ui(self):
        """Draw the UI overlay"""
        # Draw item panel at top
        self._draw_item_panel()
        
        # Draw message if present
        if self.message_timer > 0:
            msg_x = SCREEN_WIDTH // 2 - len(self.show_message) * 2
            msg_y = SCREEN_HEIGHT // 2 - 20
            # Draw background
            pyxel.rect(msg_x - 4, msg_y - 2, len(self.show_message) * 4 + 8, 11, 0)
            pyxel.rectb(msg_x - 5, msg_y - 3, len(self.show_message) * 4 + 10, 13, 7)
            # Draw message
            pyxel.text(msg_x, msg_y, self.show_message, 10)
            self.message_timer -= 1
        
        # Draw info panel at bottom (32px height with 9-slice)
        info_panel_height = 32
        self._draw_9slice_panel(0, SCREEN_HEIGHT - info_panel_height, SCREEN_WIDTH, info_panel_height)
        
        # Draw basic info with Japanese (adjusted for 32px panel)
        if self.font_loaded:
            # First row
            if self.dev_mode:
                self._draw_japanese_text(4, SCREEN_HEIGHT - 28, f"資金:∞", 11)
            else:
                self._draw_japanese_text(4, SCREEN_HEIGHT - 28, f"資金:¥{self.funds}", 7)
            self._draw_japanese_text(80, SCREEN_HEIGHT - 28, f"人口:{self.total_population}", 7)
            emp_pct = int(self.employment_rate * 100)
            self._draw_japanese_text(160, SCREEN_HEIGHT - 28, f"雇用:{emp_pct}%", 10 if emp_pct > 70 else 9)
            self._draw_japanese_text(220, SCREEN_HEIGHT - 28, f"GDP:¥{self.gdp}", 12)
            
            # Second row - RCI demand and view mode
            self._draw_japanese_text(4, SCREEN_HEIGHT - 14, f"住:{self.res_demand:+3d}", 10 if self.res_demand > 0 else 8)
            self._draw_japanese_text(44, SCREEN_HEIGHT - 14, f"商:{self.com_demand:+3d}", 10 if self.com_demand > 0 else 8)
            self._draw_japanese_text(84, SCREEN_HEIGHT - 14, f"工:{self.ind_demand:+3d}", 10 if self.ind_demand > 0 else 8)
            
            view_names = ["地図", "汚染", "地価", "電力", "交通", "水道"]
            self._draw_japanese_text(200, SCREEN_HEIGHT - 14, f"表示:{view_names[self.view_mode]}", 12)
        else:
            # First row
            if self.dev_mode:
                pyxel.text(4, SCREEN_HEIGHT - 28, f"¥:INF", 11)
            else:
                pyxel.text(4, SCREEN_HEIGHT - 28, f"¥{self.funds}", 7)
            pyxel.text(60, SCREEN_HEIGHT - 28, f"POP:{self.total_population}", 7)
            emp_pct = int(self.employment_rate * 100)
            pyxel.text(140, SCREEN_HEIGHT - 28, f"EMP:{emp_pct}%", 10 if emp_pct > 70 else 9)
            pyxel.text(200, SCREEN_HEIGHT - 28, f"GDP:¥{self.gdp}", 12)
            
            # Second row - RCI demand and view mode
            pyxel.text(4, SCREEN_HEIGHT - 14, "R:", 7)
            pyxel.text(16, SCREEN_HEIGHT - 14, f"{self.res_demand:+3d}", 10 if self.res_demand > 0 else 8)
            pyxel.text(44, SCREEN_HEIGHT - 14, "C:", 7)
            pyxel.text(56, SCREEN_HEIGHT - 14, f"{self.com_demand:+3d}", 10 if self.com_demand > 0 else 8)
            pyxel.text(84, SCREEN_HEIGHT - 14, "I:", 7)
            pyxel.text(96, SCREEN_HEIGHT - 14, f"{self.ind_demand:+3d}", 10 if self.ind_demand > 0 else 8)
            
            view_names = ["MAP", "POL", "VAL", "PWR", "TRF", "WTR"]
            pyxel.text(200, SCREEN_HEIGHT - 14, f"VIEW:{view_names[self.view_mode]}", 12)
    
    def _draw_minimap(self):
        """Draw minimap in top-left corner"""
        # Minimap settings - smaller size for 100x100 map
        # Use 40x40 pixels for 100x100 map (0.4 pixel per tile)
        minimap_display_size = 40  # Display size in pixels (half of previous 80)
        minimap_x = 4
        minimap_y = 28  # Below the reduced item panel (24px)
        border_color = 1  # Dark blue border
        
        # Draw minimap background (black)
        pyxel.rect(minimap_x - 1, minimap_y - 1, minimap_display_size + 2, minimap_display_size + 2, border_color)
        pyxel.rect(minimap_x, minimap_y, minimap_display_size, minimap_display_size, 0)
        
        # Draw minimap tiles based on current view mode
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                cell_type = self.grid[y][x]
                data = self.sim_data[y][x]
                
                # Determine pixel color based on view mode
                color = 0  # Black by default
                
                if self.view_mode == 0:  # Normal view
                    if cell_type == CellType.WATER:
                        color = 5  # Dark blue for water
                    elif cell_type == CellType.EMPTY:
                        color = 3  # Dark green for land
                    elif cell_type == CellType.ROAD:
                        color = 13  # Dark gray for roads
                    elif cell_type == CellType.RAIL:
                        color = 6  # Gray for rails
                    elif cell_type == CellType.RESIDENTIAL:
                        color = 11  # Light green for residential
                    elif cell_type == CellType.COMMERCIAL:
                        color = 12  # Light blue for commercial
                    elif cell_type == CellType.INDUSTRIAL:
                        color = 9  # Yellow for industrial
                    elif cell_type in [CellType.COAL_PLANT, CellType.NUCLEAR_PLANT, CellType.GAS_PLANT]:
                        color = 8  # Red for power plants
                    elif cell_type in [CellType.PARK, CellType.PARK_MIDDLE]:
                        color = 11  # Light green for parks
                    else:
                        color = 7  # Default white for other buildings
                
                elif self.view_mode == 1:  # Pollution view
                    pollution = data.pollution
                    if cell_type == CellType.WATER:
                        color = 5  # Dark blue (same as main view)
                    elif self.palette_loaded:
                        # Use palette colors for smooth gradient
                        color = 16 + min(47, pollution // 5)  # Colors 16-63 for pollution
                    else:
                        # Fallback colors matching main view
                        if pollution == 0:
                            color = 3  # Green for clean
                        elif pollution < 64:
                            color = 11  # Light green
                        elif pollution < 128:
                            color = 10  # Yellow
                        elif pollution < 192:
                            color = 9  # Orange
                        else:
                            color = 8  # Red for high pollution
                
                elif self.view_mode == 2:  # Land value view
                    land_value = data.land_value
                    if cell_type == CellType.WATER:
                        color = 5  # Dark blue (same as main view)
                    elif self.palette_loaded:
                        # Use palette colors for smooth gradient
                        color = 64 + min(47, land_value // 5)  # Colors 64-111 for land value
                    else:
                        # Fallback colors matching main view
                        if land_value < 64:
                            color = 1  # Dark for low value
                        elif land_value < 128:
                            color = 2  # Purple
                        elif land_value < 192:
                            color = 12  # Light green
                        else:
                            color = 7  # White for high value
                
                elif self.view_mode == 3:  # Power view
                    # Match main view power colors exactly
                    if cell_type == CellType.WATER:
                        color = 5  # Dark blue (same as main view)
                    elif cell_type in [CellType.RESIDENTIAL, CellType.COMMERCIAL, CellType.INDUSTRIAL,
                                       CellType.POLICE, CellType.FIRE, CellType.HOSPITAL, CellType.SCHOOL]:
                        color = 11 if data.power else 8  # Green if powered, red if not
                    elif cell_type in [CellType.ROAD, CellType.WIRE]:
                        color = 10 if data.power else 2  # Yellow if powered, dark red if not
                    elif cell_type in [CellType.COAL_PLANT, CellType.OIL_PLANT, CellType.NUCLEAR_PLANT]:
                        color = 12  # Cyan for power plants
                    else:
                        color = 1  # Dark for empty/non-electric cells
                
                elif self.view_mode == 4:  # Traffic view
                    # Match main view traffic colors with capacity-based congestion
                    if cell_type == CellType.WATER:
                        color = 5  # Dark blue for water
                    elif cell_type == CellType.EMPTY:
                        color = 1  # Dark gray for empty land
                    else:
                        traffic = data.traffic
                        # Show congestion levels based on road capacity
                        if cell_type == CellType.ROAD:
                            capacity = 200
                        elif cell_type == CellType.RAIL:
                            capacity = 400
                        else:
                            capacity = 100
                        
                        congestion_ratio = traffic / capacity if capacity > 0 else 0
                        
                        if traffic == 0:
                            color = 1  # Dark gray for no traffic
                        elif congestion_ratio < 0.25:
                            color = 3  # Green - free flowing
                        elif congestion_ratio < 0.5:
                            color = 11  # Light green - light traffic
                        elif congestion_ratio < 0.75:
                            color = 10  # Yellow - moderate traffic
                        elif congestion_ratio < 1.0:
                            color = 9  # Orange - heavy traffic
                        else:
                            color = 8  # Red - congested/over capacity
                
                elif self.view_mode == 5:  # Water view with pollution overlay
                    water_pollution = data.water_pollution
                    if cell_type == CellType.WATER:
                        # Show water body pollution
                        if water_pollution > 150:
                            color = 2  # Dark brown
                        elif water_pollution > 100:
                            color = 9  # Orange
                        elif water_pollution > 50:
                            color = 10  # Yellow
                        else:
                            color = 1  # Dark blue
                    elif data.water:
                        # Has water - show pollution level
                        if water_pollution > 100:
                            color = 9  # Orange - polluted
                        elif water_pollution > 50:
                            color = 10  # Yellow - slightly polluted
                        else:
                            color = 12  # Light blue - clean
                    else:
                        color = 8  # Red - no water
                
                # Draw the pixel (scaled for 100x100 map to 40x40 display)
                # Always draw the pixel, including black (color 0)
                # Scale from 100x100 to 40x40
                pixel_x = minimap_x + (x * minimap_display_size // MAP_SIZE)
                pixel_y = minimap_y + (y * minimap_display_size // MAP_SIZE)
                pyxel.pset(pixel_x, pixel_y, color)
        
        # Draw viewport rectangle (scaled for 100x100 map)
        viewport_x = self.camera_x // TILE_SIZE
        viewport_y = self.camera_y // TILE_SIZE
        viewport_w = min(SCREEN_WIDTH // TILE_SIZE, MAP_SIZE - viewport_x)
        viewport_h = min((SCREEN_HEIGHT - 36 - 32) // TILE_SIZE, MAP_SIZE - viewport_y)  # Account for UI panels
        
        # Scale viewport position for minimap
        scaled_vp_x = viewport_x * minimap_display_size // MAP_SIZE
        scaled_vp_y = viewport_y * minimap_display_size // MAP_SIZE
        scaled_vp_w = viewport_w * minimap_display_size // MAP_SIZE
        scaled_vp_h = viewport_h * minimap_display_size // MAP_SIZE
        
        # Draw viewport border (white rectangle)
        for i in range(scaled_vp_w):
            pyxel.pset(minimap_x + scaled_vp_x + i, minimap_y + scaled_vp_y, 7)
            pyxel.pset(minimap_x + scaled_vp_x + i, minimap_y + scaled_vp_y + scaled_vp_h - 1, 7)
        for i in range(scaled_vp_h):
            pyxel.pset(minimap_x + scaled_vp_x, minimap_y + scaled_vp_y + i, 7)
            pyxel.pset(minimap_x + scaled_vp_x + scaled_vp_w - 1, minimap_y + scaled_vp_y + i, 7)
        
        # Add minimap click handling in update
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mouse_x = pyxel.mouse_x
            mouse_y = pyxel.mouse_y
            
            # Check if click is within minimap
            if (minimap_x <= mouse_x < minimap_x + minimap_display_size and
                minimap_y <= mouse_y < minimap_y + minimap_display_size):
                # Calculate new camera position (unscale from 80x80 to 100x100)
                map_x = (mouse_x - minimap_x) * MAP_SIZE // minimap_display_size
                map_y = (mouse_y - minimap_y) * MAP_SIZE // minimap_display_size
                
                # Center the viewport on the clicked position
                new_camera_x = (map_x * TILE_SIZE) - (SCREEN_WIDTH // 2)
                new_camera_y = (map_y * TILE_SIZE) - ((SCREEN_HEIGHT - 36 - 32) // 2)
                
                # Clamp camera position
                max_camera_x = MAP_SIZE * TILE_SIZE - SCREEN_WIDTH
                max_camera_y = MAP_SIZE * TILE_SIZE - (SCREEN_HEIGHT - 36 - 32)
                self.camera_x = max(0, min(new_camera_x, max_camera_x))
                self.camera_y = max(0, min(new_camera_y, max_camera_y))
                
                # Update movement state
                self.is_moving = True
                self.move_timer = 30
                self.prev_camera_x = self.camera_x
                self.prev_camera_y = self.camera_y

if __name__ == "__main__":
    import sys

    # Check if GameLauncher should be used
    # Default: direct launch for now (will change to GameLauncher after testing)
    USE_GAME_LAUNCHER = True  # Set to True to enable title menu system

    if USE_GAME_LAUNCHER:
        from title_menu_system import GameLauncher
        launcher = GameLauncher(SCREEN_WIDTH, SCREEN_HEIGHT)
    else:
        # Direct launch (original behavior)
        ConcLandMini()