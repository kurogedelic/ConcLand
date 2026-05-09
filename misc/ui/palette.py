"""
Tool palette UI module for ConcLand city simulation
"""
import pyxel
import json
from typing import List, Optional, Dict, Any, Tuple
from tools.base_tool import BaseTool, BuildingTool, InfrastructureTool, TerrainTool, UtilityTool

class ToolPalette:
    """Modern tabbed tool palette with category organization"""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y  
        self.width = width
        self.height = height
        
        # UI Configuration
        self.tab_height = 20
        self.icon_size = 16
        self.button_size = 24
        self.buttons_per_row = 4
        self.button_margin = 4
        
        # State
        self.tools: List[BaseTool] = []
        self.categories: Dict[str, Dict[str, Any]] = {}
        self.current_category = "residential"
        self.selected_tool_index = 0
        self.hovered_tool_index = -1
        self.hovered_tab = ""
        
        # Load tool definitions
        self.load_tools()
        
    def load_tools(self):
        """Load tool definitions from JSON"""
        try:
            with open('data/tools.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.categories = data['categories']
            
            # Create tool instances
            for tool_data in data['tools']:
                tool = self._create_tool_from_data(tool_data)
                if tool:
                    self.tools.append(tool)
                    
        except FileNotFoundError:
            # Fallback to basic tools if JSON not found
            self._create_fallback_tools()
    
    def _create_tool_from_data(self, data: Dict[str, Any]) -> Optional[BaseTool]:
        """Create a tool instance from JSON data"""
        tool_type = data.get('type', 'building')
        
        if tool_type == 'building':
            return BuildingTool(
                tool_id=data['id'],
                name=data['name'],
                japanese_name=data['japanese_name'],
                category=data['category'],
                cost=data['cost'],
                icon_index=data['icon_index'],
                building_type=data['building_type'],
                size=tuple(data.get('size', [1, 1]))
            )
        elif tool_type == 'infrastructure':
            return InfrastructureTool(
                tool_id=data['id'],
                name=data['name'],
                japanese_name=data['japanese_name'],
                category=data['category'],
                cost=data['cost'],
                icon_index=data['icon_index'],
                infrastructure_type=data['infrastructure_type']
            )
        elif tool_type == 'terrain':
            return TerrainTool(
                tool_id=data['id'],
                name=data['name'],
                japanese_name=data['japanese_name'],
                category=data['category'],
                cost=data['cost'],
                icon_index=data['icon_index'],
                terrain_type=data['terrain_type']
            )
        elif tool_type == 'utility':
            return UtilityTool(
                tool_id=data['id'],
                name=data['name'],
                japanese_name=data['japanese_name'],
                category=data['category'],
                cost=data['cost'],
                icon_index=data['icon_index']
            )
        
        return None
    
    def _create_fallback_tools(self):
        """Create basic tools if JSON loading fails"""
        self.categories = {
            "residential": {"name": "Residential", "japanese_name": "住宅", "color": [100, 200, 100]},
            "utilities": {"name": "Utilities", "japanese_name": "ユーティリティ", "color": [200, 50, 50]}
        }
        
        self.tools = [
            BuildingTool("residence", "Residence", "住宅", "residential", 100, 0, "RESIDENCE"),
            UtilityTool("bulldozer", "Bulldozer", "ブルドーザー", "utilities", 0, 12)
        ]
    
    def get_current_category_tools(self) -> List[BaseTool]:
        """Get tools for the current category"""
        return [tool for tool in self.tools if tool.category == self.current_category]
    
    def get_category_tabs(self) -> List[str]:
        """Get list of category tabs that have tools"""
        used_categories = set(tool.category for tool in self.tools)
        return [cat for cat in self.categories.keys() if cat in used_categories]
    
    def update(self, mouse_x: int, mouse_y: int):
        """Update palette state based on mouse position"""
        self.hovered_tool_index = -1
        self.hovered_tab = ""
        
        # Check tab hover
        tabs = self.get_category_tabs()
        tab_width = self.width // len(tabs) if tabs else self.width
        
        if self.y <= mouse_y <= self.y + self.tab_height:
            for i, category in enumerate(tabs):
                tab_x = self.x + i * tab_width
                if tab_x <= mouse_x <= tab_x + tab_width:
                    self.hovered_tab = category
                    break
        
        # Check tool button hover
        tools = self.get_current_category_tools()
        if tools and self.y + self.tab_height <= mouse_y <= self.y + self.height:
            relative_x = mouse_x - self.x - self.button_margin
            relative_y = mouse_y - self.y - self.tab_height - self.button_margin
            
            if relative_x >= 0 and relative_y >= 0:
                col = relative_x // (self.button_size + self.button_margin)
                row = relative_y // (self.button_size + self.button_margin)
                
                if col < self.buttons_per_row:
                    index = row * self.buttons_per_row + col
                    if index < len(tools):
                        # Check if mouse is within button bounds
                        button_x = col * (self.button_size + self.button_margin)
                        button_y = row * (self.button_size + self.button_margin)
                        
                        if (button_x <= relative_x <= button_x + self.button_size and
                            button_y <= relative_y <= button_y + self.button_size):
                            self.hovered_tool_index = index
    
    def handle_click(self, mouse_x: int, mouse_y: int) -> Optional[BaseTool]:
        """Handle mouse click on palette. Returns selected tool or None"""
        # Check tab clicks
        tabs = self.get_category_tabs()
        tab_width = self.width // len(tabs) if tabs else self.width
        
        if self.y <= mouse_y <= self.y + self.tab_height:
            for i, category in enumerate(tabs):
                tab_x = self.x + i * tab_width
                if tab_x <= mouse_x <= tab_x + tab_width:
                    self.current_category = category
                    self.selected_tool_index = 0
                    return None
        
        # Check tool button clicks
        if self.hovered_tool_index >= 0:
            tools = self.get_current_category_tools()
            if self.hovered_tool_index < len(tools):
                self.selected_tool_index = self.hovered_tool_index
                return tools[self.selected_tool_index]
        
        return None
    
    def get_selected_tool(self) -> Optional[BaseTool]:
        """Get the currently selected tool"""
        tools = self.get_current_category_tools()
        if 0 <= self.selected_tool_index < len(tools):
            return tools[self.selected_tool_index]
        return None
    
    def get_hovered_tool(self) -> Optional[BaseTool]:
        """Get the currently hovered tool"""
        if self.hovered_tool_index >= 0:
            tools = self.get_current_category_tools()
            if self.hovered_tool_index < len(tools):
                return tools[self.hovered_tool_index]
        return None
    
    def draw(self):
        """Draw the tool palette"""
        # Load UI assets if available
        try:
            if pyxel.images[3].width > 0:
                self._draw_with_ui_assets()
            else:
                self._draw_basic()
        except:
            self._draw_basic()
    
    def _draw_basic(self):
        """Draw basic palette without UI assets"""
        # Draw background
        pyxel.rect(self.x, self.y, self.width, self.height, 1)
        pyxel.rectb(self.x, self.y, self.width, self.height, 7)
        
        # Draw tabs
        self._draw_tabs()
        
        # Draw tools
        self._draw_tools()
        
        # Draw tooltip
        self._draw_tooltip()
    
    def _draw_with_ui_assets(self):
        """Draw enhanced palette with UI assets"""
        # Draw panel background using UI assets
        panel_size = 64
        for py in range(0, self.height, panel_size):
            for px in range(0, self.width, panel_size):
                # Use textured panel (third panel type)
                pyxel.blt(self.x + px, self.y + py, 3, 
                         panel_size * 2, 0, panel_size, panel_size, 0)
        
        # Draw border
        pyxel.rectb(self.x, self.y, self.width, self.height, 7)
        
        # Draw tabs with enhanced style
        self._draw_enhanced_tabs()
        
        # Draw tools with enhanced buttons
        self._draw_enhanced_tools()
        
        # Draw tooltip
        self._draw_tooltip()
    
    def _draw_tabs(self):
        """Draw category tabs"""
        tabs = self.get_category_tabs()
        if not tabs:
            return
            
        tab_width = self.width // len(tabs)
        
        for i, category in enumerate(tabs):
            tab_x = self.x + i * tab_width
            
            # Tab background
            is_active = category == self.current_category
            is_hovered = category == self.hovered_tab
            
            bg_color = 7 if is_active else (6 if is_hovered else 5)
            pyxel.rect(tab_x, self.y, tab_width, self.tab_height, bg_color)
            pyxel.rectb(tab_x, self.y, tab_width, self.tab_height, 7)
            
            # Tab text
            text = self.categories[category]['japanese_name']
            text_width = len(text) * 4
            text_x = tab_x + (tab_width - text_width) // 2
            text_y = self.y + (self.tab_height - 6) // 2
            
            text_color = 0 if is_active else 7
            pyxel.text(text_x, text_y, text, text_color)
    
    def _draw_tools(self):
        """Draw tool buttons"""
        tools = self.get_current_category_tools()
        if not tools:
            return
        
        content_y = self.y + self.tab_height
        
        for i, tool in enumerate(tools):
            row = i // self.buttons_per_row
            col = i % self.buttons_per_row
            
            button_x = self.x + self.button_margin + col * (self.button_size + self.button_margin)
            button_y = content_y + self.button_margin + row * (self.button_size + self.button_margin)
            
            # Skip if button would be outside palette
            if button_y + self.button_size > self.y + self.height:
                break
            
            # Button background
            is_selected = i == self.selected_tool_index
            is_hovered = i == self.hovered_tool_index
            
            bg_color = 10 if is_selected else (9 if is_hovered else 5)
            pyxel.rect(button_x, button_y, self.button_size, self.button_size, bg_color)
            pyxel.rectb(button_x, button_y, self.button_size, self.button_size, 7)
            
            # Tool icon
            icon_x = button_x + (self.button_size - self.icon_size) // 2
            icon_y = button_y + (self.button_size - self.icon_size) // 2
            
            # Draw icon from sprite sheet
            sprite_col = tool.icon_index % 8
            sprite_row = tool.icon_index // 8
            sprite_x = sprite_col * self.icon_size
            sprite_y = sprite_row * self.icon_size
            
            pyxel.blt(icon_x, icon_y, 2, sprite_x, sprite_y, 
                     self.icon_size, self.icon_size, 0)
    
    def _draw_tooltip(self):
        """Draw tooltip for hovered tool"""
        hovered_tool = self.get_hovered_tool()
        if not hovered_tool:
            return
        
        tooltip_text = hovered_tool.get_tooltip()
        tooltip_width = len(tooltip_text) * 4 + 8
        tooltip_height = 12
        
        # Position tooltip at top of palette
        tooltip_x = self.x + (self.width - tooltip_width) // 2
        tooltip_y = self.y - tooltip_height - 2
        
        # Draw tooltip background
        pyxel.rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height, 0)
        pyxel.rectb(tooltip_x, tooltip_y, tooltip_width, tooltip_height, 7)
        
        # Draw tooltip text
        pyxel.text(tooltip_x + 4, tooltip_y + 3, tooltip_text, 7)
    
    def _draw_enhanced_tabs(self):
        """Draw enhanced category tabs with UI assets"""
        tabs = self.get_category_tabs()
        if not tabs:
            return
            
        tab_width = self.width // len(tabs)
        button_frame_size = 32
        
        for i, category in enumerate(tabs):
            tab_x = self.x + i * tab_width
            
            # Determine button state
            is_active = category == self.current_category
            is_hovered = category == self.hovered_tab
            
            frame_index = 2 if is_active else (1 if is_hovered else 0)
            
            # Draw button frame from UI assets (if available)
            if tab_width >= button_frame_size:
                pyxel.blt(tab_x, self.y, 3, 
                         frame_index * button_frame_size, 0, 
                         min(tab_width, button_frame_size), self.tab_height, 0)
            else:
                # Fallback to basic drawing
                bg_color = 7 if is_active else (6 if is_hovered else 5)
                pyxel.rect(tab_x, self.y, tab_width, self.tab_height, bg_color)
                pyxel.rectb(tab_x, self.y, tab_width, self.tab_height, 7)
            
            # Tab text
            text = self.categories[category]['japanese_name']
            text_width = len(text) * 4
            text_x = tab_x + (tab_width - text_width) // 2
            text_y = self.y + (self.tab_height - 6) // 2
            
            text_color = 0 if is_active else 7
            pyxel.text(text_x, text_y, text, text_color)
    
    def _draw_enhanced_tools(self):
        """Draw enhanced tool buttons with UI assets"""
        tools = self.get_current_category_tools()
        if not tools:
            return
        
        content_y = self.y + self.tab_height
        button_frame_size = 32
        
        for i, tool in enumerate(tools):
            row = i // self.buttons_per_row
            col = i % self.buttons_per_row
            
            button_x = self.x + self.button_margin + col * (self.button_size + self.button_margin)
            button_y = content_y + self.button_margin + row * (self.button_size + self.button_margin)
            
            # Skip if button would be outside palette
            if button_y + self.button_size > self.y + self.height:
                break
            
            # Determine button state
            is_selected = i == self.selected_tool_index
            is_hovered = i == self.hovered_tool_index
            
            frame_index = 2 if is_selected else (1 if is_hovered else 0)
            
            # Draw enhanced button frame
            if self.button_size <= button_frame_size:
                # Scale down button frame if needed
                pyxel.blt(button_x, button_y, 3,
                         frame_index * button_frame_size, 0,
                         self.button_size, self.button_size, 0)
            else:
                # Fallback to basic drawing for large buttons
                bg_color = 10 if is_selected else (9 if is_hovered else 5)
                pyxel.rect(button_x, button_y, self.button_size, self.button_size, bg_color)
                pyxel.rectb(button_x, button_y, self.button_size, self.button_size, 7)
            
            # Tool icon
            icon_x = button_x + (self.button_size - self.icon_size) // 2
            icon_y = button_y + (self.button_size - self.icon_size) // 2
            
            # Draw icon with slight glow effect if selected
            if is_selected:
                # Draw glow effect
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx != 0 or dy != 0:
                            sprite_col = tool.icon_index % 8
                            sprite_row = tool.icon_index // 8
                            sprite_x = sprite_col * self.icon_size
                            sprite_y = sprite_row * self.icon_size
                            
                            pyxel.blt(icon_x + dx, icon_y + dy, 2, 
                                     sprite_x, sprite_y, 
                                     self.icon_size, self.icon_size, 0)
            
            # Draw main icon
            sprite_col = tool.icon_index % 8
            sprite_row = tool.icon_index // 8
            sprite_x = sprite_col * self.icon_size
            sprite_y = sprite_row * self.icon_size
            
            pyxel.blt(icon_x, icon_y, 2, sprite_x, sprite_y, 
                     self.icon_size, self.icon_size, 0)