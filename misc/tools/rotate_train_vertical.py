#!/usr/bin/env python3
"""
Rotate train_vertical.png by 90 degrees
"""

from PIL import Image
import os

def rotate_train_vertical():
    """Rotate the vertical train image by 90 degrees"""
    
    # Path to the vertical train image
    input_path = "assets/tiles/overlay/train_vertical.png"
    output_path = "assets/tiles/overlay/train_vertical_rotated.png"
    
    # Open and rotate the image
    img = Image.open(input_path)
    
    # Rotate 90 degrees counter-clockwise to make it vertical
    rotated = img.rotate(90, expand=True)
    
    # Save the rotated image
    rotated.save(output_path)
    print(f"Rotated image saved to: {output_path}")
    
    # Also save over the original if desired
    response = input("Replace original train_vertical.png? (y/n): ")
    if response.lower() == 'y':
        rotated.save(input_path)
        print(f"Original image replaced: {input_path}")
    
    return rotated

if __name__ == "__main__":
    rotate_train_vertical()