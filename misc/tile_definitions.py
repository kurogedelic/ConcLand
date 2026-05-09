"""Tile definitions for city simulation tilemap"""

# Tile size constants
TILE_SIZE = 8
TILEMAP_WIDTH = 32  # tiles per row
TILEMAP_HEIGHT = 32  # tiles per column

# Helper function to convert row/col to tile index
def tile_index(row, col):
    return row * TILEMAP_WIDTH + col

# Terrain tiles (Row 0-1)
TERRAIN = {
    'GRASS': tile_index(0, 0),
    'SOIL': tile_index(0, 1),
    'DIRT': tile_index(0, 2),
    'SAND': tile_index(0, 3),
}

# Water tiles (Row 2-3) - 4 animation frames
WATER = {
    'STILL': tile_index(2, 0),
    'FLOW_1': tile_index(2, 1),
    'FLOW_2': tile_index(2, 2),
    'FLOW_3': tile_index(2, 3),
    'SHORE_N': tile_index(2, 4),
    'SHORE_E': tile_index(2, 5),
    'SHORE_S': tile_index(2, 6),
    'SHORE_W': tile_index(2, 7),
}

# Residential tiles (Row 4-7)
RESIDENTIAL = {
    'EMPTY': tile_index(4, 0),
    'MAKING_1': tile_index(4, 1),
    'MAKING_2': tile_index(4, 2),
    # Low density (8x8)
    'LOW_1': tile_index(5, 0),
    'LOW_2': tile_index(5, 1),
    'LOW_3': tile_index(5, 2),
    'LOW_4': tile_index(5, 3),
    # Middle density (16x16) - top-left corner
    'MIDDLE_1': tile_index(6, 0),
    'MIDDLE_2': tile_index(6, 4),
    'MIDDLE_3': tile_index(6, 8),
    'MIDDLE_4': tile_index(6, 12),
    # High density (32x32) - top-left corner
    'HIGH_1': tile_index(7, 0),
    'HIGH_2': tile_index(7, 8),
}

# Commercial tiles (Row 8-11)
COMMERCIAL = {
    'EMPTY': tile_index(8, 0),
    'MAKING_1': tile_index(8, 1),
    'MAKING_2': tile_index(8, 2),
    # Low density (8x8)
    'LOW_1': tile_index(9, 0),
    'LOW_2': tile_index(9, 1),
    'LOW_3': tile_index(9, 2),
    'LOW_4': tile_index(9, 3),
    # Middle density (16x16)
    'MIDDLE_1': tile_index(10, 0),
    'MIDDLE_2': tile_index(10, 4),
    'MIDDLE_3': tile_index(10, 8),
    'MIDDLE_4': tile_index(10, 12),
    # High density (32x32)
    'HIGH_1': tile_index(11, 0),
    'HIGH_2': tile_index(11, 8),
}

# Industrial tiles (Row 12-15)
INDUSTRIAL = {
    'EMPTY': tile_index(12, 0),
    'MAKING_1': tile_index(12, 1),
    'MAKING_2': tile_index(12, 2),
    # Low density (8x8)
    'LOW_1': tile_index(13, 0),
    'LOW_2': tile_index(13, 1),
    'LOW_3': tile_index(13, 2),
    'LOW_4': tile_index(13, 3),
    # Middle density (16x16)
    'MIDDLE_1': tile_index(14, 0),
    'MIDDLE_2': tile_index(14, 4),
    'MIDDLE_3': tile_index(14, 8),
    'MIDDLE_4': tile_index(14, 12),
    # High density (32x32)
    'HIGH_1': tile_index(15, 0),
    'HIGH_2': tile_index(15, 8),
}

# Agricultural tiles (Row 16-17)
AGRICULTURAL = {
    'FIELD_EMPTY': tile_index(16, 0),
    'FIELD_SEED': tile_index(16, 1),
    'FIELD_GROW': tile_index(16, 2),
    'FIELD_READY': tile_index(16, 3),
    'GREENHOUSE': tile_index(16, 4),  # 16x16
    'RANCH': tile_index(17, 0),  # 32x32
}

# Road tiles (Row 18-19) - Connection patterns
ROAD = {
    'HORIZONTAL': tile_index(18, 0),     # ━
    'VERTICAL': tile_index(18, 1),       # ┃
    'CORNER_NE': tile_index(18, 2),      # ┏
    'CORNER_SE': tile_index(18, 3),      # ┓
    'CORNER_SW': tile_index(18, 4),      # ┛
    'CORNER_NW': tile_index(18, 5),      # ┗
    'T_EAST': tile_index(18, 6),         # ┣
    'T_WEST': tile_index(18, 7),         # ┫
    'T_SOUTH': tile_index(18, 8),        # ┳
    'T_NORTH': tile_index(18, 9),        # ┻
    'CROSS': tile_index(18, 10),         # ╋
    'END_N': tile_index(18, 11),         # End pieces
    'END_E': tile_index(18, 12),
    'END_S': tile_index(18, 13),
    'END_W': tile_index(18, 14),
    'ALONE': tile_index(18, 15),         # Single road
}

