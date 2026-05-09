#!/usr/bin/env python3
"""Generate 16x16 tool icons for the tool panel"""

from PIL import Image, ImageDraw
import os

# Output directory
output_dir = "assets/icons"
os.makedirs(output_dir, exist_ok=True)

def create_icon(name, draw_func):
    """Create a 16x16 icon with the given drawing function"""
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_func(draw)
    img.save(os.path.join(output_dir, f"{name}.png"))
    print(f"  ✅ {name}.png")

# Define colors
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
GRAY = (128, 128, 128, 255)
DARK_GRAY = (64, 64, 64, 255)
RED = (255, 0, 0, 255)
GREEN = (0, 255, 0, 255)
BLUE = (0, 0, 255, 255)
YELLOW = (255, 255, 0, 255)
BROWN = (139, 69, 19, 255)
LIGHT_BLUE = (173, 216, 230, 255)
DARK_GREEN = (0, 128, 0, 255)
ORANGE = (255, 165, 0, 255)

print("🎨 Generating Tool Icons (16x16)")
print("=" * 40)

# Bulldozer icon
def draw_bulldozer(draw):
    # Bulldozer blade
    draw.rectangle([2, 6, 13, 9], fill=YELLOW, outline=BLACK)
    # Tracks
    draw.rectangle([4, 10, 11, 11], fill=DARK_GRAY)
    # Body
    draw.rectangle([5, 7, 10, 9], fill=ORANGE)

create_icon("bulldozer", draw_bulldozer)

# Residential icon (house)
def draw_residential(draw):
    # Roof
    draw.polygon([(8, 3), (3, 8), (13, 8)], fill=RED, outline=BLACK)
    # House body
    draw.rectangle([4, 8, 12, 13], fill=GREEN, outline=BLACK)
    # Door
    draw.rectangle([7, 10, 9, 13], fill=BROWN)

create_icon("residential", draw_residential)

# Commercial icon (shop/store)
def draw_commercial(draw):
    # Building
    draw.rectangle([3, 4, 12, 13], fill=LIGHT_BLUE, outline=BLACK)
    # Awning
    draw.rectangle([2, 8, 13, 9], fill=RED)
    # Window
    draw.rectangle([5, 5, 10, 7], fill=WHITE, outline=BLACK)
    # Door
    draw.rectangle([6, 10, 9, 13], fill=DARK_GRAY)

create_icon("commercial", draw_commercial)

# Industrial icon (factory)
def draw_industrial(draw):
    # Factory building
    draw.rectangle([2, 7, 13, 13], fill=GRAY, outline=BLACK)
    # Chimney
    draw.rectangle([4, 3, 6, 8], fill=DARK_GRAY, outline=BLACK)
    draw.rectangle([9, 3, 11, 8], fill=DARK_GRAY, outline=BLACK)
    # Smoke
    draw.ellipse([3, 1, 5, 3], fill=GRAY)
    draw.ellipse([8, 1, 10, 3], fill=GRAY)

create_icon("industrial", draw_industrial)

# Road icon
def draw_road(draw):
    # Road surface
    draw.rectangle([2, 6, 13, 10], fill=DARK_GRAY, outline=BLACK)
    # Center line
    draw.line([(2, 8), (5, 8)], fill=YELLOW, width=1)
    draw.line([(7, 8), (10, 8)], fill=YELLOW, width=1)
    draw.line([(12, 8), (13, 8)], fill=YELLOW, width=1)

create_icon("road", draw_road)

# Rail icon
def draw_rail(draw):
    # Rails
    draw.line([(2, 6), (13, 6)], fill=DARK_GRAY, width=2)
    draw.line([(2, 10), (13, 10)], fill=DARK_GRAY, width=2)
    # Ties
    for x in range(3, 14, 3):
        draw.line([(x, 5), (x, 11)], fill=BROWN, width=2)

create_icon("rail", draw_rail)

# Park icon (tree)
def draw_park(draw):
    # Tree trunk
    draw.rectangle([7, 10, 9, 13], fill=BROWN, outline=BLACK)
    # Tree crown
    draw.ellipse([3, 3, 13, 10], fill=DARK_GREEN, outline=BLACK)

create_icon("park", draw_park)

# Power line icon
def draw_wire(draw):
    # Poles
    draw.line([(3, 3), (3, 13)], fill=BROWN, width=2)
    draw.line([(12, 3), (12, 13)], fill=BROWN, width=2)
    # Wires
    draw.line([(3, 5), (12, 5)], fill=BLACK, width=1)
    draw.line([(3, 7), (12, 7)], fill=BLACK, width=1)

