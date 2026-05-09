"""
Advanced Window System for ConcLand
Professional UI window management with tabs, docking, and responsive layouts
"""

import pyxel
from typing import Dict, List, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import json

class WindowState(Enum):
    NORMAL = "normal"
    MINIMIZED = "minimized"
    MAXIMIZED = "maximized"
    DOCKED = "docked"
    HIDDEN = "hidden"

class DockPosition(Enum):
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
    CENTER = "center"
    FLOATING = "floating"

class TabAlignment(Enum):
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"

@dataclass
class Tab:
    """Tab component for tabbed windows"""
    id: str
    title: str
    content: Callable[[], None]  # Draw function
    icon: Optional[str] = None
    closeable: bool = True
    active: bool = False
    width: int = 60
    tooltip: str = ""

@dataclass
class WindowStyle:
    """Visual style for windows"""
    bg_color: int = 0
    fg_color: int = 7
    border_color: int = 7
    title_bg: int = 1
    title_fg: int = 7
    active_border: int = 12
    inactive_border: int = 5
    shadow: bool = True
    shadow_color: int = 0
    corner_radius: int = 0
    transparency: float = 1.0
    font_size: int = 6

@dataclass
class Panel:
    """Panel component for split layouts"""
    id: str
    x: int
    y: int
    width: int
    height: int
    content: Optional[Callable[[], None]] = None
    resizable: bool = True
    min_width: int = 50
    min_height: int = 30
    children: List['Panel'] = field(default_factory=list)
    split_direction: str = "horizontal"  # horizontal or vertical
    split_ratio: float = 0.5

class AdvancedWindow:
    """Advanced window with professional features"""
    
    def __init__(self, id: str, x: int, y: int, width: int, height: int, title: str = ""):
        self.id = id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title
        
        # State
        self.state = WindowState.NORMAL
        self.visible = True
        self.focused = False
        self.z_order = 0
        
        # Features
        self.draggable = True
        self.resizable = True
        self.has_close = True
        self.has_minimize = True
        self.has_maximize = True
        self.has_menu = False
        
        # Docking
        self.dockable = True
        self.dock_position = DockPosition.FLOATING
        self.dock_size_ratio = 0.3
        
        # Tabs
        self.tabs: List[Tab] = []
        self.active_tab_idx = 0
        self.tab_alignment = TabAlignment.TOP
        
        # Panels
        self.panels: List[Panel] = []
        self.layout_type = "single"  # single, split, grid
        
        # Style
        self.style = WindowStyle()
        
        # Callbacks
        self.on_close: Optional[Callable] = None
        self.on_resize: Optional[Callable] = None
        self.on_focus: Optional[Callable] = None
        
        # Animation
        self.animation_state = {}
        
        # Content
        self.content_scroll_x = 0
        self.content_scroll_y = 0
        self.content_width = width
        self.content_height = height
        
    def add_tab(self, tab_id: str, title: str, content: Callable, **kwargs) -> Tab:
        """Add a tab to the window"""
        tab = Tab(tab_id, title, content, **kwargs)
        self.tabs.append(tab)
        if len(self.tabs) == 1:
            tab.active = True
        return tab
    
    def set_active_tab(self, tab_id: str):
        """Set the active tab"""
        for i, tab in enumerate(self.tabs):
            tab.active = (tab.id == tab_id)
            if tab.active:
                self.active_tab_idx = i
    
    def close_tab(self, tab_id: str):
        """Close a tab"""
        self.tabs = [t for t in self.tabs if t.id != tab_id]
        if self.active_tab_idx >= len(self.tabs):
            self.active_tab_idx = max(0, len(self.tabs) - 1)
        if self.tabs and self.active_tab_idx < len(self.tabs):
            self.tabs[self.active_tab_idx].active = True
    
    def dock(self, position: DockPosition):
        """Dock the window to a position"""
        self.dock_position = position
        self.state = WindowState.DOCKED
    
    def undock(self):
        """Undock the window"""
        self.dock_position = DockPosition.FLOATING
        self.state = WindowState.NORMAL
    
    def minimize(self):
        """Minimize the window"""
        self.state = WindowState.MINIMIZED
    
    def maximize(self):
        """Maximize the window"""
        self.state = WindowState.MAXIMIZED
    
    def restore(self):
        """Restore the window to normal state"""
        self.state = WindowState.NORMAL
    
    def close(self):
        """Close the window"""
        if self.on_close:
            if not self.on_close():
                return  # Cancelled
        self.visible = False
        self.state = WindowState.HIDDEN

