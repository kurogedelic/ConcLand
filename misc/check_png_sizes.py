#!/usr/bin/env python3
"""Check actual PNG file sizes"""

from PIL import Image
import os

png_files = [
    'assets/tiles/power/coal.png',
    'assets/tiles/power/nuclear.png',
    'assets/tiles/public/police.png',
    'assets/tiles/public/fire.png',
    'assets/tiles/public/hospital.png',
]

for file_path in png_files:
    if os.path.exists(file_path):
        img = Image.open(file_path)
        print(f"{file_path}: {img.size[0]}x{img.size[1]} pixels, mode={img.mode}")
    else:
        print(f"{file_path}: NOT FOUND")