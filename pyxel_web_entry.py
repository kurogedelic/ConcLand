#!/usr/bin/env python3
"""
Pyxel Web Entry Point for ConcLand
Simplified entry point for Pyxel Web (WASM/browser deployment)
"""

import sys

try:
    import pyxel
except ImportError:
    print("Pyxel is not installed. Please run: pip install pyxel")
    sys.exit(1)

# Import the main game
try:
    from concland_mini import ConcLandMini
except ImportError as e:
    print(f"Error importing game: {e}")
    sys.exit(1)

def main():
    """Main entry point for Pyxel Web"""
    try:
        # Initialize and run the game
        ConcLandMini()
    except Exception as e:
        print(f"Error starting game: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
