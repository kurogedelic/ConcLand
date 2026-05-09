"""
ゲーム設定ファイル
Game Configuration File

このファイルにはConcLandのすべての設定値が含まれます。
外部化することで、ゲームバランスの調整が容易になります。
"""

# ========================================
# 画面設定 / Screen Settings
# ========================================
SCREEN_WIDTH = 800  # 画面幅
SCREEN_HEIGHT = 600  # 画面高さ
GAME_TITLE = "ConcLand Mini - City Simulation Game"  # ゲームタイトル

# ========================================
# マップ設定 / Map Settings
# ========================================
MAP_SIZE = 100  # マップサイズ (100x100タイル)
TILE_SIZE = 8   # タイルサイズ (8x8ピクセル)
VIEWPORT_WIDTH = 64   # ビューポート幅（タイル数）
VIEWPORT_HEIGHT = 64  # ビューポート高さ（タイル数）

# ========================================
# ゲームプレイ設定 / Gameplay Settings
# ========================================
# 初期資金
INITIAL_FUNDS_NORMAL = 5000  # 通常モード初期資金
INITIAL_FUNDS_DEV = 10000    # 開発モード初期資金

# シミュレーション速度
SIM_SPEED_NORMAL = 60  # 通常速度（フレーム）
SIM_SPEED_FAST = 30    # 高速
SIM_SPEED_SLOW = 120   # 低速

# ========================================
# 建物コスト / Building Costs
# ========================================
BUILDING_COSTS = {
    "RESIDENTIAL": 10,    # 住宅ゾーン
    "COMMERCIAL": 15,     # 商業ゾーン
    "INDUSTRIAL": 20,     # 工業ゾーン
    "ROAD": 5,           # 道路
    "RAIL": 20,          # 鉄道
    "WIRE": 10,          # 電線
    "PARK": 30,          # 公園
    "COAL_PLANT": 500,   # 石炭発電所
    "NUCLEAR_PLANT": 2000,  # 原子力発電所
    "GAS_PLANT": 800,    # ガス発電所
    "OIL_PLANT": 1000,   # 石油発電所
    "SOLAR_PLANT": 1500, # 太陽光発電所
    "WIND_PLANT": 300,   # 風力発電所
    "POLICE": 200,       # 警察署
    "FIRE": 200,         # 消防署
    "HOSPITAL": 500,     # 病院
    "SCHOOL": 300,       # 学校
    "UNIVERSITY": 800,   # 大学
    "LIBRARY": 200,      # 図書館
    "PUMP": 150,         # ポンプ場
    "WATER_PLANT": 400,  # 浄水場
    "SEWAGE_PLANT": 350, # 下水処理場
}

# 維持費（月額）
MAINTENANCE_COSTS = {
    "POLICE": 20,
    "FIRE": 20,
    "HOSPITAL": 50,
    "SCHOOL": 30,
    "POWER_PLANT": 100,
}

# ========================================
# シミュレーション設定 / Simulation Settings
# ========================================
# 人口設定
MAX_POPULATION_PER_CELL = 400  # セルごとの最大人口
POPULATION_GROWTH_RATE = 0.02  # 人口成長率

# 汚染設定
POLLUTION_SPREAD_RATE = 0.25   # 汚染拡散率
POLLUTION_DECAY_RATE = 0.8     # 汚染減衰率
INDUSTRIAL_POLLUTION = 50       # 工業地帯の汚染発生量

# 地価設定
BASE_LAND_VALUE = 100          # 基本地価
LAND_VALUE_DECAY = 0.9         # 地価減衰率
PARK_LAND_VALUE_BONUS = 10    # 公園による地価ボーナス
COMMERCIAL_LAND_VALUE_BONUS = 5  # 商業地による地価ボーナス

# 交通設定
ROAD_CAPACITY = 100      # 道路容量
RAIL_CAPACITY = 400      # 鉄道容量
TRAFFIC_THRESHOLD = 150  # 渋滞閾値

# ========================================
# RCI需要設定 / RCI Demand Settings
# ========================================
# 需要バランス
RESIDENTIAL_DEMAND_BASE = 50   # 住宅需要ベース
COMMERCIAL_DEMAND_BASE = 30    # 商業需要ベース
INDUSTRIAL_DEMAND_BASE = 40    # 工業需要ベース

