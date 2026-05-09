"""
Utility functions for the city simulation game
"""

def clamp(value, min_val, max_val):
    """Clamp a value between min and max"""
    return max(min_val, min(max_val, value))

def manhattan_distance(x1, y1, x2, y2):
    """Calculate Manhattan distance between two points"""
    return abs(x1 - x2) + abs(y1 - y2)

def is_in_bounds(x, y, width, height):
    """Check if coordinates are within bounds"""
    return 0 <= x < width and 0 <= y < height

def get_neighbors(x, y, width, height, diagonal=False):
    """Get valid neighboring coordinates"""
    neighbors = []
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    
    if diagonal:
        directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])
    
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if is_in_bounds(nx, ny, width, height):
            neighbors.append((nx, ny))
    
    return neighbors

def interpolate_color(color1, color2, factor):
    """Interpolate between two RGB colors"""
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    
    r = int(r1 + (r2 - r1) * factor)
    g = int(g1 + (g2 - g1) * factor)
    b = int(b1 + (b2 - b1) * factor)
    
    return (r, g, b)