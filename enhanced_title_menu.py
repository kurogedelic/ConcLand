"""
Enhanced Title Screen and Menu System for ConcLand
Improved visual effects, animations, and additional UI screens
"""
import pyxel
import os
import json
import math
import random
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass
from enum import Enum

class GameState(Enum):
    TITLE = "title"
    MAIN_MENU = "main_menu"
    NEW_GAME = "new_game"
    LOAD_GAME = "load_game"
    OPTIONS = "options"
    ACHIEVEMENTS = "achievements"
    CREDITS = "credits"
    IN_GAME = "in_game"
    PAUSED = "paused"
    QUIT_CONFIRM = "quit_confirm"
    DIFFICULTY_SELECT = "difficulty_select"

class MenuTransition(Enum):
    NONE = 0
    FADE_IN = 1
    FADE_OUT = 2
    SLIDE_LEFT = 3
    SLIDE_RIGHT = 4
    SCALE_UP = 5
    SCALE_DOWN = 6

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
    icon: Optional[str] = None

@dataclass
class SaveGameInfo:
    """Save game information"""
    filename: str
    city_name: str
    population: int
    funds: int
    play_time: int
    save_date: str
    screenshot: Optional[Any] = None
    difficulty: str = "normal"

class Particle:
    """Particle for visual effects"""
    def __init__(self, x: float, y: float, vx: float, vy: float, life: int, color: int):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = random.uniform(1, 3)

    def update(self):
        """Update particle position and life"""
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self):
        """Draw particle"""
        if self.life > 0:
            alpha = self.life / self.max_life
            size = int(self.size * alpha)
            if size > 0:
                pyxel.circ(int(self.x), int(self.y), size, self.color)

