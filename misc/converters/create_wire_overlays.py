#!/usr/bin/env python3
"""
Create wire overlay assets for roads and rails
These will have transparent backgrounds to overlay on existing tiles
"""

from PIL import Image
import os

def create_wire_overlay(input_path, output_path):
    """Create a wire overlay with transparency from existing wire tile"""
    # Open the original wire tile
    img = Image.open(input_path).convert("RGBA")
    
    # Create a new image with transparency
    overlay = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    
    # Copy only the wire pixels (non-black pixels)
    for y in range(8):
        for x in range(8):
            pixel = img.getpixel((x, y))
            # If it's not black (background), copy it
            if pixel[:3] != (0, 0, 0):
                # Make the wire a bit darker/different color for overlay
                # Use a yellow/orange color for power lines on roads
                overlay.putpixel((x, y), (255, 200, 0, 255))  # Yellow-orange
    
    # Save the overlay
    overlay.save(output_path)
    print(f"Created overlay: {output_path}")

def main():
    # Source and destination directories
    source_dir = "assets/tiles/power"
    overlay_dir = "assets/tiles/overlay/wire"
    
    # Create overlay directory if it doesn't exist
    os.makedirs(overlay_dir, exist_ok=True)
    
    # Wire tile mappings
    wire_tiles = [
        "wire_alone",
        "wire_horizontal", 
        "wire_vertical",
        "wire_ne", "wire_nw", "wire_se", "wire_sw",
        "wire_t_top", "wire_t_right", "wire_t_down", "wire_t_left",
        "wire_cross"
    ]
    
    # Create overlay for each wire tile
    for tile_name in wire_tiles:
        input_file = os.path.join(source_dir, f"{tile_name}.png")
        output_file = os.path.join(overlay_dir, f"{tile_name}_overlay.png")
        
        if os.path.exists(input_file):
            create_wire_overlay(input_file, output_file)
        else:
            print(f"Warning: {input_file} not found")
    
    print("\nWire overlays created successfully!")
    print("These overlays can be drawn on top of roads/rails with transparency")

if __name__ == "__main__":
    main()