# Power facilities (Row 20-23)
POWER = {
    'WIND_1': tile_index(20, 0),  # Wind animation
    'WIND_2': tile_index(20, 1),
    'WIND_3': tile_index(20, 2),
    'SOLAR': tile_index(20, 4),   # 16x16
    'COAL': tile_index(21, 0),    # 32x32
    'GAS': tile_index(22, 0),     # 32x32
    'NUCLEAR': tile_index(23, 0), # 32x32
    # Power lines (similar to roads)
    'LINE_H': tile_index(20, 8),
    'LINE_V': tile_index(20, 9),
    'LINE_CORNER_NE': tile_index(20, 10),
    'LINE_CORNER_SE': tile_index(20, 11),
    'LINE_CORNER_SW': tile_index(20, 12),
    'LINE_CORNER_NW': tile_index(20, 13),
    'LINE_T': tile_index(20, 14),
    'LINE_CROSS': tile_index(20, 15),
}

# Public facilities (Row 24-27)
PUBLIC = {
    'POLICE_SMALL': tile_index(24, 0),   # 8x8
    'POLICE': tile_index(24, 1),         # 16x16
    'FIRE': tile_index(24, 4),           # 16x16
    'HOSPITAL_SMALL': tile_index(25, 0), # 16x16
    'HOSPITAL': tile_index(25, 4),       # 32x32
    'SCHOOL_ELEM': tile_index(26, 0),    # 16x16
    'SCHOOL_HIGH': tile_index(26, 4),    # 24x24
    'UNIVERSITY': tile_index(27, 0),     # 32x32
}

# Parks and Nature (Row 28-29)
PARK = {
    'SMALL_1': tile_index(28, 0),  # 8x8
    'SMALL_2': tile_index(28, 1),
    'SMALL_3': tile_index(28, 2),
    'SMALL_4': tile_index(28, 3),
    'MEDIUM': tile_index(28, 4),   # 16x16
    'LARGE': tile_index(28, 8),    # 32x32
    'TREE_1': tile_index(29, 0),   # 8x8
    'TREE_2': tile_index(29, 1),
    'TREE_3': tile_index(29, 2),
    'TREE_4': tile_index(29, 3),
}

# Effects (Row 30-31)
EFFECTS = {
    'FIRE_1': tile_index(30, 0),  # Fire animation
    'FIRE_2': tile_index(30, 1),
    'FIRE_3': tile_index(30, 2),
    'FIRE_4': tile_index(30, 3),
    'SMOKE_1': tile_index(30, 4), # Smoke animation
    'SMOKE_2': tile_index(30, 5),
    'SMOKE_3': tile_index(30, 6),
    'CONSTRUCT_1': tile_index(31, 0),  # Construction animation
    'CONSTRUCT_2': tile_index(31, 1),
    'CONSTRUCT_3': tile_index(31, 2),
    'CONSTRUCT_4': tile_index(31, 3),
}

# Tile size definitions (in 8px units)
TILE_SIZES = {
    # 1x1 (8x8px)
    'small': (1, 1),
    # 2x2 (16x16px)
    'medium': (2, 2),
    # 3x3 (24x24px)
    'large': (3, 3),
    # 4x4 (32x32px)
    'xlarge': (4, 4),
}

# Building size mapping
BUILDING_SIZES = {
    'residential_low': 'small',
    'residential_middle': 'medium',
    'residential_high': 'xlarge',
    'commercial_low': 'small',
    'commercial_middle': 'medium',
    'commercial_high': 'xlarge',
    'industrial_low': 'small',
    'industrial_middle': 'medium',
    'industrial_high': 'xlarge',
    'agricultural_field': 'small',
    'agricultural_greenhouse': 'medium',
    'agricultural_ranch': 'xlarge',
    'power_wind': 'small',
    'power_solar': 'medium',
    'power_coal': 'xlarge',
    'power_gas': 'xlarge',
    'power_nuclear': 'xlarge',
}

def get_road_tile(north=False, east=False, south=False, west=False):
    """Get appropriate road tile based on connections"""
    connections = (north, east, south, west)
    
    # Map connection patterns to tiles
    patterns = {
        (False, False, False, False): ROAD['ALONE'],
        (False, True, False, True): ROAD['HORIZONTAL'],
        (True, False, True, False): ROAD['VERTICAL'],
        (False, True, True, False): ROAD['CORNER_NE'],
        (False, False, True, True): ROAD['CORNER_SE'],
        (True, False, False, True): ROAD['CORNER_SW'],
        (True, True, False, False): ROAD['CORNER_NW'],
        (True, True, True, False): ROAD['T_EAST'],
        (True, False, True, True): ROAD['T_WEST'],
        (False, True, True, True): ROAD['T_SOUTH'],
        (True, True, False, True): ROAD['T_NORTH'],
        (True, True, True, True): ROAD['CROSS'],
        (True, False, False, False): ROAD['END_N'],
        (False, True, False, False): ROAD['END_E'],
        (False, False, True, False): ROAD['END_S'],
        (False, False, False, True): ROAD['END_W'],
    }
    
    return patterns.get(connections, ROAD['ALONE'])

def get_tile_rect(tile_index):
    """Get source rectangle for a tile index"""
    row = tile_index // TILEMAP_WIDTH
    col = tile_index % TILEMAP_WIDTH
    return (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)