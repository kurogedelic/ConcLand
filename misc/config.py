"""
Configuration constants for the city simulation game
"""

# Screen and UI dimensions
SCREEN_WIDTH = 512
SCREEN_HEIGHT = 342
STATUS_HEIGHT = 32
PALETTE_WIDTH = 128

# Cell and building sizes
CELL_SIZE = 8  # Base cell size in pixels
STANDARD_SIZE = 32  # Standard building size (4x4 cells)

# Map configuration
MAP_SIZE = 64  # 64x64 cells
TERRAIN_REGIONS = 15  # Number of Voronoi regions for terrain generation

# Game mechanics
UPDATE_INTERVAL = 30  # Frames between simulation updates
CENSUS_RATE = 4  # Simulation ticks between census updates
ANIMATION_WATER_RATE = 15  # Frames between water animation updates
ANIMATION_OTHER_RATE = 20  # Frames between other animation updates

# Power system configuration
POWER_FACILITIES = {
    'POWERPLANT': {'range': 20, 'strength': 100, 'capacity': 300},
    'NUCLEAR': {'range': 30, 'strength': 150, 'capacity': 1200},
    'GAS': {'range': 15, 'strength': 80, 'capacity': 500},
    'SOLAR': {'range': 8, 'strength': 40, 'capacity': 150},
    'WIND': {'range': 6, 'strength': 30, 'capacity': 50}
}

# Economy
INITIAL_FUNDS = 10000
TAX_RATE_MIN = 0
TAX_RATE_MAX = 20
TAX_RATE_DEFAULT = 7

# Zone growth parameters
MAX_ROAD_DISTANCE = 3  # Maximum distance from road for zone growth
GROWTH_RATE_THRESHOLD = 10  # Random threshold for growth

# RCI demand balance targets
TARGET_RATIOS = {
    'residential': 0.5,   # 50% residential
    'commercial': 0.3,    # 30% commercial
    'industrial': 0.2     # 20% industrial
}

# Minimap configuration
MINIMAP_SCALE = 2  # 1 pixel = 2x2 cells
MINIMAP_X = 4
MINIMAP_Y = STATUS_HEIGHT + 4

# Color indices (Pyxel palette)
COLORS = {
    'BLACK': 0,
    'DARK_BLUE': 1,
    'DARK_PURPLE': 2,
    'DARK_GREEN': 3,
    'BROWN': 4,
    'DARK_GRAY': 5,
    'LIGHT_GRAY': 6,
    'WHITE': 7,
    'RED': 8,
    'ORANGE': 9,
    'YELLOW': 10,
    'GREEN': 11,
    'BLUE': 12,
    'INDIGO': 13,
    'PINK': 14,
    'PEACH': 15
}

# Building cost configuration
BUILDING_COSTS = {
    'RESIDENCE': 100,
    'COMMERCIAL': 150,
    'INDUSTRIAL': 200,
    'ROAD': 10,
    'POWERPLANT': 3000,
    'NUCLEAR': 5000,
    'GAS': 2000,
    'SOLAR': 1000,
    'WIND': 500,
    'AGRICULTURAL': 300,
    'PARK': 50,
    'SHRINE': 100
}