# 需要変動幅
DEMAND_FLUCTUATION = 20        # 需要変動幅
DEMAND_UPDATE_INTERVAL = 120   # 需要更新間隔（フレーム）

# ========================================
# 災害設定 / Disaster Settings
# ========================================
DISASTER_PROBABILITY = {
    "EARTHQUAKE": 0.0001,  # 地震発生確率
    "FIRE": 0.0002,        # 火災発生確率
    "TYPHOON": 0.0001,     # 台風発生確率
    "TSUNAMI": 0.00005,    # 津波発生確率
}

DISASTER_DAMAGE = {
    "EARTHQUAKE": 100,     # 地震ダメージ
    "FIRE": 50,           # 火災ダメージ
    "TYPHOON": 75,        # 台風ダメージ
    "TSUNAMI": 150,       # 津波ダメージ
}

# ========================================
# UI設定 / UI Settings
# ========================================
# パレット設定
PALETTE_HEIGHT = 24     # パレット高さ
INFO_PANEL_HEIGHT = 32  # 情報パネル高さ
MAP_BAR_HEIGHT = 16     # マップバー高さ

# 色設定（パレットインデックス）
COLORS = {
    "BLACK": 0,
    "WHITE": 7,
    "RED": 8,
    "GREEN": 3,
    "BLUE": 2,
    "YELLOW": 10,
    "CYAN": 12,
    "GRAY": 5,
    "DARK_GRAY": 13,
}

# ========================================
# デバッグ設定 / Debug Settings
# ========================================
DEBUG_MODE = False          # デバッグモード
DEV_MODE = True            # 開発モード（無限資金）
SHOW_FPS = False           # FPS表示
SHOW_GRID = False          # グリッド表示
SHOW_DEBUG_INFO = False    # デバッグ情報表示

# ========================================
# セーブ/ロード設定 / Save/Load Settings
# ========================================
SAVE_FILE = "savegame.dat"      # セーブファイル名
TERRAIN_FILE = "terrain_100.dat" # 地形ファイル名
AUTO_SAVE_INTERVAL = 600        # 自動保存間隔（秒）
MAX_SAVE_BACKUPS = 3            # バックアップ最大数

# ========================================
# パフォーマンス設定 / Performance Settings
# ========================================
# 更新間隔（フレーム単位）
POLLUTION_UPDATE_INTERVAL = 4   # 汚染更新間隔
LAND_VALUE_UPDATE_INTERVAL = 8  # 地価更新間隔
RCI_GROWTH_UPDATE_INTERVAL = 16 # RCI成長更新間隔
TRAFFIC_UPDATE_INTERVAL = 10    # 交通更新間隔

# バッチサイズ
UPDATE_BATCH_SIZE = 100  # 一度に更新するタイル数
RENDER_BATCH_SIZE = 64   # 一度にレンダリングするタイル数

# ========================================
# モジュール設定 / Module Settings
# ========================================
# 有効化するモジュール
ENABLE_TRAFFIC_SYSTEM = True     # 交通システム
ENABLE_ECONOMIC_SYSTEM = True    # 経済システム
ENABLE_DISASTER_SYSTEM = True    # 災害システム
ENABLE_SOUND_SYSTEM = True        # サウンドシステム
ENABLE_VISUAL_SYSTEM = True       # ビジュアルシステム

# モジュールインポートパス
MODULE_PATHS = {
    "traffic": "traffic_system",
    "economy": "economic_system",
    "disaster": "disaster_system",
    "sound": "sound_effects_system",
    "visual": "visual_system",
}

# ========================================
# 言語設定 / Language Settings
# ========================================
DEFAULT_LANGUAGE = "ja"  # デフォルト言語（ja: 日本語, en: 英語）

# UI文字列
UI_STRINGS = {
    "ja": {
        "funds": "資金",
        "population": "人口",
        "employment": "雇用",
        "gdp": "GDP",
        "year": "年",
        "month": "月",
    },
    "en": {
        "funds": "Funds",
        "population": "Population",
        "employment": "Employment",
        "gdp": "GDP",
        "year": "Year",
        "month": "Month",
    }
}