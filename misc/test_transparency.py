#!/usr/bin/env python3
import pyxel

# Initialize Pyxel and load the palette
pyxel.init(100, 100)

# Load palette
pyxel.images[0].load(0, 0, '/Users/kurogedelic/ConcLand/assets/palette256_magenta.png', incl_colors=True)

# Check Pyxel's color palette
print('Checking Pyxel colors after loading palette:')
for i in [0, 1, 10, 30, 254, 255]:
    if i < len(pyxel.colors):
        color = pyxel.colors[i]
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        print(f'  pyxel.colors[{i:3d}] = 0x{color:06X} = RGB({r},{g},{b})')
        if r == 255 and g == 0 and b == 255:
            print(f'    -> This is MAGENTA!')

# Load the overlay image
pyxel.images[1].load(0, 0, '/Users/kurogedelic/ConcLand/assets/tiles/overlay/power_256.png', incl_colors=False)

# Check pixel values
print('\nChecking loaded image pixels:')
unique_pixels = set()
for y in range(8):
    for x in range(8):
        pixel = pyxel.images[1].pget(x, y)
        unique_pixels.add(pixel)

print(f'Unique pixel values in image: {sorted(unique_pixels)}')

# Test transparency with different values
def update():
    if pyxel.btnp(pyxel.KEY_ESCAPE):
        pyxel.quit()

def draw():
    pyxel.cls(3)  # Green background
    
    # Draw a test square
    pyxel.rect(20, 20, 20, 20, 8)  # Red square
    
    # Test different transparency values
    tests = [
        (10, 50, "No transparency"),
        (50, 50, "transparent=30"),
        (10, 70, "transparent=255"),
        (50, 70, "transparent=10"),
    ]
    
    # Draw overlay with no transparency
    pyxel.blt(10, 50, 1, 0, 0, 8, 8)
    
    # Draw overlay with transparent=30
    pyxel.blt(50, 50, 1, 0, 0, 8, 8, 30)
    
    # Draw overlay with transparent=255  
    pyxel.blt(10, 70, 1, 0, 0, 8, 8, 255)
    
    # Draw overlay with transparent=10
    pyxel.blt(50, 70, 1, 0, 0, 8, 8, 10)
    
    # Labels
    pyxel.text(5, 5, "Transparency Test", 7)
    for x, y, label in tests:
        pyxel.text(x + 12, y + 2, label, 7)

pyxel.run(update, draw)