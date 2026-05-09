"""
Advanced UI System for ConcLand
Provides enhanced user interface with graphs, menus, and statistics
"""
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

class UIPanel(Enum):
    MAIN_GAME = "main"
    STATISTICS = "stats"
    ECONOMY = "economy"
    TRAFFIC = "traffic"
    DISASTERS = "disasters"
    POLICIES = "policies"
    BUILDING_INFO = "building_info"

@dataclass
class GraphData:
    """Data for drawing graphs"""
    values: List[float]
    max_values: int = 60  # Keep 60 data points (1 minute at 60 FPS)
    color: int = 7
    name: str = ""
    
    def add_value(self, value: float):
        """Add new value to graph"""
        self.values.append(value)
        if len(self.values) > self.max_values:
            self.values.pop(0)
    
    def get_max_value(self) -> float:
        """Get maximum value for scaling"""
        return max(self.values) if self.values else 1.0
    
    def get_min_value(self) -> float:
        """Get minimum value for scaling"""
        return min(self.values) if self.values else 0.0

@dataclass
class MenuItem:
    """Menu item definition"""
    id: str
    text: str
    japanese_text: str
    action: Optional[str] = None
    shortcut_key: Optional[int] = None
    enabled: bool = True
    submenu: Optional[List['MenuItem']] = None

