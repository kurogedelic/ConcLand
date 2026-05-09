#!/usr/bin/env python3
"""
Generate placeholder graphics assets for ConcLand Mini
Creates 16x16 tile graphics and 256-color palette
"""

from PIL import Image, ImageDraw
import os

# Ensure assets directory exists
os.makedirs("assets", exist_ok=True)

def create_16x16_tiles():
    """Create placeholder 16x16 tile graphics"""
    # Create a large image to hold all tiles
    tile_size = 16
    tiles_per_row = 8
    num_tiles = 16
    rows = (num_tiles + tiles_per_row - 1) // tiles_per_row
    
    image_width = tiles_per_row * tile_size
    image_height = rows * tile_size
    
    # Create the image with transparency
    tileset = Image.new('RGBA', (image_width, image_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(tileset)
    
    # Define tile colors and patterns
    tiles = [
        # 0: Empty/Grass
        {'color': (34, 139, 34), 'pattern': 'solid'},
        # 1: Residential
        {'color': (100, 149, 237), 'pattern': 'house'},
        # 2: Commercial  
        {'color': (144, 238, 144), 'pattern': 'building'},
        # 3: Industrial
        {'color': (139, 69, 19), 'pattern': 'factory'},
        # 4: Road
        {'color': (105, 105, 105), 'pattern': 'road'},
        # 5: Rail
        {'color': (25, 25, 112), 'pattern': 'rail'},
        # 6: Wire
        {'color': (255, 165, 0), 'pattern': 'wire'},
        # 7: Park
        {'color': (0, 255, 0), 'pattern': 'trees'},
        # 8: Water
        {'color': (0, 191, 255), 'pattern': 'water'},
        # 9: Coal Plant
        {'color': (128, 0, 128), 'pattern': 'smokestack'},
        # 10: Oil Plant
        {'color': (255, 0, 0), 'pattern': 'tower'},
        # 11: Nuclear Plant
        {'color': (255, 255, 255), 'pattern': 'dome'},
        # 12: Police
        {'color': (0, 0, 139), 'pattern': 'shield'},
        # 13: Fire Station
        {'color': (255, 0, 0), 'pattern': 'cross'},
        # 14: Hospital
        {'color': (255, 255, 255), 'pattern': 'plus'},
        # 15: School
        {'color': (255, 165, 0), 'pattern': 'book'}
    ]
    
    for i, tile_info in enumerate(tiles):
        row = i // tiles_per_row
        col = i % tiles_per_row
        
        x = col * tile_size
        y = row * tile_size
        
        color = tile_info['color']
        pattern = tile_info['pattern']
        
        # Draw base tile
        draw.rectangle([x, y, x + tile_size - 1, y + tile_size - 1], fill=color)
        
        # Add pattern details
        if pattern == 'house':
            # Simple house shape
            draw.rectangle([x + 3, y + 6, x + 12, y + 14], fill=(139, 69, 19))  # House body
            draw.polygon([x + 2, y + 6, x + 8, y + 2, x + 13, y + 6], fill=(178, 34, 34))  # Roof
            draw.rectangle([x + 6, y + 10, x + 9, y + 14], fill=(101, 67, 33))  # Door
            
        elif pattern == 'building':
            # Commercial building
            draw.rectangle([x + 2, y + 4, x + 13, y + 14], fill=(169, 169, 169))
            for floor in range(2):
                for window in range(3):
                    draw.rectangle([x + 4 + window * 3, y + 6 + floor * 3, 
                                   x + 5 + window * 3, y + 7 + floor * 3], fill=(135, 206, 235))
                    
        elif pattern == 'factory':
            # Industrial building with smokestack
            draw.rectangle([x + 2, y + 6, x + 13, y + 14], fill=(105, 105, 105))
            draw.rectangle([x + 10, y + 2, x + 12, y + 6], fill=(139, 69, 19))  # Smokestack
            draw.ellipse([x + 9, y + 1, x + 13, y + 4], fill=(128, 128, 128))  # Smoke
            
        elif pattern == 'road':
            # Road with center line
            draw.line([x + 8, y, x + 8, y + 15], fill=(255, 255, 0), width=1)
            
        elif pattern == 'rail':
            # Railway tracks
            draw.rectangle([x + 6, y, x + 9, y + 15], fill=(139, 69, 19))  # Track base
            for i in range(4):
                draw.line([x + 3, y + 2 + i * 4, x + 12, y + 2 + i * 4], fill=(192, 192, 192))
                
        elif pattern == 'wire':
            # Power lines
            draw.line([x, y + 8, x + 15, y + 8], fill=(255, 255, 0), width=2)
            for i in range(3):
                draw.rectangle([x + 2 + i * 6, y + 4, x + 3 + i * 6, y + 12], fill=(139, 69, 19))
                
        elif pattern == 'trees':
            # Trees for park
            for tree in range(3):
                tree_x = x + 3 + tree * 4
                tree_y = y + 8
                draw.rectangle([tree_x, tree_y, tree_x + 1, tree_y + 6], fill=(139, 69, 19))
                draw.ellipse([tree_x - 2, tree_y - 3, tree_x + 3, tree_y + 2], fill=(0, 128, 0))
                
        elif pattern == 'water':
            # Water with waves
            for wave in range(3):
                draw.arc([x + 2, y + 2 + wave * 4, x + 13, y + 6 + wave * 4], 0, 180, fill=(65, 105, 225))
                
        elif pattern == 'smokestack':
            # Coal plant
            draw.rectangle([x + 2, y + 8, x + 13, y + 14], fill=(105, 105, 105))
            draw.rectangle([x + 6, y + 2, x + 9, y + 8], fill=(139, 69, 19))
            draw.ellipse([x + 4, y + 1, x + 11, y + 5], fill=(105, 105, 105))
            
        elif pattern == 'dome':
            # Nuclear plant
            draw.rectangle([x + 2, y + 10, x + 13, y + 14], fill=(192, 192, 192))
            draw.ellipse([x + 4, y + 4, x + 11, y + 11], fill=(220, 220, 220))
            
        elif pattern == 'shield':
            # Police badge
            points = [x + 8, y + 3, x + 11, y + 6, x + 10, y + 12, x + 6, y + 12, x + 5, y + 6]
            draw.polygon(points, fill=(255, 215, 0))
            
        elif pattern == 'plus':
            # Medical cross
            draw.rectangle([x + 6, y + 3, x + 9, y + 12], fill=(255, 0, 0))
            draw.rectangle([x + 3, y + 6, x + 12, y + 9], fill=(255, 0, 0))
        
        # Add border for visibility
        draw.rectangle([x, y, x + tile_size - 1, y + tile_size - 1], outline=(0, 0, 0), width=1)
    
    # Save the tileset
    tileset.save("assets/tiles_16x16.png")
    print("Created assets/tiles_16x16.png")

def create_256_palette():
    """Create a 256-color palette for extended colors"""
    palette_img = Image.new('RGB', (256, 1))
    
    # Create a gradual palette
    colors = []
    
    # Basic 16 colors (similar to Pyxel default)
    basic_colors = [
        (0, 0, 0),         # 0: Black
        (29, 43, 83),      # 1: Dark blue
        (126, 37, 83),     # 2: Dark purple
        (0, 135, 81),      # 3: Dark green
        (171, 82, 54),     # 4: Brown
        (95, 87, 79),      # 5: Dark gray
        (194, 195, 199),   # 6: Light gray
        (255, 241, 232),   # 7: White
        (255, 0, 77),      # 8: Red
        (255, 163, 0),     # 9: Orange
        (255, 236, 39),    # 10: Yellow
        (0, 228, 54),      # 11: Green
        (41, 173, 255),    # 12: Blue
        (131, 118, 156),   # 13: Indigo
        (255, 119, 168),   # 14: Pink
        (255, 204, 170)    # 15: Peach
    ]
    
    colors.extend(basic_colors)
    
    # Add pollution gradient colors (16-63)
    for i in range(48):
        factor = i / 47.0
        r = int(0 + factor * 255)
        g = int(255 - factor * 255)
        b = 0
        colors.append((r, g, b))
    
    # Add land value gradient colors (64-111)
    for i in range(48):
        factor = i / 47.0
        r = int(100 + factor * 155)
        g = int(100 + factor * 155)
        b = int(255 - factor * 155)
        colors.append((r, g, b))
    
    # Add density gradient colors (112-159)
    for i in range(48):
        factor = i / 47.0
        r = int(50 + factor * 205)
        g = int(50 + factor * 205)
        b = int(50 + factor * 205)
        colors.append((r, g, b))
    
    # Add water animation colors (160-191)
    for i in range(32):
        factor = i / 31.0
        r = int(0 + factor * 100)
        g = int(150 + factor * 105)
        b = 255
        colors.append((r, g, b))
    
    # Fill remaining colors with gradients
    for i in range(64):
        factor = i / 63.0
        r = int(factor * 255)
        g = int(factor * 255)
        b = int(factor * 255)
        colors.append((r, g, b))
    
    # Set pixel colors
    for i, color in enumerate(colors):
        palette_img.putpixel((i, 0), color)
    
    palette_img.save("assets/palette256.png")
    print("Created assets/palette256.png")

def create_ui_icons():
    """Create UI icons for tools"""
    icon_size = 16
    icons_per_row = 8
    num_icons = 16
    rows = 2
    
    image_width = icons_per_row * icon_size
    image_height = rows * icon_size
    
    ui_icons = Image.new('RGBA', (image_width, image_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(ui_icons)
    
    # Tool icons
    tools = [
        'bulldozer', 'residential', 'commercial', 'industrial',
        'road', 'rail', 'wire', 'park',
        'coal_plant', 'police', 'fire', 'hospital',
        'school', 'query', 'zoom_in', 'zoom_out'
    ]
    
    for i, tool in enumerate(tools):
        row = i // icons_per_row
        col = i % icons_per_row
        
        x = col * icon_size
        y = row * icon_size
        
        # Draw icon background
        draw.rectangle([x + 1, y + 1, x + icon_size - 2, y + icon_size - 2], fill=(64, 64, 64))
        
        # Draw simple tool representation
        if tool == 'bulldozer':
            draw.rectangle([x + 4, y + 8, x + 11, y + 12], fill=(255, 255, 0))
            draw.polygon([x + 3, y + 8, x + 8, y + 4, x + 12, y + 8], fill=(255, 165, 0))
        elif tool == 'residential':
            draw.rectangle([x + 5, y + 8, x + 10, y + 13], fill=(100, 149, 237))
            draw.polygon([x + 4, y + 8, x + 8, y + 4, x + 11, y + 8], fill=(178, 34, 34))
        elif tool == 'road':
            draw.rectangle([x + 6, y + 3, x + 9, y + 12], fill=(105, 105, 105))
            draw.line([x + 7, y + 3, x + 7, y + 12], fill=(255, 255, 0))
            
        # Add border
        draw.rectangle([x, y, x + icon_size - 1, y + icon_size - 1], outline=(128, 128, 128))
    
    ui_icons.save("assets/ui_icons.png")
    print("Created assets/ui_icons.png")

if __name__ == "__main__":
    print("Generating ConcLand Mini assets...")
    create_16x16_tiles()
    create_256_palette()
    create_ui_icons()
    print("All assets created successfully!")