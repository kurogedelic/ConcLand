"""
Visual Enhancement System for ConcLand
Provides advanced color palettes, window management, and visualization
"""

import pyxel
import math
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

class ColorTheme(Enum):
    """Available color themes"""
    CLASSIC = "classic"      # Original SimCity colors
    MODERN = "modern"        # Contemporary flat design
    RETRO = "retro"         # 8-bit nostalgia
    DARK = "dark"           # Dark mode
    PASTEL = "pastel"       # Soft pastel colors
    VIBRANT = "vibrant"     # High contrast vibrant
    MONOCHROME = "monochrome"  # Grayscale
    NATURE = "nature"       # Earth tones
    CYBERPUNK = "cyberpunk" # Neon and dark
    AUTUMN = "autumn"       # Fall colors

@dataclass
class ColorPalette:
    """Color palette definition"""
    name: str
    primary: List[int]      # Main UI colors
    secondary: List[int]    # Secondary UI colors
    terrain: List[int]      # Terrain colors
    buildings: List[int]    # Building colors
    ui_bg: int             # UI background
    ui_fg: int             # UI foreground
    ui_accent: int         # UI accent color
    grid: int              # Grid lines
    selection: int         # Selection highlight
    danger: int            # Danger/error color
    success: int           # Success color
    warning: int           # Warning color
    info: int              # Info color

class PaletteManager:
    """Manages color palettes and themes"""
    
    def __init__(self):
        self.current_theme = ColorTheme.CLASSIC
        self.palettes = self._initialize_palettes()
        self.custom_palette = None
        self.color_map = {}  # Maps logical colors to palette indices
        
    def _initialize_palettes(self) -> Dict[ColorTheme, ColorPalette]:
        """Initialize all color palettes"""
        palettes = {}
        
        # Classic SimCity palette
        palettes[ColorTheme.CLASSIC] = ColorPalette(
            name="Classic",
            primary=[7, 12, 10, 11],     # White, Light green, Yellow, Light yellow
            secondary=[8, 2, 4, 14],      # Red, Dark blue, Brown, Pink
            terrain=[3, 11, 10, 5, 6],    # Green, Light yellow, Yellow, Dark gray, Gray
            buildings=[7, 13, 5, 8, 2],   # Various building colors
            ui_bg=0,                      # Black
            ui_fg=7,                      # White
            ui_accent=12,                 # Light green
            grid=5,                       # Dark gray
            selection=10,                 # Yellow
            danger=8,                     # Red
            success=11,                   # Light green
            warning=9,                    # Orange
            info=12                       # Cyan
        )
        
        # Modern flat design
        palettes[ColorTheme.MODERN] = ColorPalette(
            name="Modern",
            primary=[7, 12, 6, 13],
            secondary=[5, 14, 2, 10],
            terrain=[3, 11, 6, 13, 15],
            buildings=[7, 12, 13, 14, 6],
            ui_bg=1,
            ui_fg=7,
            ui_accent=12,
            grid=13,
            selection=14,
            danger=8,
            success=11,
            warning=10,
            info=12
        )
        
        # Dark theme
        palettes[ColorTheme.DARK] = ColorPalette(
            name="Dark",
            primary=[13, 5, 6, 1],
            secondary=[12, 14, 2, 8],
            terrain=[1, 5, 13, 0, 6],
            buildings=[13, 5, 6, 14, 12],
            ui_bg=0,
            ui_fg=13,
            ui_accent=14,
            grid=1,
            selection=5,
            danger=8,
            success=11,
            warning=9,
            info=6
        )
        
        # Pastel theme
        palettes[ColorTheme.PASTEL] = ColorPalette(
            name="Pastel",
            primary=[7, 14, 11, 10],
            secondary=[12, 13, 6, 15],
            terrain=[11, 14, 10, 12, 7],
            buildings=[7, 14, 15, 11, 13],
            ui_bg=7,
            ui_fg=0,
            ui_accent=14,
            grid=13,
            selection=11,
            danger=8,
            success=11,
            warning=10,
            info=12
        )
        
        # Cyberpunk neon
        palettes[ColorTheme.CYBERPUNK] = ColorPalette(
            name="Cyberpunk",
            primary=[14, 12, 8, 0],
            secondary=[5, 13, 10, 2],
            terrain=[0, 1, 5, 13, 14],
            buildings=[14, 12, 13, 5, 8],
            ui_bg=0,
            ui_fg=14,
            ui_accent=12,
            grid=5,
            selection=14,
            danger=8,
            success=12,
            warning=10,
            info=13
        )
        
        return palettes
    
    def set_theme(self, theme: ColorTheme):
        """Set the current color theme"""
        if theme in self.palettes:
            self.current_theme = theme
            self._apply_palette(self.palettes[theme])
    
    def _apply_palette(self, palette: ColorPalette):
        """Apply a color palette to the game"""
        # Update color mapping
        self.color_map = {
            'ui_bg': palette.ui_bg,
            'ui_fg': palette.ui_fg,
            'ui_accent': palette.ui_accent,
            'grid': palette.grid,
            'selection': palette.selection,
            'danger': palette.danger,
            'success': palette.success,
            'warning': palette.warning,
            'info': palette.info
        }
    
    def get_color(self, color_name: str) -> int:
        """Get a color by logical name"""
        return self.color_map.get(color_name, 7)  # Default to white
    
    def get_current_palette(self) -> ColorPalette:
        """Get the current color palette"""
        return self.palettes[self.current_theme]