create_icon("wire", draw_wire)

# Coal power plant icon
def draw_coal_plant(draw):
    # Building
    draw.rectangle([3, 8, 12, 13], fill=GRAY, outline=BLACK)
    # Smokestacks
    draw.rectangle([5, 4, 7, 9], fill=DARK_GRAY, outline=BLACK)
    draw.rectangle([9, 4, 11, 9], fill=DARK_GRAY, outline=BLACK)
    # Smoke
    draw.ellipse([4, 2, 8, 4], fill=BLACK)
    draw.ellipse([8, 2, 12, 4], fill=BLACK)

create_icon("coal_plant", draw_coal_plant)

# Nuclear power plant icon
def draw_nuclear_plant(draw):
    # Cooling tower shape
    draw.polygon([(8, 3), (5, 13), (11, 13)], fill=LIGHT_BLUE, outline=BLACK)
    # Nuclear symbol
    draw.ellipse([6, 7, 10, 11], fill=YELLOW, outline=BLACK)
    draw.ellipse([7, 8, 9, 10], fill=BLACK)

create_icon("nuclear_plant", draw_nuclear_plant)

# Police station icon
def draw_police(draw):
    # Building
    draw.rectangle([3, 5, 12, 13], fill=BLUE, outline=BLACK)
    # Badge/star shape
    draw.polygon([(8, 6), (9, 8), (11, 8), (9, 9), (10, 11), 
                  (8, 10), (6, 11), (7, 9), (5, 8), (7, 8)], 
                 fill=YELLOW, outline=BLACK)

create_icon("police", draw_police)

# Fire station icon
def draw_fire(draw):
    # Building
    draw.rectangle([3, 6, 12, 13], fill=RED, outline=BLACK)
    # Garage door
    draw.rectangle([5, 8, 10, 13], fill=WHITE, outline=BLACK)
    # Fire truck hint
    draw.rectangle([6, 9, 9, 11], fill=RED)

create_icon("fire", draw_fire)

# Hospital icon
def draw_hospital(draw):
    # Building
    draw.rectangle([3, 4, 12, 13], fill=WHITE, outline=BLACK)
    # Red cross
    draw.rectangle([7, 6, 9, 11], fill=RED)
    draw.rectangle([5, 8, 11, 9], fill=RED)

create_icon("hospital", draw_hospital)

# School icon
def draw_school(draw):
    # Building
    draw.rectangle([3, 6, 12, 13], fill=BROWN, outline=BLACK)
    # Roof
    draw.polygon([(8, 3), (3, 6), (12, 6)], fill=RED, outline=BLACK)
    # Bell tower
    draw.rectangle([7, 4, 9, 6], fill=YELLOW)

create_icon("school", draw_school)

# Query/Info icon
def draw_query(draw):
    # Circle background
    draw.ellipse([2, 2, 13, 13], fill=BLUE, outline=BLACK)
    # Question mark
    draw.text((6, 3), "?", fill=WHITE)

create_icon("query", draw_query)

# Budget icon (money)
def draw_budget(draw):
    # Dollar sign background
    draw.ellipse([3, 3, 12, 12], fill=GREEN, outline=BLACK)
    # Dollar sign
    draw.text((5, 4), "$", fill=WHITE)

create_icon("budget", draw_budget)

# Map icon
def draw_map(draw):
    # Map background
    draw.rectangle([2, 2, 13, 13], fill=LIGHT_BLUE, outline=BLACK)
    # Land masses
    draw.rectangle([3, 3, 7, 6], fill=GREEN)
    draw.rectangle([9, 8, 12, 12], fill=GREEN)
    # Roads
    draw.line([(5, 5), (10, 10)], fill=GRAY, width=1)

create_icon("map", draw_map)

# Settings icon (gear)
def draw_settings(draw):
    # Gear shape (simplified)
    draw.ellipse([4, 4, 11, 11], fill=GRAY, outline=BLACK)
    # Center hole
    draw.ellipse([6, 6, 9, 9], fill=WHITE)
    # Teeth
    draw.rectangle([7, 2, 8, 4], fill=GRAY)
    draw.rectangle([7, 11, 8, 13], fill=GRAY)
    draw.rectangle([2, 7, 4, 8], fill=GRAY)
    draw.rectangle([11, 7, 13, 8], fill=GRAY)

create_icon("settings", draw_settings)

print("=" * 40)
print(f"✨ Generated {len(os.listdir(output_dir))} icons in {output_dir}/")