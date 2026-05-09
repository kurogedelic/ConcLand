#!/usr/bin/env python3
"""
Simple launcher for ConcLand Mini
"""
import subprocess
import sys

def main():
    print("🏙️  ConcLand Mini - City Simulation Game")
    print("Starting game...")
    print("Controls: Arrow keys to move, 1-9 for tools, Space/Z to place, V to change view mode")
    print("Press Q to quit the game")
    print()
    
    try:
        subprocess.run([sys.executable, "concland_mini.py"])
    except KeyboardInterrupt:
        print("\nGame stopped by user")
    except Exception as e:
        print(f"Error starting game: {e}")

if __name__ == "__main__":
    main()