@dataclass
class Window:
    """Window component for UI"""
    x: int
    y: int
    width: int
    height: int
    title: str = ""
    visible: bool = True
    draggable: bool = False
    resizable: bool = False
    has_close: bool = True
    has_minimize: bool = False
    minimized: bool = False
    z_order: int = 0
    content_offset_x: int = 0
    content_offset_y: int = 0
    border_style: str = "single"  # single, double, none, rounded
    
class WindowManager:
    """Manages UI windows"""
    
    def __init__(self, palette_manager: PaletteManager):
        self.windows: List[Window] = []
        self.active_window: Optional[Window] = None
        self.dragging_window: Optional[Window] = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.palette = palette_manager
        
    def create_window(self, x: int, y: int, width: int, height: int, 
                     title: str = "", **kwargs) -> Window:
        """Create a new window"""
        window = Window(x, y, width, height, title, **kwargs)
        self.windows.append(window)
        self.windows.sort(key=lambda w: w.z_order)
        return window
    
    def draw_window(self, window: Window):
        """Draw a window"""
        if not window.visible:
            return
        
        if window.minimized:
            # Draw minimized window (title bar only)
            self._draw_title_bar(window)
            return
        
        # Draw window background
        pyxel.rect(window.x, window.y, window.width, window.height, 
                  self.palette.get_color('ui_bg'))
        
        # Draw border
        self._draw_border(window)
        
        # Draw title bar if has title
        if window.title:
            self._draw_title_bar(window)
    
    def _draw_border(self, window: Window):
        """Draw window border"""
        x, y, w, h = window.x, window.y, window.width, window.height
        color = self.palette.get_color('ui_fg')
        
        if window.border_style == "single":
            # Simple rectangle border
            pyxel.rectb(x, y, w, h, color)
        elif window.border_style == "double":
            # Double border
            pyxel.rectb(x, y, w, h, color)
            pyxel.rectb(x+1, y+1, w-2, h-2, color)
        elif window.border_style == "rounded":
            # Rounded corners (simplified)
            pyxel.line(x+2, y, x+w-2, y, color)
            pyxel.line(x+2, y+h-1, x+w-2, y+h-1, color)
            pyxel.line(x, y+2, x, y+h-2, color)
            pyxel.line(x+w-1, y+2, x+w-1, y+h-2, color)
            # Corner pixels
            pyxel.pset(x+1, y+1, color)
            pyxel.pset(x+w-2, y+1, color)
            pyxel.pset(x+1, y+h-2, color)
            pyxel.pset(x+w-2, y+h-2, color)
    
    def _draw_title_bar(self, window: Window):
        """Draw window title bar"""
        if not window.title:
            return
        
        x, y, w = window.x, window.y, window.width
        bar_height = 10
        
        # Title bar background
        pyxel.rect(x, y, w, bar_height, self.palette.get_color('ui_accent'))
        
        # Title text
        text_x = x + 2
        text_y = y + 2
        pyxel.text(text_x, text_y, window.title, self.palette.get_color('ui_fg'))
        
        # Control buttons
        if window.has_close:
            close_x = x + w - 8
            pyxel.text(close_x, text_y, "X", self.palette.get_color('danger'))
        
        if window.has_minimize:
            min_x = x + w - 16 if window.has_close else x + w - 8
            pyxel.text(min_x, text_y, "_", self.palette.get_color('ui_fg'))
    
    def handle_mouse(self, mx: int, my: int, clicked: bool):
        """Handle mouse input for windows"""
        # Check for window interaction
        for window in reversed(self.windows):  # Check top windows first
            if not window.visible:
                continue
            
            # Check if mouse is over window
            if (window.x <= mx < window.x + window.width and
                window.y <= my < window.y + window.height):
                
                if clicked:
                    # Check for close button
                    if window.has_close:
                        close_x = window.x + window.width - 8
                        if close_x <= mx < close_x + 8 and window.y <= my < window.y + 10:
                            window.visible = False
                            return
                    
                    # Check for minimize button
                    if window.has_minimize:
                        min_x = window.x + window.width - (16 if window.has_close else 8)
                        if min_x <= mx < min_x + 8 and window.y <= my < window.y + 10:
                            window.minimized = not window.minimized
                            return
                    
                    # Start dragging if draggable
                    if window.draggable and window.y <= my < window.y + 10:
                        self.dragging_window = window
                        self.drag_offset_x = mx - window.x
                        self.drag_offset_y = my - window.y
                        # Bring to front
                        window.z_order = max(w.z_order for w in self.windows) + 1
                        self.windows.sort(key=lambda w: w.z_order)
                
                self.active_window = window
                break
        
        # Handle dragging
        if self.dragging_window and not clicked:
            self.dragging_window = None
        elif self.dragging_window:
            self.dragging_window.x = mx - self.drag_offset_x
            self.dragging_window.y = my - self.drag_offset_y