class AdvancedUI:
    """Advanced UI system with panels and graphs"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Current UI state
        self.current_panel = UIPanel.MAIN_GAME
        self.show_fps = True
        self.show_debug_info = False
        
        # Graph data
        self.graphs: Dict[str, GraphData] = {
            "population": GraphData([], name="人口", color=11),
            "funds": GraphData([], name="資金", color=10), 
            "gdp": GraphData([], name="GDP", color=12),
            "traffic": GraphData([], name="交通量", color=8),
            "pollution": GraphData([], name="汚染", color=2),
            "land_value": GraphData([], name="地価", color=14)
        }
        
        # Menu system
        self.main_menu_visible = False
        self.current_menu: Optional[List[MenuItem]] = None
        self.menu_selection = 0
        
        # Panel positions and sizes
        self.info_panel_height = 32
        self.side_panel_width = 200
        self.graph_panel_height = 120
        
        # Animation timers
        self.notification_timer = 0
        self.notification_message = ""
        self.transition_timer = 0
        
        # Initialize menus
        self._create_menus()
    
    def _create_menus(self):
        """Create menu structure"""
        self.menus = {
            "main": [
                MenuItem("statistics", "Statistics", "統計", "show_statistics", ord('S')),
                MenuItem("economy", "Economy", "経済", "show_economy", ord('E')),
                MenuItem("traffic", "Traffic", "交通", "show_traffic", ord('T')),
                MenuItem("disasters", "Disasters", "災害", "show_disasters", ord('D')),
                MenuItem("policies", "Policies", "政策", "show_policies", ord('P')),
                MenuItem("settings", "Settings", "設定", submenu=[
                    MenuItem("fps_toggle", "Toggle FPS", "FPS表示切替", "toggle_fps"),
                    MenuItem("debug_toggle", "Toggle Debug", "デバッグ表示切替", "toggle_debug"),
                    MenuItem("language", "Language", "言語設定", "toggle_language")
                ]),
                MenuItem("save", "Save Game", "ゲーム保存", "save_game", ord('O')),
                MenuItem("load", "Load Game", "ゲーム読込", "load_game", ord('I')),
                MenuItem("quit", "Quit", "終了", "quit_game", ord('Q'))
            ]
        }
    
    def update(self, game_data: Dict[str, Any]):
        """Update UI system with game data"""
        # Update graph data
        if "population" in game_data:
            self.graphs["population"].add_value(game_data["population"])
        if "funds" in game_data:
            self.graphs["funds"].add_value(game_data["funds"])
        if "gdp" in game_data:
            self.graphs["gdp"].add_value(game_data["gdp"])
        if "total_traffic" in game_data:
            self.graphs["traffic"].add_value(game_data["total_traffic"])
        if "avg_pollution" in game_data:
            self.graphs["pollution"].add_value(game_data["avg_pollution"])
        if "avg_land_value" in game_data:
            self.graphs["land_value"].add_value(game_data["avg_land_value"])
        
        # Update timers
        if self.notification_timer > 0:
            self.notification_timer -= 1
        
        if self.transition_timer > 0:
            self.transition_timer -= 1
    
    def handle_input(self, key_pressed: int) -> Optional[str]:
        """Handle UI input and return action if any"""
        import pyxel
        
        # Menu navigation
        if self.main_menu_visible:
            if key_pressed == pyxel.KEY_UP:
                self.menu_selection = max(0, self.menu_selection - 1)
            elif key_pressed == pyxel.KEY_DOWN:
                self.menu_selection = min(len(self.current_menu) - 1, self.menu_selection + 1)
            elif key_pressed == pyxel.KEY_ENTER:
                return self._execute_menu_action()
            elif key_pressed == pyxel.KEY_ESCAPE:
                self.main_menu_visible = False
        
        # Global shortcuts
        else:
            if key_pressed == pyxel.KEY_ESCAPE or key_pressed == ord('M'):
                self.toggle_main_menu()
            elif key_pressed == ord('S') and not self.main_menu_visible:
                return "show_statistics"
            elif key_pressed == ord('E') and not self.main_menu_visible:
                return "show_economy"
            elif key_pressed == ord('T') and not self.main_menu_visible:
                return "show_traffic"
            elif key_pressed == ord('D') and not self.main_menu_visible:
                return "show_disasters"
            elif key_pressed == ord('P') and not self.main_menu_visible:
                return "show_policies"
            elif key_pressed == pyxel.KEY_F1:
                self.show_fps = not self.show_fps
            elif key_pressed == pyxel.KEY_F2:
                self.show_debug_info = not self.show_debug_info
        
        return None
    
    def toggle_main_menu(self):
        """Toggle main menu visibility"""
        self.main_menu_visible = not self.main_menu_visible
        if self.main_menu_visible:
            self.current_menu = self.menus["main"]
            self.menu_selection = 0
    
    def _execute_menu_action(self) -> Optional[str]:
        """Execute selected menu action"""
        if not self.current_menu or self.menu_selection >= len(self.current_menu):
            return None
        
        selected_item = self.current_menu[self.menu_selection]
        
        if selected_item.submenu:
            # Enter submenu
            self.current_menu = selected_item.submenu
            self.menu_selection = 0
        else:
            # Execute action
            self.main_menu_visible = False
            return selected_item.action
        
        return None
    
    def set_panel(self, panel: UIPanel):
        """Switch to different UI panel"""
        self.current_panel = panel
        self.transition_timer = 30  # 0.5 second transition
    
    def show_notification(self, message: str, duration: int = 180):
        """Show notification message"""
        self.notification_message = message
        self.notification_timer = duration
    
    def draw(self, game_data: Dict[str, Any]):
        """Draw complete UI"""
        import pyxel
        
        if self.current_panel == UIPanel.MAIN_GAME:
            self._draw_main_game_ui(game_data)
        elif self.current_panel == UIPanel.STATISTICS:
            self._draw_statistics_panel(game_data)
        elif self.current_panel == UIPanel.ECONOMY:
            self._draw_economy_panel(game_data)
        elif self.current_panel == UIPanel.TRAFFIC:
            self._draw_traffic_panel(game_data)
        elif self.current_panel == UIPanel.DISASTERS:
            self._draw_disasters_panel(game_data)
        elif self.current_panel == UIPanel.POLICIES:
            self._draw_policies_panel(game_data)
        
        # Draw overlays
        if self.main_menu_visible:
            self._draw_main_menu()
        
        if self.notification_timer > 0:
            self._draw_notification()
        
        if self.show_fps:
            self._draw_fps()
        
        if self.show_debug_info:
            self._draw_debug_info(game_data)
    
    def _draw_main_game_ui(self, game_data: Dict[str, Any]):
        """Draw main game UI"""
        import pyxel
        
        # Information panel at bottom
        panel_y = self.screen_height - self.info_panel_height
        pyxel.rect(0, panel_y, self.screen_width, self.info_panel_height, 0)
        pyxel.rectb(0, panel_y, self.screen_width, self.info_panel_height, 7)
        
        # Basic info
        info_text = f"資金: ¥{game_data.get('funds', 0):,} | 人口: {game_data.get('population', 0):,}"
        info_text += f" | 雇用: {game_data.get('employment', 0):,}"
        pyxel.text(5, panel_y + 5, info_text, 7)
        
        # RCI demand
        res_demand = game_data.get('res_demand', 0)
        com_demand = game_data.get('com_demand', 0)
        ind_demand = game_data.get('ind_demand', 0)
        
        demand_text = f"需要 - R:{res_demand:+d} C:{com_demand:+d} I:{ind_demand:+d}"
        pyxel.text(5, panel_y + 15, demand_text, 7)
        
        # Current tool info
        if 'current_tool' in game_data:
            tool_text = f"ツール: {game_data['current_tool']}"
            if 'tool_cost' in game_data:
                tool_text += f" (¥{game_data['tool_cost']})"
            pyxel.text(self.screen_width - 150, panel_y + 5, tool_text, 7)
        
        # View mode info
        if 'view_mode' in game_data:
            view_text = f"表示: {game_data['view_mode']}"
            pyxel.text(self.screen_width - 150, panel_y + 15, view_text, 7)
        
        # Mini-graphs
        self._draw_mini_graphs(game_data, self.screen_width - 400, panel_y + 5, 120, 20)
        
        # Controls hint
        controls_y = panel_y - 15
        pyxel.text(5, controls_y, "[ESC]メニュー [S]統計 [E]経済 [T]交通 [D]災害", 6)
    
    def _draw_statistics_panel(self, game_data: Dict[str, Any]):
        """Draw statistics panel with graphs"""
        import pyxel
        
        # Title bar
        pyxel.rect(0, 0, self.screen_width, 25, 1)
        pyxel.text(10, 8, "統計情報 - Statistics", 7)
        pyxel.text(self.screen_width - 100, 8, "[ESC] 戻る", 6)
        
        # Main content area
        content_y = 30
        content_height = self.screen_height - content_y - 5
        
        # Draw large graphs
        graph_width = (self.screen_width - 30) // 2
        graph_height = (content_height - 20) // 3
        
        graphs_to_show = ["population", "funds", "gdp", "traffic", "pollution", "land_value"]
        
        for i, graph_name in enumerate(graphs_to_show):
            col = i % 2
            row = i // 2
            
            x = 10 + col * (graph_width + 10)
            y = content_y + row * (graph_height + 10)
            
            self._draw_graph(self.graphs[graph_name], x, y, graph_width, graph_height)
    
    def _draw_economy_panel(self, game_data: Dict[str, Any]):
        """Draw economy management panel"""
        import pyxel
        
        # Title bar
        pyxel.rect(0, 0, self.screen_width, 25, 2)
        pyxel.text(10, 8, "経済管理 - Economy Management", 7)
        pyxel.text(self.screen_width - 100, 8, "[ESC] 戻る", 6)
        
        y = 35
        
        # Economic indicators
        pyxel.text(10, y, "経済指標:", 7)
        y += 15
        
        indicators = [
            ("GDP", f"¥{game_data.get('gdp', 0):,.0f}"),
            ("失業率", f"{game_data.get('unemployment', 0)*100:.1f}%"),
            ("インフレ率", f"{game_data.get('inflation', 0)*100:+.1f}%"),
            ("貿易収支", f"¥{game_data.get('trade_balance', 0):+,}"),
            ("生産性", f"{game_data.get('productivity', 1.0):.2f}x")
        ]
        
        for name, value in indicators:
            pyxel.text(15, y, f"{name}: {value}", 7)
            y += 12
        
        # Tax policy
        y += 10
        pyxel.text(10, y, "税率設定:", 7)
        y += 15
        
        tax_rates = [
            ("住宅", game_data.get('residential_tax_rate', 0.08)),
            ("商業", game_data.get('commercial_tax_rate', 0.12)),
            ("工業", game_data.get('industrial_tax_rate', 0.10))
        ]
        
        for name, rate in tax_rates:
            pyxel.text(15, y, f"{name}: {rate*100:.1f}%", 7)
            y += 12
        
        # Monthly budget
        y += 10
        pyxel.text(10, y, "月次予算:", 7)
        y += 15
        
        revenue = game_data.get('monthly_revenue', 0)
        expenses = game_data.get('monthly_expenses', 0)
        net = revenue - expenses
        
        pyxel.text(15, y, f"収入: ¥{revenue:,}", 11 if revenue > 0 else 7)
        y += 12
        pyxel.text(15, y, f"支出: ¥{expenses:,}", 8 if expenses > 0 else 7)
        y += 12
        pyxel.text(15, y, f"純収入: ¥{net:+,}", 11 if net > 0 else 8)
        
        # Resource summary (if economic system active)
        if 'resources' in game_data:
            y += 20
            pyxel.text(10, y, "資源状況:", 7)
            y += 15
            
            resources = game_data['resources']
            for resource_id, info in list(resources.items())[:8]:  # Show first 8 resources
                amount = info.get('amount', 0)
                production = info.get('production', 0)
                consumption = info.get('consumption', 0)
                net_rate = production - consumption
                
                color = 11 if net_rate > 0 else 8 if net_rate < 0 else 7
                pyxel.text(15, y, f"{info['name']}: {amount:.0f} ({net_rate:+.1f}/月)", color)
                y += 12
                
                if y > self.screen_height - 50:
                    break
    
    def _draw_traffic_panel(self, game_data: Dict[str, Any]):
        """Draw traffic management panel"""
        import pyxel
        
        # Title bar
        pyxel.rect(0, 0, self.screen_width, 25, 12)
        pyxel.text(10, 8, "交通管理 - Traffic Management", 7)
        pyxel.text(self.screen_width - 100, 8, "[ESC] 戻る", 6)
        
        y = 35
        
        # Traffic statistics
        traffic_data = game_data.get('traffic_system', {})
        
        stats = [
            ("運行バス数", traffic_data.get('total_buses', 0)),
            ("運行路線数", traffic_data.get('active_routes', 0)),
            ("乗客数", traffic_data.get('total_passengers', 0)),
            ("待機乗客", traffic_data.get('waiting_passengers', 0)),
            ("平均混雑度", f"{traffic_data.get('average_congestion', 0)*100:.1f}%"),
            ("渋滞箇所", traffic_data.get('bottlenecks', 0)),
            ("信号機数", traffic_data.get('traffic_lights', 0))
        ]
        
        for name, value in stats:
            pyxel.text(15, y, f"{name}: {value}", 7)
            y += 12
        
        # Traffic improvements suggestions
        if 'improvement_suggestions' in traffic_data:
            y += 10
            pyxel.text(10, y, "改善提案:", 7)
            y += 15
            
            for suggestion in traffic_data['improvement_suggestions'][:5]:
                pos = suggestion.get('position', (0, 0))
                cost = suggestion.get('cost', 0)
                reason = suggestion.get('reason', '')
                
                pyxel.text(15, y, f"• {suggestion['type']} ({pos[0]},{pos[1]}) - ¥{cost}", 7)
                y += 10
                if len(reason) < 50:
                    pyxel.text(20, y, reason, 6)
                    y += 10
                y += 5
        
        # Traffic graph
        if len(self.graphs["traffic"].values) > 1:
            graph_y = self.screen_height - 140
            self._draw_graph(self.graphs["traffic"], 10, graph_y, self.screen_width - 20, 100)
    
    def _draw_disasters_panel(self, game_data: Dict[str, Any]):
        """Draw disaster management panel"""
        import pyxel
        
        # Title bar
        pyxel.rect(0, 0, self.screen_width, 25, 8)
        pyxel.text(10, 8, "災害管理 - Disaster Management", 7)
        pyxel.text(self.screen_width - 100, 8, "[ESC] 戻る", 6)
        
        y = 35
        
        # Disaster status
        disaster_data = game_data.get('disaster_system', {})
        
        status_items = [
            ("発生中災害", disaster_data.get('active_disasters', 0)),
            ("総被害額", f"¥{disaster_data.get('total_damage_cost', 0):,}"),
            ("倒壊建物", disaster_data.get('buildings_destroyed', 0)),
            ("負傷者数", disaster_data.get('casualties', 0)),
            ("緊急施設", disaster_data.get('emergency_services', 0)),
            ("次回警戒まで", f"{disaster_data.get('disaster_cooldown', 0)//60}秒")
        ]
        
        for name, value in status_items:
            pyxel.text(15, y, f"{name}: {value}", 7)
            y += 12
        
        # Active disasters
        if 'active_disasters' in disaster_data and disaster_data['active_disasters']:
            y += 10
            pyxel.text(10, y, "発生中災害:", 8)
            y += 15
            
            for disaster in disaster_data['active_disasters'][:5]:
                disaster_type = disaster['type']
                severity = disaster['severity']
                pos = disaster['center']
                remaining = disaster['remaining_time']
                
                pyxel.text(15, y, f"• {disaster_type.upper()} ({severity}) - ({pos[0]},{pos[1]})", 8)
                y += 10
                pyxel.text(20, y, f"残り時間: {remaining}秒", 6)
                y += 15
        
        # Warning display
        if disaster_data.get('warning_active', False):
            warning_msg = disaster_data.get('warning_message', '')
            pyxel.rect(10, self.screen_height - 80, self.screen_width - 20, 30, 8)
            pyxel.rectb(10, self.screen_height - 80, self.screen_width - 20, 30, 7)
            pyxel.text(15, self.screen_height - 70, "⚠️ 災害警報", 7)
            pyxel.text(15, self.screen_height - 58, warning_msg[:50], 7)
    
    def _draw_policies_panel(self, game_data: Dict[str, Any]):
        """Draw policy management panel"""
        import pyxel
        
        # Title bar
        pyxel.rect(0, 0, self.screen_width, 25, 11)
        pyxel.text(10, 8, "政策管理 - Policy Management", 7)
        pyxel.text(self.screen_width - 100, 8, "[ESC] 戻る", 6)
        
        y = 35
        
        # Available policies
        policies = game_data.get('available_policies', [])
        
        pyxel.text(10, y, "利用可能な政策:", 7)
        y += 15
        
        for i, policy in enumerate(policies[:8]):
            affordable = policy.get('affordable', False)
            color = 7 if affordable else 6
            
            pyxel.text(15, y, f"{i+1}. {policy['name']}", color)
            y += 10
            pyxel.text(20, y, f"費用: ¥{policy['cost']:,} 期間: {policy['duration']}ヶ月", 6)
            y += 10
            pyxel.text(20, y, policy['description'][:40], 6)
            y += 15
        
        # Active policies
        active_policies = game_data.get('active_policies_count', 0)
        if active_policies > 0:
            y += 10
            pyxel.text(10, y, f"実施中政策: {active_policies}件", 11)
    
    def _draw_graph(self, graph_data: GraphData, x: int, y: int, width: int, height: int):
        """Draw a graph with the given data"""
        import pyxel
        
        if not graph_data.values:
            return
        
        # Background
        pyxel.rect(x, y, width, height, 0)
        pyxel.rectb(x, y, width, height, 7)
        
        # Title
        pyxel.text(x + 2, y + 2, graph_data.name, 7)
        
        # Graph area
        graph_x = x + 2
        graph_y = y + 12
        graph_width = width - 4
        graph_height = height - 16
        
        # Scale values
        max_val = graph_data.get_max_value()
        min_val = graph_data.get_min_value()
        
        if max_val == min_val:
            max_val = min_val + 1
        
        # Draw data points
        values = graph_data.values
        if len(values) > 1:
            for i in range(1, len(values)):
                # Calculate positions
                x1 = graph_x + int((i - 1) * graph_width / max(len(values) - 1, 1))
                x2 = graph_x + int(i * graph_width / max(len(values) - 1, 1))
                
                y1 = graph_y + graph_height - int((values[i-1] - min_val) / (max_val - min_val) * graph_height)
                y2 = graph_y + graph_height - int((values[i] - min_val) / (max_val - min_val) * graph_height)
                
                # Clamp y values
                y1 = max(graph_y, min(graph_y + graph_height, y1))
                y2 = max(graph_y, min(graph_y + graph_height, y2))
                
                pyxel.line(x1, y1, x2, y2, graph_data.color)
        
        # Show current value
        if values:
            current_val = values[-1]
            val_text = f"{current_val:.0f}" if current_val >= 10 else f"{current_val:.1f}"
            pyxel.text(x + width - 50, y + 2, val_text, graph_data.color)
    
    def _draw_mini_graphs(self, game_data: Dict[str, Any], x: int, y: int, width: int, height: int):
        """Draw mini graphs for main UI"""
        import pyxel
        
        # Population mini-graph
        pop_graph = self.graphs["population"]
        if len(pop_graph.values) > 1:
            self._draw_mini_line_graph(pop_graph.values, x, y, width//3, height, 11)
            pyxel.text(x + 2, y + height - 8, "人口", 6)
        
        # Funds mini-graph  
        funds_graph = self.graphs["funds"]
        if len(funds_graph.values) > 1:
            self._draw_mini_line_graph(funds_graph.values, x + width//3, y, width//3, height, 10)
            pyxel.text(x + width//3 + 2, y + height - 8, "資金", 6)
        
        # Traffic mini-graph
        traffic_graph = self.graphs["traffic"]
        if len(traffic_graph.values) > 1:
            self._draw_mini_line_graph(traffic_graph.values, x + 2*width//3, y, width//3, height, 8)
            pyxel.text(x + 2*width//3 + 2, y + height - 8, "交通", 6)
    
    def _draw_mini_line_graph(self, values: List[float], x: int, y: int, width: int, height: int, color: int):
        """Draw a mini line graph"""
        import pyxel
        
        if len(values) < 2:
            return
        
        # Calculate scale
        max_val = max(values)
        min_val = min(values)
        if max_val == min_val:
            max_val = min_val + 1
        
        # Draw lines
        for i in range(1, len(values)):
            x1 = x + int((i - 1) * width / max(len(values) - 1, 1))
            x2 = x + int(i * width / max(len(values) - 1, 1))
            
            y1 = y + height - int((values[i-1] - min_val) / (max_val - min_val) * height)
            y2 = y + height - int((values[i] - min_val) / (max_val - min_val) * height)
            
            pyxel.line(x1, y1, x2, y2, color)
    
    def _draw_main_menu(self):
        """Draw main menu"""
        import pyxel
        
        if not self.current_menu:
            return
        
        # Menu background
        menu_width = 200
        menu_height = len(self.current_menu) * 20 + 10
        menu_x = (self.screen_width - menu_width) // 2
        menu_y = (self.screen_height - menu_height) // 2
        
        pyxel.rect(menu_x, menu_y, menu_width, menu_height, 0)
        pyxel.rectb(menu_x, menu_y, menu_width, menu_height, 7)
        
        # Menu items
        for i, item in enumerate(self.current_menu):
            item_y = menu_y + 5 + i * 20
            
            # Highlight selected item
            if i == self.menu_selection:
                pyxel.rect(menu_x + 2, item_y - 2, menu_width - 4, 16, 1)
            
            # Draw item text
            color = 7 if item.enabled else 6
            pyxel.text(menu_x + 10, item_y, item.japanese_text, color)
            
            # Draw shortcut key
            if item.shortcut_key:
                key_text = chr(item.shortcut_key) if 32 <= item.shortcut_key <= 126 else f"#{item.shortcut_key}"
                pyxel.text(menu_x + menu_width - 30, item_y, f"[{key_text}]", 6)
            
            # Draw submenu indicator
            if item.submenu:
                pyxel.text(menu_x + menu_width - 15, item_y, ">", 7)
    
    def _draw_notification(self):
        """Draw notification message"""
        import pyxel
        
        # Notification background
        msg_width = len(self.notification_message) * 4 + 20
        msg_x = (self.screen_width - msg_width) // 2
        msg_y = 50
        
        # Fade effect
        alpha = min(1.0, self.notification_timer / 60.0)
        if alpha > 0.5:
            pyxel.rect(msg_x, msg_y, msg_width, 20, 1)
            pyxel.rectb(msg_x, msg_y, msg_width, 20, 7)
            pyxel.text(msg_x + 10, msg_y + 6, self.notification_message, 7)
    
    def _draw_fps(self):
        """Draw FPS counter"""
        import pyxel
        pyxel.text(self.screen_width - 40, 5, f"FPS:{pyxel.frame_count%60}", 7)
    
    def _draw_debug_info(self, game_data: Dict[str, Any]):
        """Draw debug information"""
        import pyxel
        
        debug_info = [
            f"Panel: {self.current_panel.value}",
            f"Menu: {self.main_menu_visible}",
            f"Transition: {self.transition_timer}",
            f"Population: {game_data.get('population', 0)}",
            f"Employment: {game_data.get('employment', 0)}",
            f"Funds: {game_data.get('funds', 0)}"
        ]
        
        y = 30
        for info in debug_info:
            pyxel.text(5, y, info, 8)
            y += 10