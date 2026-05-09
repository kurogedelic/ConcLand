#!/usr/bin/env python3
"""Create a lightning bolt icon for unpowered buildings"""

from PIL import Image, ImageDraw

def create_lightning_icon():
    # Create 8x8 transparent image
    img = Image.new('RGBA', (8, 8), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Lightning bolt shape (yellow/orange)
    lightning_color = (255, 200, 0, 255)  # Yellow-orange
    
    # Draw lightning bolt pattern
    # Top part (going down-right)
    pixels = [
        (3, 0), (4, 0),  # Top
        (2, 1), (3, 1),
        (2, 2), (3, 2),
        (1, 3), (2, 3), (3, 3), (4, 3),  # Middle wide part
        (3, 4), (4, 4),
        (4, 5), (5, 5),
        (5, 6), (6, 6),
        (6, 7),  # Bottom tip
    ]
    
    for x, y in pixels:
        img.putpixel((x, y), lightning_color)
    
    # Add darker outline for visibility
    outline_color = (180, 100, 0, 255)  # Dark orange
    outline_pixels = [
        (2, 0), (5, 0),  # Top outline
        (1, 1), (4, 1),
        (1, 2), (4, 2),
        (0, 3), (5, 3),  # Middle outline
        (2, 4), (5, 4),
        (3, 5), (6, 5),
        (4, 6), (7, 6),
        (5, 7), (7, 7),  # Bottom outline
    ]
    
    for x, y in outline_pixels:
        if 0 <= x < 8 and 0 <= y < 8:
            # Only add outline if pixel is transparent
            if img.getpixel((x, y))[3] == 0:
                img.putpixel((x, y), outline_color)
    
    # Save the icon
    img.save('assets/icons/no_power.png')
    print("✅ Created lightning bolt icon: assets/icons/no_power.png")
    
    # Also create a simpler version with just the bolt
    img2 = Image.new('RGBA', (8, 8), (0, 0, 0, 0))
    
    # Simpler lightning pattern
    simple_pixels = [
        (3, 1), (4, 1),
        (2, 2), (3, 2),
        (3, 3), (4, 3),
        (4, 4), (5, 4),
        (3, 5), (4, 5),
    ]
    
    for x, y in simple_pixels:
        img2.putpixel((x, y), lightning_color)
    
    img2.save('assets/icons/no_power_simple.png')
    print("✅ Created simple lightning icon: assets/icons/no_power_simple.png")

if __name__ == "__main__":
    create_lightning_icon()