import pyxel

class BDFRenderer:
    """BDF (Bitmap Distribution Format) font renderer for Pyxel"""
    
    def __init__(self, bdf_path):
        self.glyphs = {}
        self.font_name = ""
        self.font_size = 0
        self.bbox = [0, 0, 0, 0]  # Font bounding box
        self.baseline = 0
        
        self._parse_bdf(bdf_path)
    
    def _parse_bdf(self, bdf_path):
        """Parse BDF font file"""
        try:
            with open(bdf_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Font file not found: {bdf_path}")
            return
        
        current_char = None
        current_bitmap = []
        in_bitmap = False
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("FONT "):
                self.font_name = line[5:]
            
            elif line.startswith("SIZE "):
                parts = line.split()
                if len(parts) >= 2:
                    self.font_size = int(parts[1])
            
            elif line.startswith("FONTBOUNDINGBOX "):
                parts = line.split()
                if len(parts) >= 5:
                    self.bbox = [int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])]
            
            elif line.startswith("ENCODING "):
                current_char = int(line.split()[1])
                current_bitmap = []
            
            elif line == "BITMAP":
                in_bitmap = True
            
            elif line == "ENDCHAR":
                if current_char is not None and current_bitmap:
                    self.glyphs[current_char] = current_bitmap
                current_char = None
                current_bitmap = []
                in_bitmap = False
            
            elif in_bitmap and line:
                # Convert hex string to binary representation
                current_bitmap.append(line)
    
    def draw_text(self, x, y, text, color=7):
        """Draw text using the loaded BDF font"""
        cursor_x = x
        cursor_y = y
        
        for char in text:
            char_code = ord(char)
            
            if char_code in self.glyphs:
                self._draw_glyph(cursor_x, cursor_y, char_code, color)
                # Move cursor for next character
                # Simple fixed-width assumption - can be improved with glyph metrics
                cursor_x += 8  # Default character width
            elif char == ' ':
                cursor_x += 6  # Space width
            elif char == '\n':
                cursor_x = x
                cursor_y += self.font_size if self.font_size > 0 else 12
    
    def _draw_glyph(self, x, y, char_code, color):
        """Draw a single glyph at the specified position"""
        if char_code not in self.glyphs:
            return
        
        bitmap = self.glyphs[char_code]
        
        for row_idx, hex_row in enumerate(bitmap):
            # Convert hex to binary
            try:
                row_value = int(hex_row, 16)
            except ValueError:
                continue
            
            # Draw pixels for this row
            bit_width = len(hex_row) * 4  # Each hex digit = 4 bits
            
            for bit_idx in range(bit_width):
                if row_value & (1 << (bit_width - 1 - bit_idx)):
                    pyxel.pset(x + bit_idx, y + row_idx, color)
    
    def get_text_width(self, text):
        """Calculate the width of text in pixels"""
        # Simple implementation - assumes fixed width
        return len(text) * 8
    
    def get_text_height(self, text):
        """Calculate the height of text in pixels"""
        lines = text.split('\n')
        return len(lines) * (self.font_size if self.font_size > 0 else 12)