class DataVisualizer:
    """Data visualization components"""
    
    def __init__(self, palette_manager: PaletteManager):
        self.palette = palette_manager
        self.animations = {}
        
    def draw_bar_chart(self, x: int, y: int, width: int, height: int,
                       data: List[float], labels: Optional[List[str]] = None,
                       colors: Optional[List[int]] = None):
        """Draw a bar chart"""
        if not data:
            return
        
        max_value = max(data) if max(data) > 0 else 1
        bar_width = width // len(data)
        
        for i, value in enumerate(data):
            bar_height = int((value / max_value) * height)
            bar_x = x + i * bar_width
            bar_y = y + height - bar_height
            
            color = colors[i] if colors and i < len(colors) else self.palette.get_color('ui_accent')
            
            # Draw bar
            pyxel.rect(bar_x + 1, bar_y, bar_width - 2, bar_height, color)
            
            # Draw label if provided
            if labels and i < len(labels):
                label_y = y + height + 2
                pyxel.text(bar_x, label_y, labels[i][:3], self.palette.get_color('ui_fg'))
    
    def draw_line_graph(self, x: int, y: int, width: int, height: int,
                       data: List[float], color: Optional[int] = None,
                       show_points: bool = True):
        """Draw a line graph"""
        if len(data) < 2:
            return
        
        color = color or self.palette.get_color('ui_accent')
        max_value = max(data) if max(data) > 0 else 1
        min_value = min(data)
        value_range = max_value - min_value if max_value != min_value else 1
        
        x_step = width / (len(data) - 1)
        
        # Draw lines
        for i in range(len(data) - 1):
            x1 = x + int(i * x_step)
            y1 = y + height - int((data[i] - min_value) / value_range * height)
            x2 = x + int((i + 1) * x_step)
            y2 = y + height - int((data[i + 1] - min_value) / value_range * height)
            
            pyxel.line(x1, y1, x2, y2, color)
            
            # Draw points
            if show_points:
                pyxel.pset(x1, y1, self.palette.get_color('ui_fg'))
        
        # Draw last point
        if show_points:
            last_x = x + width
            last_y = y + height - int((data[-1] - min_value) / value_range * height)
            pyxel.pset(last_x, last_y, self.palette.get_color('ui_fg'))
    
    def draw_pie_chart(self, cx: int, cy: int, radius: int,
                      data: List[float], colors: Optional[List[int]] = None,
                      labels: Optional[List[str]] = None):
        """Draw a pie chart (simplified using circles)"""
        if not data:
            return
        
        total = sum(data)
        if total == 0:
            return
        
        # Draw background circle
        pyxel.circb(cx, cy, radius, self.palette.get_color('ui_fg'))
        
        # Calculate angles
        start_angle = 0
        for i, value in enumerate(data):
            # Calculate slice size
            slice_angle = (value / total) * 360
            color = colors[i] if colors and i < len(colors) else (i % 16)
            
            # Draw slice (simplified - using lines from center)
            for angle in range(int(start_angle), int(start_angle + slice_angle)):
                rad = math.radians(angle)
                x = cx + int(radius * math.cos(rad))
                y = cy + int(radius * math.sin(rad))
                pyxel.line(cx, cy, x, y, color)
            
            start_angle += slice_angle
    
    def draw_heat_map(self, x: int, y: int, width: int, height: int,
                     data: List[List[float]], color_scale: Optional[List[int]] = None):
        """Draw a heat map"""
        if not data or not data[0]:
            return
        
        rows = len(data)
        cols = len(data[0])
        cell_width = width // cols
        cell_height = height // rows
        
        # Find data range
        flat_data = [val for row in data for val in row]
        max_val = max(flat_data) if flat_data else 1
        min_val = min(flat_data) if flat_data else 0
        val_range = max_val - min_val if max_val != min_val else 1
        
        # Default color scale (blue to red)
        if not color_scale:
            color_scale = [1, 5, 6, 13, 12, 10, 9, 8]  # Blue to red gradient
        
        for row in range(rows):
            for col in range(cols):
                value = data[row][col]
                # Normalize value to 0-1
                norm_value = (value - min_val) / val_range
                # Map to color scale
                color_idx = int(norm_value * (len(color_scale) - 1))
                color = color_scale[color_idx]
                
                # Draw cell
                cell_x = x + col * cell_width
                cell_y = y + row * cell_height
                pyxel.rect(cell_x, cell_y, cell_width, cell_height, color)
    
    def draw_progress_bar(self, x: int, y: int, width: int, height: int,
                         value: float, max_value: float = 100,
                         color: Optional[int] = None, show_text: bool = True):
        """Draw a progress bar"""
        if max_value <= 0:
            return
        
        progress = min(value / max_value, 1.0)
        color = color or self.palette.get_color('success')
        
        # Draw background
        pyxel.rect(x, y, width, height, self.palette.get_color('ui_bg'))
        pyxel.rectb(x, y, width, height, self.palette.get_color('ui_fg'))
        
        # Draw progress
        progress_width = int(width * progress)
        if progress_width > 0:
            pyxel.rect(x, y, progress_width, height, color)
        
        # Draw text
        if show_text:
            text = f"{int(progress * 100)}%"
            text_x = x + width // 2 - len(text) * 2
            text_y = y + height // 2 - 3
            pyxel.text(text_x, text_y, text, self.palette.get_color('ui_fg'))
    
    def draw_gauge(self, cx: int, cy: int, radius: int,
                  value: float, max_value: float = 100,
                  start_angle: float = 135, end_angle: float = 405):
        """Draw a circular gauge"""
        if max_value <= 0:
            return
        
        progress = min(value / max_value, 1.0)
        
        # Draw outer circle
        pyxel.circb(cx, cy, radius, self.palette.get_color('ui_fg'))
        
        # Draw progress arc
        angle_range = end_angle - start_angle
        current_angle = start_angle + angle_range * progress
        
        # Draw arc using lines (simplified)
        for angle in range(int(start_angle), int(current_angle), 5):
            rad = math.radians(angle)
            x1 = cx + int((radius - 2) * math.cos(rad))
            y1 = cy + int((radius - 2) * math.sin(rad))
            x2 = cx + int(radius * math.cos(rad))
            y2 = cy + int(radius * math.sin(rad))
            
            # Color based on value
            if progress < 0.3:
                color = self.palette.get_color('danger')
            elif progress < 0.7:
                color = self.palette.get_color('warning')
            else:
                color = self.palette.get_color('success')
            
            pyxel.line(x1, y1, x2, y2, color)
        
        # Draw center value
        text = f"{int(value)}"
        text_x = cx - len(text) * 2
        text_y = cy - 3
        pyxel.text(text_x, text_y, text, self.palette.get_color('ui_fg'))

