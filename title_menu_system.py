"""
Title Screen and Main Menu System for ConcLand
Handles game startup, menu navigation, and game state management
"""
import pyxel
import os
import json
import pickle
import math
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass
from enum import Enum

class GameState(Enum):
    TITLE = "title"
    MAIN_MENU = "main_menu"
    NEW_GAME = "new_game"
    LOAD_GAME = "load_game"
    OPTIONS = "options"
    CREDITS = "credits"
    IN_GAME = "in_game"
    PAUSED = "paused"
    QUIT_CONFIRM = "quit_confirm"

class MenuTransition(Enum):
    NONE = 0
    FADE_IN = 1
    FADE_OUT = 2
    SLIDE_LEFT = 3
    SLIDE_RIGHT = 4

@dataclass
class MenuItem:
    """Menu item definition"""
    id: str
    label: str
    japanese_label: str
    action: Optional[Callable] = None
    enabled: bool = True
    visible: bool = True
    shortcut: Optional[str] = None
    description: Optional[str] = None

@dataclass
class SaveGameInfo:
    """Save game information"""
    filename: str
    city_name: str
    population: int
    funds: int
    play_time: int
    save_date: str
    screenshot: Optional[Any] = None  # Small preview image

class UserSettings:
    """User preferences and settings"""
    def __init__(self):
        self.settings_file = "user_settings.json"
        self.defaults = {
            "auto_load_last_save": False,
            "skip_title_screen": False,
            "quick_start_mode": "continue",  # "continue", "new", "menu"
            "language": "japanese",  # "japanese", "english"
            "difficulty": "normal",
            "auto_save": True,
            "auto_save_interval": 300,  # 5 minutes
            "show_hints": True,
            "fullscreen": False,
            "music_volume": 70,
            "sfx_volume": 80,
            "last_save_file": None,
            "recent_saves": [],
            "preferred_map_size": 100,
            "dev_mode": False
        }
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict:
        """Load user settings from file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults to handle new settings
                    settings = self.defaults.copy()
                    settings.update(loaded)
                    return settings
            except:
                return self.defaults.copy()
        return self.defaults.copy()
    
    def save_settings(self):
        """Save user settings to file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save settings: {e}")
    
    def get(self, key: str, default=None):
        """Get setting value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value):
        """Set setting value"""
        self.settings[key] = value
        self.save_settings()

class TitleScreen:
    """Title screen with logo and press start"""
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.logo_animation_timer = 0
        self.press_start_blink = 0
        self.background_scroll = 0
        
    def update(self):
        """Update title screen animations"""
        self.logo_animation_timer += 1
        self.press_start_blink = (self.press_start_blink + 1) % 60
        self.background_scroll = (self.background_scroll + 1) % 320
        
    def draw(self):
        """Draw title screen"""
        # Animated background
        self._draw_animated_background()
        
        # Logo
        self._draw_logo()
        
        # Press Start message
        if self.press_start_blink < 40:
            text = "PRESS ENTER TO START" if pyxel.frame_count % 120 < 60 else "エンターキーでスタート"
            text_width = len(text) * 4
            x = (self.screen_width - text_width) // 2
            y = self.screen_height - 60
            
            # Shadow
            pyxel.text(x + 1, y + 1, text, 0)
            # Main text
            pyxel.text(x, y, text, 7)
        
        # Version info
        pyxel.text(5, self.screen_height - 10, "v1.0.0", 6)
        
    def _draw_animated_background(self):
        """Draw animated city silhouette background"""
        # Sky gradient
        for y in range(self.screen_height // 2):
            color = 1 if y < self.screen_height // 4 else 5
            pyxel.rect(0, y, self.screen_width, 1, color)
        
        # City silhouette
        building_heights = [30, 45, 35, 60, 40, 55, 38, 48, 42, 50]
        x_offset = -self.background_scroll
        
        for i in range(20):  # Draw multiple sets for scrolling
            for j, height in enumerate(building_heights):
                x = x_offset + i * 160 + j * 16
                y = self.screen_height - height - 80
                
                if -16 <= x <= self.screen_width:
                    # Building
                    pyxel.rect(x, y, 14, height, 0)
                    
                    # Windows
                    if pyxel.frame_count % 30 < 15 or (i + j) % 3 == 0:
                        for wy in range(2, height - 2, 6):
                            for wx in range(2, 12, 4):
                                if (wx + wy + i) % 5 != 0:
                                    pyxel.rect(x + wx, y + wy, 2, 2, 10)
        
        # Ground
        pyxel.rect(0, self.screen_height - 80, self.screen_width, 80, 3)
    
    def _draw_logo(self):
        """Draw game logo"""
        # Main title
        title = "CONCLAND"
        title_scale = 3
        char_width = 8
        total_width = len(title) * char_width * title_scale
        x = (self.screen_width - total_width) // 2
        y = 60
        
        # Animated color cycle
        colors = [7, 12, 6, 11, 10]
        color_index = (self.logo_animation_timer // 10) % len(colors)
        
        # Draw each character with scaling effect
        for i, char in enumerate(title):
            char_x = x + i * char_width * title_scale
            char_y = y + int(math.sin((self.logo_animation_timer + i * 10) * 0.05) * 3)
            
            # Shadow
            self._draw_scaled_text(char_x + 2, char_y + 2, char, 0, title_scale)
            # Main character
            color = colors[(color_index + i) % len(colors)]
            self._draw_scaled_text(char_x, char_y, char, color, title_scale)
        
        # Subtitle
        subtitle = "都市建設シミュレーション"
        sub_width = len(subtitle) * 4
        sub_x = (self.screen_width - sub_width) // 2
        sub_y = y + 40
        pyxel.text(sub_x, sub_y, subtitle, 7)
    
    def _draw_scaled_text(self, x: int, y: int, text: str, color: int, scale: int):
        """Draw scaled text character"""
        for dy in range(8):
            for dx in range(8):
                if self._get_char_pixel(text, dx, dy):
                    for sy in range(scale):
                        for sx in range(scale):
                            pyxel.pset(x + dx * scale + sx, y + dy * scale + sy, color)
    
    def _get_char_pixel(self, char: str, x: int, y: int) -> bool:
        """Get pixel value for character (simplified)"""
        # This is a simplified version - in real implementation,
        # you'd use proper font data
        char_data = {
            'C': [0b01111100, 0b11000110, 0b11000000, 0b11000000, 
                  0b11000000, 0b11000110, 0b01111100, 0b00000000],
            'O': [0b01111100, 0b11000110, 0b11000110, 0b11000110,
                  0b11000110, 0b11000110, 0b01111100, 0b00000000],
            'N': [0b11000110, 0b11100110, 0b11110110, 0b11011110,
                  0b11001110, 0b11000110, 0b11000110, 0b00000000],
            'L': [0b11000000, 0b11000000, 0b11000000, 0b11000000,
                  0b11000000, 0b11000000, 0b11111110, 0b00000000],
            'A': [0b00111000, 0b01101100, 0b11000110, 0b11111110,
                  0b11000110, 0b11000110, 0b11000110, 0b00000000],
            'D': [0b11111000, 0b11001100, 0b11000110, 0b11000110,
                  0b11000110, 0b11001100, 0b11111000, 0b00000000]
        }
        
        if char in char_data and y < 8:
            row = char_data[char][y]
            return bool(row & (1 << (7 - x)))
        return False

class MainMenu:
    """Main menu system"""
    def __init__(self, screen_width: int, screen_height: int, user_settings: UserSettings):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.user_settings = user_settings
        self.current_selection = 0
        self.transition_state = MenuTransition.NONE
        self.transition_timer = 0
        
        # Menu items
        self.menu_items = [
            MenuItem("new_game", "New Game", "新しいゲーム", None, True, True, "N"),
            MenuItem("continue", "Continue", "続きから", None, True, True, "C"),
            MenuItem("load_game", "Load Game", "ロード", None, True, True, "L"),
            MenuItem("options", "Options", "設定", None, True, True, "O"),
            MenuItem("achievements", "Achievements", "実績", None, True, True, "A"),
            MenuItem("credits", "Credits", "クレジット", None, True, True, "R"),
            MenuItem("quit", "Quit", "終了", None, True, True, "Q")
        ]
        
        # Check if continue is available
        if not self.user_settings.get("last_save_file"):
            self.menu_items[1].enabled = False
        
    def update(self):
        """Update menu state"""
        if self.transition_state != MenuTransition.NONE:
            self.transition_timer += 5
            if self.transition_timer >= 30:
                self.transition_state = MenuTransition.NONE
                self.transition_timer = 0
    
    def handle_input(self) -> Optional[str]:
        """Handle menu input and return action"""
        if pyxel.btnp(pyxel.KEY_UP):
            self.current_selection = self._get_prev_enabled_item()
            return "cursor_move"
            
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.current_selection = self._get_next_enabled_item()
            return "cursor_move"
            
        elif pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
            item = self.menu_items[self.current_selection]
            if item.enabled:
                return item.id
        
        # Shortcut keys
        for i, item in enumerate(self.menu_items):
            if item.shortcut and item.enabled:
                key = ord(item.shortcut)
                if pyxel.btnp(key):
                    self.current_selection = i
                    return item.id
        
        return None
    
    def _get_next_enabled_item(self) -> int:
        """Get next enabled menu item index"""
        current = self.current_selection
        for _ in range(len(self.menu_items)):
            current = (current + 1) % len(self.menu_items)
            if self.menu_items[current].enabled and self.menu_items[current].visible:
                return current
        return self.current_selection
    
    def _get_prev_enabled_item(self) -> int:
        """Get previous enabled menu item index"""
        current = self.current_selection
        for _ in range(len(self.menu_items)):
            current = (current - 1) % len(self.menu_items)
            if self.menu_items[current].enabled and self.menu_items[current].visible:
                return current
        return self.current_selection
    
    def draw(self):
        """Draw main menu"""
        # Background
        self._draw_menu_background()
        
        # Menu panel
        panel_width = 200
        panel_height = len([i for i in self.menu_items if i.visible]) * 25 + 40
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        # Apply transition effect
        if self.transition_state == MenuTransition.SLIDE_LEFT:
            panel_x -= self.transition_timer * 10
        elif self.transition_state == MenuTransition.SLIDE_RIGHT:
            panel_x += self.transition_timer * 10
        
        # Draw panel with 9-slice border
        self._draw_panel(panel_x, panel_y, panel_width, panel_height)
        
        # Draw menu items
        y_offset = 20
        for i, item in enumerate(self.menu_items):
            if not item.visible:
                continue
            
            item_y = panel_y + y_offset
            
            # Selection highlight
            if i == self.current_selection:
                pyxel.rect(panel_x + 10, item_y - 2, panel_width - 20, 18, 1)
            
            # Item text
            if self.user_settings.get("language") == "japanese":
                text = item.japanese_label
            else:
                text = item.label
            
            # Color based on state
            if not item.enabled:
                color = 5  # Disabled
            elif i == self.current_selection:
                color = 7  # Selected
            else:
                color = 6  # Normal
            
            # Draw text
            text_x = panel_x + 20
            pyxel.text(text_x, item_y, text, color)
            
            # Shortcut hint
            if item.shortcut and item.enabled:
                shortcut_text = f"[{item.shortcut}]"
                shortcut_x = panel_x + panel_width - 30
                pyxel.text(shortcut_x, item_y, shortcut_text, 5)
            
            y_offset += 25
    
    def _draw_menu_background(self):
        """Draw menu background"""
        # Gradient background
        for y in range(self.screen_height):
            color = 1 if y < self.screen_height // 3 else 5 if y < 2 * self.screen_height // 3 else 0
            pyxel.rect(0, y, self.screen_width, 1, color)
        
        # Decorative elements
        if pyxel.frame_count % 120 < 60:
            for i in range(5):
                x = (i * 100 + pyxel.frame_count) % (self.screen_width + 50) - 25
                y = 50 + i * 30
                pyxel.circ(x, y, 3, 6)
    
    def _draw_panel(self, x: int, y: int, width: int, height: int):
        """Draw UI panel with border"""
        # Main panel
        pyxel.rect(x, y, width, height, 0)
        
        # Border
        pyxel.rectb(x, y, width, height, 7)
        pyxel.rectb(x + 1, y + 1, width - 2, height - 2, 6)

class GameLauncher:
    """Main game launcher and state manager"""
    def __init__(self, screen_width=320, screen_height=288):
        # Initialize Pyxel
        self.screen_width = screen_width
        self.screen_height = screen_height

        pyxel.init(self.screen_width, self.screen_height, title="ConcLand", fps=60)
        
        # Load user settings
        self.user_settings = UserSettings()
        
        # Initialize subsystems
        self.title_screen = TitleScreen(self.screen_width, self.screen_height)
        self.main_menu = MainMenu(self.screen_width, self.screen_height, self.user_settings)
        
        # Game state
        self.current_state = GameState.TITLE
        self.next_state = None
        self.game_instance = None
        
        # Quick start logic
        self._handle_quick_start()
        
        # Start Pyxel
        pyxel.run(self.update, self.draw)
    
    def _handle_quick_start(self):
        """Handle quick start based on user settings"""
        if self.user_settings.get("skip_title_screen"):
            if self.user_settings.get("auto_load_last_save"):
                last_save = self.user_settings.get("last_save_file")
                if last_save and os.path.exists(last_save):
                    self._load_game(last_save)
                    self.current_state = GameState.IN_GAME
                    return
            
            quick_start = self.user_settings.get("quick_start_mode")
            if quick_start == "continue":
                last_save = self.user_settings.get("last_save_file")
                if last_save and os.path.exists(last_save):
                    self._load_game(last_save)
                    self.current_state = GameState.IN_GAME
                else:
                    self.current_state = GameState.MAIN_MENU
            elif quick_start == "new":
                self._start_new_game()
                self.current_state = GameState.IN_GAME
            else:
                self.current_state = GameState.MAIN_MENU
        else:
            self.current_state = GameState.TITLE
    
    def update(self):
        """Update game state"""
        # Handle state transitions
        if self.next_state:
            self.current_state = self.next_state
            self.next_state = None
        
        # Update based on current state
        if self.current_state == GameState.TITLE:
            self._update_title()
        elif self.current_state == GameState.MAIN_MENU:
            self._update_main_menu()
        elif self.current_state == GameState.IN_GAME:
            self._update_game()
        elif self.current_state == GameState.OPTIONS:
            self._update_options()
        elif self.current_state == GameState.QUIT_CONFIRM:
            self._update_quit_confirm()
    
    def draw(self):
        """Draw current state"""
        pyxel.cls(0)
        
        if self.current_state == GameState.TITLE:
            self.title_screen.draw()
        elif self.current_state == GameState.MAIN_MENU:
            self.main_menu.draw()
        elif self.current_state == GameState.IN_GAME:
            if self.game_instance:
                self.game_instance.draw()
        elif self.current_state == GameState.OPTIONS:
            self._draw_options()
        elif self.current_state == GameState.QUIT_CONFIRM:
            self._draw_quit_confirm()
    
    def _update_title(self):
        """Update title screen"""
        self.title_screen.update()
        
        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
            self.next_state = GameState.MAIN_MENU
        # ESC key on title screen does nothing (disabled quit)
        # elif pyxel.btnp(pyxel.KEY_ESCAPE):
        #     pyxel.quit()
    
    def _update_main_menu(self):
        """Update main menu"""
        self.main_menu.update()
        
        action = self.main_menu.handle_input()
        if action:
            if action == "new_game":
                self._start_new_game()
                self.next_state = GameState.IN_GAME
            elif action == "continue":
                last_save = self.user_settings.get("last_save_file")
                if last_save and os.path.exists(last_save):
                    self._load_game(last_save)
                    self.next_state = GameState.IN_GAME
            elif action == "load_game":
                self.next_state = GameState.LOAD_GAME
            elif action == "options":
                self.next_state = GameState.OPTIONS
            elif action == "quit":
                self.next_state = GameState.QUIT_CONFIRM
        
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self.next_state = GameState.TITLE
    
    def _update_game(self):
        """Update game"""
        if self.game_instance:
            self.game_instance.update()
            
            # Check for pause/menu
            if pyxel.btnp(pyxel.KEY_ESCAPE):
                self.next_state = GameState.PAUSED
    
    def _update_options(self):
        """Update options menu"""
        # Options menu implementation
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self.next_state = GameState.MAIN_MENU
    
    def _update_quit_confirm(self):
        """Update quit confirmation"""
        if pyxel.btnp(pyxel.KEY_Y):
            pyxel.quit()
        elif pyxel.btnp(pyxel.KEY_N) or pyxel.btnp(pyxel.KEY_ESCAPE):
            self.next_state = GameState.MAIN_MENU
    
    def _draw_options(self):
        """Draw options menu"""
        pyxel.text(100, 100, "OPTIONS MENU", 7)
        pyxel.text(100, 120, "Press ESC to return", 6)
    
    def _draw_quit_confirm(self):
        """Draw quit confirmation"""
        pyxel.rect(200, 200, 400, 200, 0)
        pyxel.rectb(200, 200, 400, 200, 7)
        pyxel.text(350, 250, "本当に終了しますか？", 7)
        pyxel.text(340, 280, "Really quit?", 7)
        pyxel.text(320, 320, "[Y] はい/Yes  [N] いいえ/No", 6)
    
    def _start_new_game(self):
        """Start a new game"""
        # Import and initialize the main game
        try:
            from concland_mini import ConcLandMini
            self.game_instance = ConcLandMini(skip_pyxel_init=True)
            print("New game started")
        except ImportError:
            print("Game module not found, using stub")
            self.game_instance = None

    def _load_game(self, filename: str):
        """Load a saved game"""
        try:
            from concland_mini import ConcLandMini
            self.game_instance = ConcLandMini(skip_pyxel_init=True)
            self.game_instance.load_city(filename)
            print(f"Game loaded from {filename}")

            # Update last save in settings
            self.user_settings.set("last_save_file", filename)
        except Exception as e:
            print(f"Failed to load game: {e}")
            self.game_instance = None

def main():
    """Entry point"""
    GameLauncher()

if __name__ == "__main__":
    main()