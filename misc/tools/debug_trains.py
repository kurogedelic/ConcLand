#!/usr/bin/env python3
"""
Debug script to check train system status
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from concland_mini import ConcLandMini

def debug_trains():
    print("🚂 Train System Debug")
    print("=" * 40)
    
    # Create game instance
    game = ConcLandMini()
    
    # Check train system
    print(f"Train system initialized: {game.train_system is not None}")
    print(f"Number of trains: {len(game.train_system.trains)}")
    print(f"Number of stations: {len(game.train_system.stations)}")
    print(f"Rail network size: {len(game.train_system.rail_network)}")
    
    # Check for stations in grid
    station_count = 0
    rail_count = 0
    for y in range(100):
        for x in range(100):
            if hasattr(game, 'grid') and y < len(game.grid) and x < len(game.grid[y]):
                from concland_mini import CellType
                if game.grid[y][x] == CellType.STATION:
                    station_count += 1
                elif game.grid[y][x] == CellType.RAIL:
                    rail_count += 1
    
    print(f"Stations in grid: {station_count}")
    print(f"Rails in grid: {rail_count}")
    
    # Check train sprites
    sprite_files = ['train_horizontal', 'train_vertical']
    for sprite in sprite_files:
        exists = sprite in game.tile_manager.tile_images
        print(f"Train sprite '{sprite}': {'✅ Found' if exists else '❌ Missing'}")
    
    # Check if trains would be visible
    print(f"View mode: {game.view_mode} (trains only visible in mode 0)")
    
    if game.train_system.trains:
        print("\nActive trains:")
        for i, train in enumerate(game.train_system.trains):
            print(f"  Train {i}: pos=({train.x:.1f}, {train.y:.1f}), dir={train.direction}")
    else:
        print("No active trains - try building stations and rails first!")

if __name__ == "__main__":
    debug_trains()