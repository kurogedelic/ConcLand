#!/usr/bin/env python3
from PIL import Image
import numpy as np

# List of overlay files to process
overlay_files = [
    'power.png',
    'fire.png', 
    'water.png',
    'nuclear.png',
    'cars.png'
]

for filename in overlay_files:
    filepath = f'/Users/kurogedelic/ConcLand/assets/tiles/overlay/{filename}'
    
    try:
        # Open the image
        img = Image.open(filepath)
        
        # Convert to RGBA
        img = img.convert('RGBA')
        
        # Get pixel data
        data = np.array(img)
        
        # Create mask for magenta pixels (255, 0, 255)
        magenta_mask = (data[:,:,0] == 255) & (data[:,:,1] == 0) & (data[:,:,2] == 255)
        
        # Set alpha to 0 for magenta pixels
        data[magenta_mask, 3] = 0
        
        # Save with alpha channel
        new_img = Image.fromarray(data, 'RGBA')
        output_path = filepath.replace('.png', '_alpha.png')
        new_img.save(output_path)
        
        print(f'Created {output_path} with {np.sum(magenta_mask)} transparent pixels')
        
    except Exception as e:
        print(f'Error processing {filename}: {e}')