class EnhancedTitleScreen:
    """Enhanced title screen with particle effects and improved animations"""
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.logo_animation_timer = 0
        self.press_start_blink = 0
        self.background_scroll = 0

        # Particles
        self.particles = []
        self.stars = []
        self.clouds = []

        # Initialize effects
        self._init_stars()
        self._init_clouds()

        # Audio hooks (to be implemented)
        self.bgm_playing = False
        self.sfx_hooks = {}

    def _init_stars(self):
        """Initialize background stars"""
        for _ in range(50):
            self.stars.append({
                'x': random.randint(0, self.screen_width),
                'y': random.randint(0, self.screen_height // 2),
                'size': random.randint(1, 2),
                'twinkle_speed': random.uniform(0.05, 0.15),
                'twinkle_offset': random.uniform(0, math.pi * 2)
            })

    def _init_clouds(self):
        """Initialize floating clouds"""
        for _ in range(5):
            self.clouds.append({
                'x': random.randint(-50, self.screen_width + 50),
                'y': random.randint(30, 80),
                'width': random.randint(40, 80),
                'height': random.randint(15, 30),
                'speed': random.uniform(0.2, 0.5)
            })

    def update(self):
        """Update title screen animations"""
        self.logo_animation_timer += 1
        self.press_start_blink = (self.press_start_blink + 1) % 60
        self.background_scroll = (self.background_scroll + 0.5) % 320

        # Update particles
        self._update_particles()
        self._update_clouds()

        # Spawn new particles occasionally
        if random.random() < 0.1:
            self._spawn_particle()

    def _update_particles(self):
        """Update all particles"""
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update()

    def _update_clouds(self):
        """Update cloud positions"""
        for cloud in self.clouds:
            cloud['x'] += cloud['speed']
            if cloud['x'] > self.screen_width + 50:
                cloud['x'] = -cloud['width']

    def _spawn_particle(self):
        """Spawn a new particle"""
        x = random.randint(0, self.screen_width)
        y = random.randint(self.screen_height - 100, self.screen_height - 50)
        vx = random.uniform(-0.5, 0.5)
        vy = random.uniform(-1, -0.3)
        life = random.randint(30, 60)
        color = random.choice([7, 6, 12])
        self.particles.append(Particle(x, y, vx, vy, life, color))

    def draw(self):
        """Draw enhanced title screen"""
        # Animated gradient sky
        self._draw_sky_gradient()

        # Stars
        self._draw_stars()

        # Clouds
        self._draw_clouds()

        # City silhouette
        self._draw_city_silhouette()

        # Particles
        for p in self.particles:
            p.draw()

        # Logo with enhanced animation
        self._draw_enhanced_logo()

        # Press Start message
        self._draw_press_start()

        # Version and copyright
        self._draw_footer_info()

    def _draw_sky_gradient(self):
        """Draw animated gradient sky"""
        for y in range(self.screen_height // 2 + 50):
            # Time-based color shift
            t = self.logo_animation_timer * 0.01
            r = int(30 + 20 * math.sin(y * 0.02 + t))
            g = int(60 + 30 * math.sin(y * 0.03 + t))
            b = int(100 + 40 * math.sin(y * 0.01 + t))

            # Map to Pyxel colors (simplified)
            if y < self.screen_height // 4:
                color = 12  # Dark blue
            elif y < self.screen_height // 3:
                color = 7   # Light blue
            else:
                color = 6   # Light orange

            pyxel.rect(0, y, self.screen_width, 1, color)

    def _draw_stars(self):
        """Draw twinkling stars"""
        for star in self.stars:
            twinkle = math.sin(self.logo_animation_timer * star['twinkle_speed'] + star['twinkle_offset'])
            if twinkle > 0.3:
                color = 7 if twinkle > 0.7 else 6
                pyxel.circ(star['x'], star['y'], star['size'], color)

    def _draw_clouds(self):
        """Draw floating clouds"""
        for cloud in self.clouds:
            # Simple cloud shape (multiple circles)
            pyxel.circ(cloud['x'], cloud['y'], cloud['height'] // 2, 7)
            pyxel.circ(cloud['x'] + cloud['width'] // 3, cloud['y'] - 5, cloud['height'] // 2, 7)
            pyxel.circ(cloud['x'] + 2 * cloud['width'] // 3, cloud['y'], cloud['height'] // 2, 7)

    def _draw_city_silhouette(self):
        """Draw animated city silhouette"""
        building_heights = [30, 45, 35, 60, 40, 55, 38, 48, 42, 50, 44, 52]
        x_offset = -self.background_scroll

        for i in range(25):  # Draw multiple sets for scrolling
            for j, height in enumerate(building_heights):
                x = x_offset + i * 140 + j * 12
                y = self.screen_height - height - 70

                if -20 <= x <= self.screen_width + 20:
                    # Building silhouette
                    pyxel.rect(x, y, 10, height, 0)

                    # Animated windows
                    if (pyxel.frame_count + i * 10 + j * 5) % 60 < 30:
                        for wy in range(5, height - 5, 8):
                            for wx in range(2, 8, 3):
                                if (wx + wy + i + j) % 3 == 0:
                                    # Window light color varies
                                    wcolor = 10 if (wx + wy) % 5 == 0 else 7
                                    pyxel.rect(x + wx, y + wy, 2, 2, wcolor)

        # Ground
        pyxel.rect(0, self.screen_height - 70, self.screen_width, 70, 3)

    def _draw_enhanced_logo(self):
        """Draw enhanced animated logo"""
        title = "CONCLAND"
        title_scale = 4
        char_width = 8
        total_width = len(title) * char_width * title_scale
        x = (self.screen_width - total_width) // 2
        y = 50

        # Enhanced color cycle with glow effect
        colors = [7, 12, 6, 14, 10, 9, 11]
        color_index = (self.logo_animation_timer // 8) % len(colors)

        # Glow effect
        glow_offset = int(math.sin(self.logo_animation_timer * 0.1) * 2)
        for i, char in enumerate(title):
            char_x = x + i * char_width * title_scale
            char_y = y + int(math.sin((self.logo_animation_timer + i * 12) * 0.03) * 4)

            # Glow layers
            for glow in range(3, 0, -1):
                glow_color = colors[(color_index + i + glow) % len(colors)]
                self._draw_scaled_text(
                    char_x + glow_offset - glow,
                    char_y + glow_offset - glow,
                    char,
                    glow_color,
                    title_scale
                )

            # Main character
            color = colors[(color_index + i) % len(colors)]
            self._draw_scaled_text(char_x, char_y, char, color, title_scale)

        # Subtitle with animation
        subtitle = "都市建設シミュレーション"
        sub_width = len(subtitle) * 4
        sub_x = (self.screen_width - sub_width) // 2
        sub_y = y + 50

        # Animated subtitle appearance
        alpha = min(1.0, self.logo_animation_timer / 60.0)
        if alpha > 0:
            pyxel.text(sub_x, sub_y, subtitle, 7)

        # Decorative line
        line_width = int(200 * alpha)
        line_x = (self.screen_width - line_width) // 2
        pyxel.rect(line_x, sub_y - 8, line_width, 1, 6)

    def _draw_press_start(self):
        """Draw animated press start message"""
        if self.press_start_blink < 45:
            # Bilingual text
            text_en = "PRESS ENTER TO START"
            text_jp = "エンターキーでスタート"

            # Alternate languages
            show_japanese = (self.logo_animation_timer // 120) % 2 == 0
            text = text_jp if show_japanese else text_en

            text_width = len(text) * 4
            x = (self.screen_width - text_width) // 2
            y = self.screen_height - 80

            # Shadow
            pyxel.text(x + 1, y + 1, text, 0)
            # Main text with animated color
            color = 7 if self.press_start_blink < 30 else 6
            pyxel.text(x, y, text, color)

    def _draw_footer_info(self):
        """Draw version and copyright information"""
        # Version
        version = "v1.0.0 Enhanced"
        pyxel.text(5, self.screen_height - 15, version, 6)

        # Copyright
        copyright = "© 2025 ConcLand Team"
        pyxel.text(self.screen_width - len(copyright) * 4 - 5, self.screen_height - 15, copyright, 6)

    def _draw_scaled_text(self, x: int, y: int, text: str, color: int, scale: int):
        """Draw scaled text character"""
        for dy in range(8):
            for dx in range(8):
                if self._get_char_pixel(text, dx, dy):
                    for sy in range(scale):
                        for sx in range(scale):
                            pyxel.pset(x + dx * scale + sx, y + dy * scale + sy, color)

    def _get_char_pixel(self, char: str, x: int, y: int) -> bool:
        """Get pixel value for character"""
        # Extended font data for better title rendering
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

class OptionsMenu:
    """Options menu for game settings"""
    def __init__(self, screen_width: int, screen_height: int, settings: Dict):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.settings = settings
        self.current_category = 0
        self.current_item = 0

        self.categories = [
            {"id": "display", "name": "Display", "jp": "表示"},
            {"id": "audio", "name": "Audio", "jp": "オーディオ"},
            {"id": "gameplay", "name": "Gameplay", "jp": "ゲームプレイ"}
        ]

        self.options = {
            "display": [
                {"key": "language", "name": "Language", "jp": "言語", "type": "select",
                 "options": ["japanese", "english"], "values": ["日本語", "English"]},
                {"key": "fullscreen", "name": "Fullscreen", "jp": "フルスクリーン", "type": "bool"},
                {"key": "show_hints", "name": "Show Hints", "jp": "ヒント表示", "type": "bool"}
            ],
            "audio": [
                {"key": "music_volume", "name": "Music Volume", "jp": "音楽音量", "type": "range", "min": 0, "max": 100},
                {"key": "sfx_volume", "name": "SFX Volume", "jp": "効果音音量", "type": "range", "min": 0, "max": 100}
            ],
            "gameplay": [
                {"key": "difficulty", "name": "Difficulty", "jp": "難易度", "type": "select",
                 "options": ["easy", "normal", "hard"], "values": ["易しい", "普通", "難しい"]},
                {"key": "auto_save", "name": "Auto Save", "jp": "オートセーブ", "type": "bool"}
            ]
        }

    def update(self):
        """Update options menu"""
        # Implementation for navigation and value changes
        pass

    def draw(self):
        """Draw options menu"""
        # Semi-transparent background
        for i in range(self.screen_height):
            alpha = 128 if i < self.screen_height // 2 else 64
            pyxel.rect(0, i, self.screen_width, 1, 0)

        # Title
        title = "OPTIONS / 設定"
        title_x = (self.screen_width - len(title) * 8) // 2
        pyxel.text(title_x, 20, title, 7)

        # Categories
        cat_y = 50
        for i, cat in enumerate(self.categories):
            color = 7 if i == self.current_category else 6
            cat_text = cat["jp"]
            pyxel.text(50, cat_y + i * 20, cat_text, color)

        # Options
        current_cat = self.categories[self.current_category]["id"]
        opts = self.options[current_cat]

        opt_y = 50
        for i, opt in enumerate(opts):
            opt_text = opt["jp"]
            pyxel.text(150, opt_y + i * 25, opt_text, 7)

            # Current value
            value = self.settings.get(opt["key"], "")
            value_text = str(value)
            pyxel.text(300, opt_y + i * 25, value_text, 6)

class CreditsScreen:
    """Credits screen with scrolling text"""
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scroll_y = screen_height
        self.credits_content = self._generate_credits()

    def _generate_credits(self) -> List[Dict]:
        """Generate credits content"""
        return [
            {"type": "title", "text": "ConcLand", "size": 4},
            {"type": "subtitle", "text": "都市建設シミュレーションゲーム", "size": 2},
            {"type": "spacer", "amount": 3},
            {"type": "section", "text": "Development Team", "size": 2},
            {"type": "name", "text": "Lead Developer", "size": 1},
            {"type": "name", "text": "Game Design", "size": 1},
            {"type": "name", "text": "Programming", "size": 1},
            {"type": "spacer", "amount": 2},
            {"type": "section", "text": "Special Thanks", "size": 2},
            {"type": "name", "text": "Pyxel Development Team", "size": 1},
            {"type": "name", "text": "Original SimCity by Maxis", "size": 1},
            {"type": "name", "text": "Claude AI Assistant", "size": 1},
            {"type": "spacer", "amount": 3},
            {"type": "title", "text": "Thank You for Playing!", "size": 3},
        ]

    def update(self):
        """Update scroll position"""
        self.scroll_y -= 0.5
        if self.scroll_y < -self._get_total_height():
            self.scroll_y = self.screen_height

    def _get_total_height(self) -> int:
        """Calculate total credits height"""
        total = 0
        for item in self.credits_content:
            if item["type"] == "spacer":
                total += item["amount"] * 20
            else:
                total += item["size"] * 15
        return total

    def draw(self):
        """Draw scrolling credits"""
        # Semi-transparent background
        for y in range(self.screen_height):
            alpha = 180
            pyxel.rect(0, y, self.screen_width, 1, 0)

        # Draw credits
        y = self.scroll_y
        for item in self.credits_content:
            if item["type"] == "spacer":
                y += item["amount"] * 20
            else:
                text = item["text"]
                text_width = len(text) * 4 * item["size"]
                x = (self.screen_width - text_width) // 2

                # Color based on type
                if item["type"] == "title":
                    color = 7
                elif item["type"] == "section":
                    color = 6
                else:
                    color = 7

                # Draw scaled text
                for i, char in enumerate(text):
                    char_x = x + i * 4 * item["size"]
                    for dy in range(8):
                        for dx in range(8):
                            pyxel.pset(char_x + dx * item["size"], y + dy * item["size"], color)

                y += item["size"] * 15

class DifficultySelectScreen:
    """Difficulty selection screen"""
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.difficulties = [
            {"id": "easy", "name": "Easy", "jp": "易しい", "desc": "初心者向け"},
            {"id": "normal", "name": "Normal", "jp": "普通", "desc": "標準"},
            {"id": "hard", "name": "Hard", "jp": "難しい", "desc": "上級者向け"}
        ]
        self.current_selection = 1  # Default to normal

    def update(self):
        """Handle difficulty selection input"""
        if pyxel.btnp(pyxel.KEY_LEFT):
            self.current_selection = max(0, self.current_selection - 1)
        elif pyxel.btnp(pyxel.KEY_RIGHT):
            self.current_selection = min(len(self.difficulties) - 1, self.current_selection + 1)

    def draw(self):
        """Draw difficulty selection"""
        # Background
        for y in range(self.screen_height):
            color = 1 if y < self.screen_height // 2 else 5
            pyxel.rect(0, y, self.screen_width, 1, color)

        # Title
        title = "SELECT DIFFICULTY / 難易度を選択"
        title_x = (self.screen_width - len(title) * 4) // 2
        pyxel.text(title_x, 40, title, 7)

        # Difficulty cards
        card_width = 100
        card_height = 120
        spacing = 20
        total_width = card_width * len(self.difficulties) + spacing * (len(self.difficulties) - 1)
        start_x = (self.screen_width - total_width) // 2
        card_y = 80

        for i, diff in enumerate(self.difficulties):
            card_x = start_x + i * (card_width + spacing)

            # Card background
            bg_color = 6 if i == self.current_selection else 0
            pyxel.rect(card_x, card_y, card_width, card_height, bg_color)
            pyxel.rectb(card_x, card_y, card_width, card_height, 7)

            # Difficulty name
            name = diff["jp"]
            name_x = card_x + (card_width - len(name) * 4) // 2
            pyxel.text(name_x, card_y + 20, name, 7 if i == self.current_selection else 6)

            # Description
            desc = diff["desc"]
            desc_x = card_x + (card_width - len(desc) * 4) // 2
            pyxel.text(desc_x, card_y + 50, desc, 7 if i == self.current_selection else 5)

            # Selection indicator
            if i == self.current_selection:
                pyxel.text(card_x + card_width // 2 - 8, card_y + card_height - 30, "→", 7)
                pyxel.text(card_x + card_width // 2 + 4, card_y + card_height - 30, "←", 7)

class EnhancedGameLauncher:
    """Enhanced game launcher with improved UI"""
    def __init__(self):
        self.screen_width = 320
        self.screen_height = 288
        self.current_state = GameState.TITLE
        self.previous_state = None

        # Initialize screens
        self.title_screen = EnhancedTitleScreen(self.screen_width, self.screen_height)

        # User settings
        self.user_settings = self._load_user_settings()

        # Menu (will be integrated with title_menu_system.py)
        # self.main_menu = MainMenu(...)
        # self.options_menu = OptionsMenu(...)
        # self.credits_screen = CreditsScreen(...)
        # self.difficulty_select = DifficultySelectScreen(...)

        # Audio hooks (placeholder)
        self.audio_system = None

    def _load_user_settings(self) -> Dict:
        """Load user settings"""
        settings_file = "user_settings.json"
        defaults = {
            "language": "japanese",
            "difficulty": "normal",
            "music_volume": 70,
            "sfx_volume": 80,
            "show_hints": True,
        }

        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    defaults.update(loaded)
            except:
                pass

        return defaults

    def update(self):
        """Update current state"""
        if self.current_state == GameState.TITLE:
            self.title_screen.update()

            # Check for start input
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
                self.current_state = GameState.MAIN_MENU

        elif self.current_state == GameState.MAIN_MENU:
            # Main menu update logic
            pass

        elif self.current_state == GameState.OPTIONS:
            # Options update logic
            pass

        elif self.current_state == GameState.CREDITS:
            # Credits update logic
            pass

        elif self.current_state == GameState.DIFFICULTY_SELECT:
            # Difficulty select update logic
            pass

    def draw(self):
        """Draw current state"""
        if self.current_state == GameState.TITLE:
            self.title_screen.draw()

        elif self.current_state == GameState.MAIN_MENU:
            # Main menu draw logic
            pass

        elif self.current_state == GameState.OPTIONS:
            # Options draw logic
            pass

        elif self.current_state == GameState.CREDITS:
            # Credits draw logic
            pass

        elif self.current_state == GameState.DIFFICULTY_SELECT:
            # Difficulty select draw logic
            pass

# Standalone test
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Initialize Pyxel
    pyxel.init(320, 288, title="ConcLand - Enhanced Title Screen")

    # Create launcher
    launcher = EnhancedGameLauncher()

    # Main loop
    def update():
        launcher.update()

        # Quit with Q
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

    def draw():
        pyxel.cls(0)
        launcher.draw()

    pyxel.run(update, draw)