class WindowSystem:
    """Advanced window management system"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.windows: Dict[str, AdvancedWindow] = {}
        self.window_order: List[str] = []
        self.focused_window: Optional[str] = None
        
        # Docking areas
        self.dock_areas = {
            DockPosition.LEFT: (0, 0, screen_width // 4, screen_height),
            DockPosition.RIGHT: (3 * screen_width // 4, 0, screen_width // 4, screen_height),
            DockPosition.TOP: (0, 0, screen_width, screen_height // 4),
            DockPosition.BOTTOM: (0, 3 * screen_height // 4, screen_width, screen_height // 4),
            DockPosition.CENTER: (screen_width // 4, screen_height // 4, 
                                 screen_width // 2, screen_height // 2)
        }
        
        # Dragging state
        self.dragging_window: Optional[str] = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        # Resizing state
        self.resizing_window: Optional[str] = None
        self.resize_edge = ""  # n, s, e, w, ne, nw, se, sw
        
        # Theme
        self.default_style = WindowStyle()
        
        # Layout management
        self.layout_presets = self._create_layout_presets()
        
    def _create_layout_presets(self) -> Dict[str, Dict]:
        """Create predefined layout presets"""
        return {
            "default": {
                "main": {"dock": DockPosition.CENTER, "size": (0.6, 0.6)},
                "sidebar": {"dock": DockPosition.RIGHT, "size": (0.3, 1.0)},
                "toolbar": {"dock": DockPosition.TOP, "size": (1.0, 0.1)}
            },
            "development": {
                "editor": {"dock": DockPosition.CENTER, "size": (0.5, 0.7)},
                "console": {"dock": DockPosition.BOTTOM, "size": (1.0, 0.3)},
                "inspector": {"dock": DockPosition.RIGHT, "size": (0.25, 0.7)},
                "explorer": {"dock": DockPosition.LEFT, "size": (0.25, 0.7)}
            },
            "analysis": {
                "main": {"dock": DockPosition.LEFT, "size": (0.4, 1.0)},
                "charts": {"dock": DockPosition.CENTER, "size": (0.6, 0.6)},
                "data": {"dock": DockPosition.BOTTOM, "size": (0.6, 0.4)}
            }
        }
    
    def create_window(self, window_id: str, x: int, y: int, 
                     width: int, height: int, title: str = "", **kwargs) -> AdvancedWindow:
        """Create a new window"""
        window = AdvancedWindow(window_id, x, y, width, height, title)
        
        # Apply kwargs
        for key, value in kwargs.items():
            if hasattr(window, key):
                setattr(window, key, value)
        
        self.windows[window_id] = window
        self.window_order.append(window_id)
        self.focus_window(window_id)
        
        return window
    
    def focus_window(self, window_id: str):
        """Focus a window"""
        if window_id not in self.windows:
            return
        
        # Update focus state
        for wid in self.windows:
            self.windows[wid].focused = (wid == window_id)
        
        self.focused_window = window_id
        
        # Bring to front
        if window_id in self.window_order:
            self.window_order.remove(window_id)
            self.window_order.append(window_id)
    
    def close_window(self, window_id: str):
        """Close a window"""
        if window_id in self.windows:
            self.windows[window_id].close()
            del self.windows[window_id]
            if window_id in self.window_order:
                self.window_order.remove(window_id)
    
    def apply_layout(self, preset_name: str):
        """Apply a layout preset"""
        if preset_name not in self.layout_presets:
            return
        
        preset = self.layout_presets[preset_name]
        
        for window_id, config in preset.items():
            if window_id in self.windows:
                window = self.windows[window_id]
                
                # Apply docking
                if "dock" in config:
                    window.dock(config["dock"])
                    
                    # Calculate position and size based on dock
                    if config["dock"] != DockPosition.FLOATING:
                        x, y, w, h = self.dock_areas[config["dock"]]
                        if "size" in config:
                            size_w, size_h = config["size"]
                            window.width = int(w * size_w)
                            window.height = int(h * size_h)
                        else:
                            window.width = w
                            window.height = h
                        window.x = x
                        window.y = y
    
    def handle_mouse(self, mx: int, my: int, left_click: bool, right_click: bool):
        """Handle mouse input"""
        # Check windows in reverse order (top to bottom)
        for window_id in reversed(self.window_order):
            window = self.windows[window_id]
            
            if not window.visible:
                continue
            
            # Check if mouse is over window
            if (window.x <= mx < window.x + window.width and
                window.y <= my < window.y + window.height):
                
                # Focus window on click
                if left_click and not window.focused:
                    self.focus_window(window_id)
                
                # Handle window controls
                if left_click:
                    # Check close button
                    if window.has_close:
                        close_x = window.x + window.width - 10
                        close_y = window.y + 2
                        if close_x <= mx < close_x + 8 and close_y <= my < close_y + 8:
                            window.close()
                            return
                    
                    # Check minimize button
                    if window.has_minimize:
                        min_x = window.x + window.width - 20
                        min_y = window.y + 2
                        if min_x <= mx < min_x + 8 and min_y <= my < min_y + 8:
                            window.minimize()
                            return
                    
                    # Check maximize button
                    if window.has_maximize:
                        max_x = window.x + window.width - 30
                        max_y = window.y + 2
                        if max_x <= mx < max_x + 8 and max_y <= my < max_y + 8:
                            if window.state == WindowState.MAXIMIZED:
                                window.restore()
                            else:
                                window.maximize()
                            return
                    
                    # Check for tab clicks
                    if window.tabs:
                        tab_y = window.y + 12
                        tab_x = window.x + 2
                        for i, tab in enumerate(window.tabs):
                            if tab_x <= mx < tab_x + tab.width and tab_y <= my < tab_y + 12:
                                window.set_active_tab(tab.id)
                                return
                            tab_x += tab.width + 2
                    
                    # Start dragging
                    if window.draggable and window.y <= my < window.y + 12:
                        self.dragging_window = window_id
                        self.drag_offset_x = mx - window.x
                        self.drag_offset_y = my - window.y
                        return
                    
                    # Check for resize
                    if window.resizable:
                        # Check corners and edges
                        edge_size = 5
                        if (window.x + window.width - edge_size <= mx < window.x + window.width and
                            window.y + window.height - edge_size <= my < window.y + window.height):
                            self.resizing_window = window_id
                            self.resize_edge = "se"
                            return
                
                break  # Stop checking other windows
        
        # Handle dragging
        if not left_click:
            self.dragging_window = None
            self.resizing_window = None
        elif self.dragging_window:
            window = self.windows[self.dragging_window]
            window.x = mx - self.drag_offset_x
            window.y = my - self.drag_offset_y
            
            # Snap to edges
            snap_distance = 10
            if window.x < snap_distance:
                window.x = 0
            elif window.x + window.width > self.screen_width - snap_distance:
                window.x = self.screen_width - window.width
            
            if window.y < snap_distance:
                window.y = 0
            elif window.y + window.height > self.screen_height - snap_distance:
                window.y = self.screen_height - window.height
        elif self.resizing_window:
            window = self.windows[self.resizing_window]
            if self.resize_edge == "se":
                window.width = max(100, mx - window.x)
                window.height = max(50, my - window.y)
    
    def draw(self):
        """Draw all windows"""
        # Draw windows in order
        for window_id in self.window_order:
            window = self.windows[window_id]
            
            if not window.visible:
                continue
            
            if window.state == WindowState.MINIMIZED:
                self._draw_minimized_window(window)
            elif window.state == WindowState.MAXIMIZED:
                self._draw_maximized_window(window)
            else:
                self._draw_window(window)
    
    def _draw_window(self, window: AdvancedWindow):
        """Draw a normal window"""
        x, y, w, h = window.x, window.y, window.width, window.height
        style = window.style
        
        # Draw shadow
        if style.shadow:
            pyxel.rect(x + 2, y + 2, w, h, style.shadow_color)
        
        # Draw background
        pyxel.rect(x, y, w, h, style.bg_color)
        
        # Draw border
        border_color = style.active_border if window.focused else style.inactive_border
        pyxel.rectb(x, y, w, h, border_color)
        
        # Draw title bar
        title_height = 12
        pyxel.rect(x, y, w, title_height, style.title_bg)
        pyxel.line(x, y + title_height, x + w - 1, y + title_height, border_color)
        
        # Draw title
        if window.title:
            title_x = x + 2
            title_y = y + 3
            pyxel.text(title_x, title_y, window.title, style.title_fg)
        
        # Draw window controls
        control_y = y + 2
        
        if window.has_close:
            close_x = x + w - 10
            pyxel.text(close_x, control_y, "x", 8)
        
        if window.has_minimize:
            min_x = x + w - 20
            pyxel.text(min_x, control_y, "_", style.title_fg)
        
        if window.has_maximize:
            max_x = x + w - 30
            pyxel.text(max_x, control_y, "□", style.title_fg)
        
        # Draw tabs
        if window.tabs:
            self._draw_tabs(window)
        
        # Draw content
        content_y = y + title_height + (14 if window.tabs else 0)
        content_height = h - title_height - (14 if window.tabs else 0)
        
        # Set clipping region for content
        if window.tabs and window.active_tab_idx < len(window.tabs):
            active_tab = window.tabs[window.active_tab_idx]
            if active_tab.content:
                # Call tab content draw function
                active_tab.content()
        
        # Draw resize handle
        if window.resizable and window.focused:
            handle_size = 5
            handle_x = x + w - handle_size
            handle_y = y + h - handle_size
            pyxel.line(handle_x, handle_y + handle_size, 
                      handle_x + handle_size, handle_y, style.fg_color)
    
    def _draw_tabs(self, window: AdvancedWindow):
        """Draw window tabs"""
        if not window.tabs:
            return
        
        x, y = window.x, window.y + 12
        tab_height = 14
        
        # Draw tab bar background
        pyxel.rect(x, y, window.width, tab_height, window.style.bg_color)
        
        # Draw tabs
        tab_x = x + 2
        for i, tab in enumerate(window.tabs):
            # Tab background
            tab_color = window.style.title_bg if tab.active else window.style.bg_color
            pyxel.rect(tab_x, y, tab.width, tab_height - 2, tab_color)
            
            # Tab border
            if tab.active:
                pyxel.rectb(tab_x, y, tab.width, tab_height - 2, window.style.active_border)
            
            # Tab title
            title_x = tab_x + 2
            title_y = y + 3
            pyxel.text(title_x, title_y, tab.title[:8], window.style.fg_color)
            
            # Close button
            if tab.closeable:
                close_x = tab_x + tab.width - 8
                pyxel.text(close_x, title_y, "x", 8)
            
            tab_x += tab.width + 2
    
    def _draw_minimized_window(self, window: AdvancedWindow):
        """Draw a minimized window"""
        # Draw as a small bar at the bottom
        x = window.x
        y = self.screen_height - 20
        width = 100
        height = 18
        
        pyxel.rect(x, y, width, height, window.style.bg_color)
        pyxel.rectb(x, y, width, height, window.style.border_color)
        pyxel.text(x + 2, y + 6, window.title[:12], window.style.fg_color)
    
    def _draw_maximized_window(self, window: AdvancedWindow):
        """Draw a maximized window"""
        # Store original position and size
        orig_x, orig_y = window.x, window.y
        orig_w, orig_h = window.width, window.height
        
        # Temporarily set to full screen
        window.x, window.y = 0, 0
        window.width = self.screen_width
        window.height = self.screen_height
        
        # Draw normally
        self._draw_window(window)
        
        # Restore original values
        window.x, window.y = orig_x, orig_y
        window.width, window.height = orig_w, orig_h

# Demo and test
def test_window_system():
    """Test the advanced window system"""
    pyxel.init(400, 300, title="Advanced Window System")
    
    window_system = WindowSystem(400, 300)
    
    # Create sample windows
    main_window = window_system.create_window(
        "main", 50, 50, 200, 150, "Main Window"
    )
    
    # Add tabs to main window
    def draw_tab1():
        pyxel.text(60, 80, "Tab 1 Content", 7)
    
    def draw_tab2():
        pyxel.text(60, 80, "Tab 2 Content", 7)
    
    main_window.add_tab("tab1", "General", draw_tab1)
    main_window.add_tab("tab2", "Settings", draw_tab2)
    
    # Create tool window
    tool_window = window_system.create_window(
        "tools", 260, 50, 120, 100, "Tools",
        has_maximize=False
    )
    
    # Create docked window
    sidebar = window_system.create_window(
        "sidebar", 10, 10, 100, 280, "Sidebar"
    )
    sidebar.dock(DockPosition.LEFT)
    
    def update():
        # Handle mouse
        window_system.handle_mouse(
            pyxel.mouse_x, pyxel.mouse_y,
            pyxel.btn(pyxel.MOUSE_BUTTON_LEFT),
            pyxel.btn(pyxel.MOUSE_BUTTON_RIGHT)
        )
        
        # Test layout presets with keys
        if pyxel.btnp(pyxel.KEY_1):
            window_system.apply_layout("default")
        elif pyxel.btnp(pyxel.KEY_2):
            window_system.apply_layout("development")
        elif pyxel.btnp(pyxel.KEY_3):
            window_system.apply_layout("analysis")
    
    def draw():
        pyxel.cls(1)
        window_system.draw()
        
        # Instructions
        pyxel.text(5, 285, "Press 1-3 for layouts, drag windows", 7)
    
    pyxel.run(update, draw)

if __name__ == "__main__":
    test_window_system()