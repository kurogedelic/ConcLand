#!/usr/bin/env python3
"""Check if tiles are overlapping in memory"""

from individual_tile_system import IndividualTileSystem
import pyxel

pyxel.init(320, 240)
ts = IndividualTileSystem()
ts.initialize()

# Check coal_plant specifically
if 'coal_plant' in ts.loaded_tiles:
    info = ts.loaded_tiles['coal_plant']
    print(f'\n=== Coal plant loaded info ===')
    print(f'Info: {info}')
    
    if len(info) == 5:
        bank, x, y, w, h = info
        print(f'Bank: {bank}, Position: ({x},{y}), Size: {w}x{h}')
        
        # Check if anything else is at the same position or overlapping
        print(f'\nChecking for overlaps...')
        
        overlaps = []
        for tile_id, tile_info in ts.loaded_tiles.items():
            if tile_id != 'coal_plant' and len(tile_info) == 5:
                t_bank, t_x, t_y, t_w, t_h = tile_info
                # Check if this tile overlaps with coal_plant
                if t_bank == bank:
                    # Check for any overlap
                    if (t_x < x + w and t_x + t_w > x and 
                        t_y < y + h and t_y + t_h > y):
                        overlaps.append((tile_id, t_x, t_y, t_w, t_h))
        
        if overlaps:
            print(f'Found {len(overlaps)} overlapping tiles:')
            for tile_id, t_x, t_y, t_w, t_h in overlaps:
                print(f'  - {tile_id}: at ({t_x},{t_y}) size {t_w}x{t_h}')
        else:
            print('No overlapping tiles found')
        
        # Check actual pixels in the image bank
        print(f'\nChecking actual pixels in bank {bank} at coal_plant position:')
        non_zero_8x8 = 0
        non_zero_32x32 = 0
        
        for dy in range(8):
            for dx in range(8):
                if pyxel.images[bank].pget(x + dx, y + dy) != 0:
                    non_zero_8x8 += 1
        
        for dy in range(32):
            for dx in range(32):
                if x + dx < 256 and y + dy < 256:
                    if pyxel.images[bank].pget(x + dx, y + dy) != 0:
                        non_zero_32x32 += 1
        
        print(f'Non-zero pixels in first 8x8: {non_zero_8x8}/64')
        print(f'Non-zero pixels in full 32x32: {non_zero_32x32}/1024')
        
        if non_zero_32x32 > non_zero_8x8:
            print('✓ Full 32x32 sprite is in memory')
        else:
            print('✗ Only 8x8 portion is in memory')

pyxel.quit()