class AnimationSystem:
    """Handles UI animations"""
    
    def __init__(self):
        self.animations = {}
        self.frame_count = 0
        
    def update(self):
        """Update all animations"""
        self.frame_count += 1
        
        # Update each animation
        for anim_id in list(self.animations.keys()):
            anim = self.animations[anim_id]
            anim['current_frame'] += 1
            
            if anim['current_frame'] >= anim['duration']:
                if anim['loop']:
                    anim['current_frame'] = 0
                else:
                    del self.animations[anim_id]
    
    def add_animation(self, anim_id: str, duration: int, loop: bool = False,
                     easing: str = "linear", **kwargs):
        """Add a new animation"""
        self.animations[anim_id] = {
            'duration': duration,
            'current_frame': 0,
            'loop': loop,
            'easing': easing,
            'data': kwargs
        }
    
    def get_progress(self, anim_id: str) -> float:
        """Get animation progress (0.0 to 1.0)"""
        if anim_id not in self.animations:
            return 0.0
        
        anim = self.animations[anim_id]
        progress = anim['current_frame'] / anim['duration']
        
        # Apply easing
        if anim['easing'] == 'ease_in':
            return progress * progress
        elif anim['easing'] == 'ease_out':
            return 1 - (1 - progress) * (1 - progress)
        elif anim['easing'] == 'ease_in_out':
            if progress < 0.5:
                return 2 * progress * progress
            else:
                return 1 - 2 * (1 - progress) * (1 - progress)
        else:  # linear
            return progress
    
    def interpolate(self, anim_id: str, start_value: float, end_value: float) -> float:
        """Interpolate a value based on animation progress"""
        progress = self.get_progress(anim_id)
        return start_value + (end_value - start_value) * progress
    
    def pulse(self, base_value: float, amplitude: float, frequency: float) -> float:
        """Create a pulsing effect"""
        return base_value + amplitude * math.sin(self.frame_count * frequency)
    
    def shake(self, base_x: int, base_y: int, intensity: int) -> Tuple[int, int]:
        """Create a shaking effect"""
        import random
        offset_x = random.randint(-intensity, intensity)
        offset_y = random.randint(-intensity, intensity)
        return base_x + offset_x, base_y + offset_y

