#!/usr/bin/env python3
"""
Fixed tile system that properly handles large tiles
"""

import pyxel
import os

class FixedTileSystem:
    def __init__(self):
        self.loaded_tiles = {}
        
        # Large tiles need special handling
        self.large_tiles = {
            'coal_plant': ('assets/tiles/power/coal.png', 32),
            'nuclear_plant': ('assets/tiles/power/nuclear.png', 32),
            'police': ('assets/tiles/public/police.png', 24),
            'fire': ('assets/tiles/public/fire.png', 24),
            'hospital': ('assets/tiles/public/hospital.png', 24),
        }
    
    def initialize(self):
        """Initialize tile system with proper large tile support"""
        
        # Use bank 2 for large tiles
        # Load each large tile at position (0,0) temporarily
        # then store where it actually should be drawn from
        
        print("Loading large tiles properly...")
        
        # First, create the combined tileset
        self._create_combined_tileset()
        
        # Load the combined tileset
        pyxel.images[2].load(0, 0, 'assets/combined_tileset_fixed.png')
        
        # Store tile positions
        self.loaded_tiles['coal_plant'] = (2, 0, 0, 32, 32)
        self.loaded_tiles['nuclear_plant'] = (2, 32, 0, 32, 32)
        self.loaded_tiles['police'] = (2, 64, 0, 24, 24)
        self.loaded_tiles['fire'] = (2, 88, 0, 24, 24)
        self.loaded_tiles['hospital'] = (2, 112, 0, 24, 24)
        
        print("Large tiles loaded successfully!")
        return True
    
    def _create_combined_tileset(self):
        """Create a combined tileset with all large tiles"""
        try:
            from PIL import Image
            
            # Create empty tileset
            tileset = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
            
            # Position large tiles
            positions = [
                ('assets/tiles/power/coal.png', 0, 0),
                ('assets/tiles/power/nuclear.png', 32, 0),
                ('assets/tiles/public/police.png', 64, 0),
                ('assets/tiles/public/fire.png', 88, 0),
                ('assets/tiles/public/hospital.png', 112, 0),
            ]
            
            for file_path, x, y in positions:
                if os.path.exists(file_path):
                    img = Image.open(file_path)
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    tileset.paste(img, (x, y))
            
            # Save it
            tileset.save('assets/combined_tileset_fixed.png')
            print("Created combined tileset")
            
        except ImportError:
            print("PIL not available, using pre-made tileset")
    
    def draw_tile(self, tile_id, x, y):
        """Draw a tile at screen position"""
        if tile_id in self.loaded_tiles:
            bank, src_x, src_y, width, height = self.loaded_tiles[tile_id]
            pyxel.blt(x, y, bank, src_x, src_y, width, height)
        else:
            # Fallback for missing tiles
            pyxel.rect(x, y, 8, 8, 8)

# Test it
if __name__ == "__main__":
    pyxel.init(320, 240)
    
    tile_system = FixedTileSystem()
    tile_system.initialize()
    
    def update():
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
    
    def draw():
        pyxel.cls(0)
        
        pyxel.text(10, 10, "Fixed Tile System", 7)
        
        # Draw large tiles
        tile_system.draw_tile('coal_plant', 10, 30)
        pyxel.rectb(10, 30, 32, 32, 10)
        
        tile_system.draw_tile('nuclear_plant', 50, 30)
        pyxel.rectb(50, 30, 32, 32, 11)
        
        tile_system.draw_tile('police', 90, 30)
        pyxel.rectb(90, 30, 24, 24, 12)
    
    pyxel.run(update, draw)