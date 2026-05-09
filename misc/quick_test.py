#!/usr/bin/env python3
"""
Quick test - start ConcLand Mini and immediately quit
"""

import pyxel
import time
import threading
from concland_mini import ConcLandMini

def auto_quit():
    """Quit after 1 second"""
    time.sleep(1)
    pyxel.quit()

if __name__ == "__main__":
    # Start auto-quit thread
    threading.Thread(target=auto_quit, daemon=True).start()
    
    # Start game
    try:
        game = ConcLandMini()
    except Exception as e:
        print(f"Game error: {e}")
        
    print("Game finished, checking log...")