class VisualSystem:
    """Main visual system integrating all components"""
    
    def __init__(self):
        self.palette_manager = PaletteManager()
        self.window_manager = WindowManager(self.palette_manager)
        self.visualizer = DataVisualizer(self.palette_manager)
        self.animation_system = AnimationSystem()
        
        # Create sample windows
        self._create_sample_ui()
    
    def _create_sample_ui(self):
        """Create sample UI elements for demonstration"""
        # Stats window
        self.stats_window = self.window_manager.create_window(
            10, 10, 100, 80, "City Statistics",
            draggable=True, has_minimize=True
        )
        
        # Graph window
        self.graph_window = self.window_manager.create_window(
            120, 10, 120, 60, "Population Graph",
            draggable=True, has_close=True
        )
        
        # Control panel
        self.control_window = self.window_manager.create_window(
            10, 100, 150, 40, "Controls",
            draggable=True, border_style="rounded"
        )
    
    def update(self):
        """Update visual system"""
        self.animation_system.update()
    
    def draw(self):
        """Draw all visual elements"""
        # Draw windows
        for window in self.window_manager.windows:
            self.window_manager.draw_window(window)
    
    def set_theme(self, theme: ColorTheme):
        """Change the color theme"""
        self.palette_manager.set_theme(theme)
    
    def draw_demo(self, x: int, y: int):
        """Draw demonstration of visual capabilities"""
        # Sample data
        bar_data = [30, 45, 60, 35, 80, 55]
        line_data = [10, 25, 30, 45, 35, 50, 45, 60, 55, 70]
        
        # Draw bar chart
        self.visualizer.draw_bar_chart(
            x, y, 80, 40, bar_data,
            labels=["R", "C", "I", "P", "T", "S"]
        )
        
        # Draw line graph
        self.visualizer.draw_line_graph(
            x + 90, y, 80, 40, line_data
        )
        
        # Draw progress bar
        progress = self.animation_system.pulse(50, 30, 0.05)
        self.visualizer.draw_progress_bar(
            x, y + 50, 100, 10, progress
        )
        
        # Draw gauge
        self.visualizer.draw_gauge(
            x + 130, y + 70, 20, progress
        )

