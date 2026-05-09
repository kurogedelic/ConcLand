"""
Font management system for ConcLand
Handles BDF font loading and fallback to basic fonts
"""
import os
from typing import Optional, List, Tuple

class FontManager:
    """Manages font loading and rendering"""
    
    def __init__(self):
        self.font_renderer = None
        self.font_loaded = False
        self.font_paths = [
            "font/umplus_j10r.bdf",
            "font/umplus_j12r.bdf",
            "font/misakifont/misaki_gothic.bdf",
            "fonts/umplus_j10r.bdf",
            "fonts/umplus_j12r.bdf"
        ]
        
        # Try to import BDFRenderer
        try:
            from font.bdfrenderer import BDFRenderer
            self.BDFRenderer = BDFRenderer
        except ImportError:
            self.BDFRenderer = None
    
    def initialize(self) -> bool:
        """Initialize font system"""
        if not self.BDFRenderer:
            print("BDFRenderer not available, using fallback font")
            return False
        
        # Try each font path
        for font_path in self.font_paths:
            if os.path.exists(font_path):
                try:
                    self.font_renderer = self.BDFRenderer(font_path)
                    self.font_loaded = True
                    print(f"Font loaded successfully: {font_path}")
                    return True
                except Exception as e:
                    print(f"Failed to load font {font_path}: {e}")
        
        print("No fonts could be loaded, using fallback")
        return False
    
    def render_text(self, pyxel, x: int, y: int, text: str, color: int, 
                   scale: int = 1, use_fallback: bool = True) -> None:
        """Render text with font or fallback"""
        if self.font_loaded and self.font_renderer:
            try:
                self.font_renderer.draw_text(x, y, text, color)
                return
            except Exception as e:
                if use_fallback:
                    print(f"Font rendering failed, using fallback: {e}")
                else:
                    raise
        
        # Fallback to Pyxel's built-in font
        if use_fallback:
            pyxel.text(x, y, text, color)
    
    def get_text_width(self, text: str, scale: int = 1) -> int:
        """Get text width in pixels"""
        if self.font_loaded and self.font_renderer:
            try:
                return self.font_renderer.get_text_width(text) * scale
            except:
                pass
        
        # Fallback: approximate width (4 pixels per character for Pyxel font)
        return len(text) * 4
    
    def get_text_height(self, scale: int = 1) -> int:
        """Get text height in pixels"""
        if self.font_loaded and self.font_renderer:
            try:
                return self.font_renderer.font_height * scale
            except:
                pass
        
        # Fallback: Pyxel font height
        return 6
    
    def is_loaded(self) -> bool:
        """Check if font is loaded"""
        return self.font_loaded
    
    def supports_japanese(self) -> bool:
        """Check if current font supports Japanese"""
        return self.font_loaded  # BDF fonts typically support Japanese

class TextRenderer:
    """High-level text rendering with automatic line breaking"""
    
    def __init__(self, font_manager: FontManager):
        self.font_manager = font_manager
    
    def draw_wrapped_text(self, pyxel, x: int, y: int, text: str, 
                         max_width: int, color: int, line_spacing: int = 2) -> int:
        """Draw text with automatic line breaking"""
        lines = self.wrap_text(text, max_width)
        current_y = y
        
        for line in lines:
            self.font_manager.render_text(pyxel, x, current_y, line, color)
            current_y += self.font_manager.get_text_height() + line_spacing
        
        return current_y
    
    def wrap_text(self, text: str, max_width: int) -> List[str]:
        """Wrap text to fit within max_width"""
        if not text:
            return []
        
        # Simple character-based wrapping for Japanese text
        lines = []
        current_line = ""
        
        for char in text:
            test_line = current_line + char
            if self.font_manager.get_text_width(test_line) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def draw_text_box(self, pyxel, x: int, y: int, width: int, height: int,
                     text: str, bg_color: int, text_color: int, 
                     border_color: Optional[int] = None, padding: int = 4) -> None:
        """Draw a text box with background"""
        # Draw background
        pyxel.rect(x, y, width, height, bg_color)
        
        # Draw border if specified
        if border_color is not None:
            pyxel.rectb(x, y, width, height, border_color)
        
        # Draw wrapped text
        text_x = x + padding
        text_y = y + padding
        max_text_width = width - (padding * 2)
        
        self.draw_wrapped_text(pyxel, text_x, text_y, text, max_text_width, text_color)

# Global font manager instance
_font_manager = None

def get_font_manager() -> FontManager:
    """Get or create global font manager"""
    global _font_manager
    if _font_manager is None:
        _font_manager = FontManager()
        _font_manager.initialize()
    return _font_manager