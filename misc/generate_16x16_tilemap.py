"""
Generate 16x16 tilemap for ConcLand Mini from existing 8x8 tiles
"""

import pyxel
from PIL import Image, ImageDraw
import os

def create_16x16_tilemap():
    """Create a 16x16 tilemap for ConcLand Mini"""
    
    # Create a new image for the 16x16 tilemap
    tilemap_width = 256
    tilemap_height = 256
    tilemap = Image.new('RGBA', (tilemap_width, tilemap_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(tilemap)
    
    # Define colors for different tile types
    colors = {
        'empty': (34, 32, 52),      # Dark purple
        'grass': (69, 107, 60),     # Green
        'water': (69, 86, 130),     # Blue
        'residential': (141, 165, 132),  # Light green
        'commercial': (130, 151, 185),   # Light blue
        'industrial': (133, 122, 112),   # Brown
        'road': (89, 86, 82),       # Dark gray
        'rail': (115, 111, 107),    # Light gray
        'wire': (194, 133, 71),     # Orange
        'park': (99, 155, 85),      # Bright green
        'coal_plant': (71, 71, 71), # Dark gray
        'oil_plant': (89, 89, 89),  # Medium gray
        'nuclear_plant': (115, 115, 130), # Light gray-blue
        'police': (69, 86, 185),    # Police blue
        'fire': (185, 69, 69),      # Fire red
        'hospital': (185, 185, 185), # White
        'school': (185, 151, 69),   # Yellow
    }
    
    # Draw basic terrain tiles
    # Empty/grass
    draw.rectangle([0, 0, 15, 15], fill=colors['empty'])
    draw.rectangle([16, 0, 31, 15], fill=colors['grass'])
    draw.rectangle([32, 0, 47, 15], fill=colors['water'])
    
    # Draw residential tiles (different densities)
    for i in range(4):
        x = i * 16
        y = 16
        color = colors['residential']
        # Make higher density darker
        if i > 0:
            r, g, b = color
            factor = 1 - (i * 0.1)
            color = (int(r * factor), int(g * factor), int(b * factor))
        draw.rectangle([x, y, x+15, y+15], fill=color)
        # Add simple building pattern
        if i > 0:
            for j in range(i+1):
                draw.rectangle([x+2+j*3, y+2, x+4+j*3, y+13], fill=(200, 200, 200))
    
    # Draw commercial tiles
    for i in range(4):
        x = i * 16
        y = 32
        color = colors['commercial']
        if i > 0:
            r, g, b = color
            factor = 1 - (i * 0.1)
            color = (int(r * factor), int(g * factor), int(b * factor))
        draw.rectangle([x, y, x+15, y+15], fill=color)
        # Add commercial pattern
        if i > 0:
            for j in range(i+1):
                draw.rectangle([x+1+j*4, y+1, x+3+j*4, y+14], fill=(180, 180, 220))
    
    # Draw industrial tiles
    for i in range(4):
        x = i * 16
        y = 48
        color = colors['industrial']
        if i > 0:
            r, g, b = color
            factor = 1 - (i * 0.1)
            color = (int(r * factor), int(g * factor), int(b * factor))
        draw.rectangle([x, y, x+15, y+15], fill=color)
        # Add industrial pattern
        if i > 0:
            for j in range(i):
                draw.rectangle([x+2+j*5, y+2, x+5+j*5, y+13], fill=(100, 100, 100))
    
    # Draw road tiles with connections
    road_y = 64
    road_patterns = [
        ('alone', [(6, 6, 9, 9)]),  # Single road piece
        ('horizontal', [(0, 6, 15, 9)]),  # Horizontal road
        ('vertical', [(6, 0, 9, 15)]),  # Vertical road
        ('corner_ne', [(6, 6, 15, 9), (6, 0, 9, 6)]),  # Northeast corner
        ('corner_se', [(6, 6, 15, 9), (6, 9, 9, 15)]),  # Southeast corner
        ('corner_sw', [(0, 6, 9, 9), (6, 9, 9, 15)]),  # Southwest corner
        ('corner_nw', [(0, 6, 9, 9), (6, 0, 9, 6)]),  # Northwest corner
        ('cross', [(0, 6, 15, 9), (6, 0, 9, 15)]),  # Crossroads
        ('t_north', [(0, 6, 15, 9), (6, 6, 9, 15)]),  # T-junction north
        ('t_south', [(0, 6, 15, 9), (6, 0, 9, 9)]),  # T-junction south
        ('t_east', [(6, 0, 9, 15), (0, 6, 9, 9)]),  # T-junction east
        ('t_west', [(6, 0, 9, 15), (6, 6, 15, 9)]),  # T-junction west
    ]
    
    for i, (pattern_name, rects) in enumerate(road_patterns):
        x = i * 16
        # Draw grass background
        draw.rectangle([x, road_y, x+15, road_y+15], fill=colors['grass'])
        # Draw road pattern
        for rect in rects:
            draw.rectangle([x+rect[0], road_y+rect[1], x+rect[2], road_y+rect[3]], fill=colors['road'])
    
    # Draw rail tiles (similar to roads but different color)
    rail_y = 80
    rail_patterns = [
        ('alone', [(7, 7, 8, 8)]),
        ('horizontal', [(0, 7, 15, 8)]),
        ('vertical', [(7, 0, 8, 15)]),
        ('corner_ne', [(7, 7, 15, 8), (7, 0, 8, 7)]),
        ('corner_se', [(7, 7, 15, 8), (7, 8, 8, 15)]),
        ('corner_sw', [(0, 7, 8, 8), (7, 8, 8, 15)]),
        ('corner_nw', [(0, 7, 8, 8), (7, 0, 8, 7)]),
        ('cross', [(0, 7, 15, 8), (7, 0, 8, 15)]),
    ]
    
    for i, (pattern_name, rects) in enumerate(rail_patterns):
        x = i * 16
        # Draw grass background
        draw.rectangle([x, rail_y, x+15, rail_y+15], fill=colors['grass'])
        # Draw rail pattern
        for rect in rects:
            draw.rectangle([x+rect[0], rail_y+rect[1], x+rect[2], rail_y+rect[3]], fill=colors['rail'])
            # Add rail ties
            if pattern_name in ['horizontal', 'cross']:
                for j in range(2, 14, 3):
                    draw.rectangle([x+j, rail_y+5, x+j+1, rail_y+10], fill=(71, 71, 71))
            if pattern_name in ['vertical', 'cross']:
                for j in range(2, 14, 3):
                    draw.rectangle([x+5, rail_y+j, x+10, rail_y+j+1], fill=(71, 71, 71))
    
    # Draw infrastructure tiles
    infra_y = 96
    # Wire
    draw.rectangle([0, infra_y, 15, infra_y+15], fill=colors['grass'])
    draw.rectangle([7, infra_y, 8, infra_y+15], fill=colors['wire'])
    draw.rectangle([0, infra_y+7, 15, infra_y+8], fill=colors['wire'])
    # Park
    draw.rectangle([16, infra_y, 31, infra_y+15], fill=colors['park'])
    # Add trees to park
    for i in range(2):
        for j in range(2):
            draw.ellipse([16+2+i*6, infra_y+2+j*6, 16+6+i*6, infra_y+6+j*6], fill=(69, 107, 60))
    
    # Draw power plants (3x3 buildings shown as single tiles)
    plant_y = 112
    # Coal plant
    draw.rectangle([0, plant_y, 15, plant_y+15], fill=colors['coal_plant'])
    draw.rectangle([2, plant_y+2, 13, plant_y+13], fill=(51, 51, 51))
    # Smoke stacks
    draw.rectangle([4, plant_y+2, 6, plant_y+8], fill=(31, 31, 31))
    draw.rectangle([9, plant_y+2, 11, plant_y+8], fill=(31, 31, 31))
    
    # Oil plant
    draw.rectangle([16, plant_y, 31, plant_y+15], fill=colors['oil_plant'])
    draw.rectangle([18, plant_y+2, 29, plant_y+13], fill=(71, 71, 71))
    draw.ellipse([20, plant_y+4, 27, plant_y+11], fill=(51, 51, 51))
    
    # Nuclear plant
    draw.rectangle([32, plant_y, 47, plant_y+15], fill=colors['nuclear_plant'])
    draw.ellipse([34, plant_y+2, 45, plant_y+13], fill=(95, 95, 110))
    draw.rectangle([37, plant_y+2, 42, plant_y+8], fill=(75, 75, 90))
    
    # Draw public service buildings
    service_y = 128
    # Police
    draw.rectangle([0, service_y, 15, service_y+15], fill=colors['police'])
    draw.rectangle([2, service_y+2, 13, service_y+13], fill=(49, 66, 165))
    draw.rectangle([6, service_y+5, 9, service_y+10], fill=(255, 255, 255))
    
    # Fire
    draw.rectangle([16, service_y, 31, service_y+15], fill=colors['fire'])
    draw.rectangle([18, service_y+2, 29, service_y+13], fill=(165, 49, 49))
    draw.rectangle([22, service_y+5, 25, service_y+10], fill=(255, 255, 255))
    
    # Hospital
    draw.rectangle([32, service_y, 47, service_y+15], fill=colors['hospital'])
    draw.rectangle([34, service_y+2, 45, service_y+13], fill=(165, 165, 165))
    # Red cross
    draw.rectangle([38, service_y+4, 41, service_y+11], fill=(185, 69, 69))
    draw.rectangle([36, service_y+6, 43, service_y+9], fill=(185, 69, 69))
    
    # School
    draw.rectangle([48, service_y, 63, service_y+15], fill=colors['school'])
    draw.rectangle([50, service_y+2, 61, service_y+13], fill=(165, 131, 49))
    draw.rectangle([53, service_y+5, 58, service_y+10], fill=(255, 255, 255))
    
    # Save the tilemap
    output_path = 'assets/concland_tiles_16x16.png'
    tilemap.save(output_path)
    print(f"Generated 16x16 tilemap: {output_path}")
    
    return output_path

if __name__ == "__main__":
    create_16x16_tilemap()