# Integration helper
def integrate_visual_system(game_instance):
    """Integrate visual system with the main game"""
    visual_system = VisualSystem()
    game_instance.visual_system = visual_system
    
    # Override draw method to include visual system
    original_draw = game_instance.draw
    
    def enhanced_draw():
        original_draw()
        game_instance.visual_system.draw()
    
    game_instance.draw = enhanced_draw
    
    # Override update to include animations
    original_update = game_instance.update
    
    def enhanced_update():
        original_update()
        game_instance.visual_system.update()
    
    game_instance.update = enhanced_update
    
    return visual_system

# Test function
def test_visual_system():
    """Test the visual system"""
    pyxel.init(320, 240, title="Visual System Test")
    
    visual_system = VisualSystem()
    
    # Test different themes
    themes = list(ColorTheme)
    current_theme_idx = 0
    
    def update():
        visual_system.update()
        
        # Change theme with keys
        if pyxel.btnp(pyxel.KEY_SPACE):
            nonlocal current_theme_idx
            current_theme_idx = (current_theme_idx + 1) % len(themes)
            visual_system.set_theme(themes[current_theme_idx])
        
        # Handle mouse for windows
        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            visual_system.window_manager.handle_mouse(
                pyxel.mouse_x, pyxel.mouse_y, True
            )
        else:
            visual_system.window_manager.handle_mouse(
                pyxel.mouse_x, pyxel.mouse_y, False
            )
    
    def draw():
        pyxel.cls(visual_system.palette_manager.get_color('ui_bg'))
        
        # Draw demo visualizations
        visual_system.draw_demo(10, 150)
        
        # Draw windows
        visual_system.draw()
        
        # Show current theme
        theme_name = themes[current_theme_idx].value
        pyxel.text(250, 10, f"Theme: {theme_name}", 7)
        pyxel.text(250, 20, "Press SPACE to change", 7)
    
    pyxel.run(update, draw)

if __name__ == "__main__":
    test_visual_system()