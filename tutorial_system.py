"""
Interactive Tutorial System for ConcLand
Guides new players through game mechanics step by step
"""
import pyxel
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class TutorialStage(Enum):
    WELCOME = "welcome"
    CAMERA_CONTROL = "camera_control"
    FIRST_ROAD = "first_road"
    FIRST_RESIDENTIAL = "first_residential"
    POWER_PLANT = "power_plant"
    POWER_LINES = "power_lines"
    COMMERCIAL_ZONE = "commercial_zone"
    INDUSTRIAL_ZONE = "industrial_zone"
    WATER_SYSTEM = "water_system"
    PUBLIC_SERVICES = "public_services"
    TRAFFIC_MANAGEMENT = "traffic_management"
    ECONOMY_BASICS = "economy_basics"
    DISASTER_PREPARATION = "disaster_preparation"
    ADVANCED_FEATURES = "advanced_features"
    COMPLETION = "completion"

@dataclass
class TutorialStep:
    """Individual tutorial step definition"""
    id: str
    stage: TutorialStage
    title: str
    japanese_title: str
    description: str
    japanese_description: str
    objective: str
    japanese_objective: str
    completion_condition: Callable
    highlight_area: Optional[Tuple[int, int, int, int]] = None  # x, y, width, height
    highlight_tool: Optional[str] = None
    arrow_position: Optional[Tuple[int, int]] = None
    reward: int = 0
    skip_allowed: bool = True
    auto_advance: bool = True
    timeout: Optional[int] = None  # Frames before auto-skip

@dataclass
class TutorialProgress:
    """Player's tutorial progress"""
    current_stage: TutorialStage
    current_step: int
    completed_steps: List[str]
    total_rewards: int
    start_time: int
    completion_time: Optional[int] = None
    skipped: bool = False

class TutorialOverlay:
    """Visual overlay for tutorial guidance"""
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.animation_timer = 0
        self.pulse_alpha = 0
        
    def draw_highlight(self, x: int, y: int, width: int, height: int):
        """Draw highlighted area with pulsing effect"""
        self.animation_timer += 1
        self.pulse_alpha = abs(pyxel.sin(self.animation_timer * 0.05)) * 0.5 + 0.5
        
        # Darken everything except highlighted area
        # Top
        pyxel.rect(0, 0, self.screen_width, y, 0)
        # Bottom
        pyxel.rect(0, y + height, self.screen_width, self.screen_height - (y + height), 0)
        # Left
        pyxel.rect(0, y, x, height, 0)
        # Right
        pyxel.rect(x + width, y, self.screen_width - (x + width), height, 0)
        
        # Highlight border
        for i in range(3):
            alpha = self.pulse_alpha if i == 0 else 1.0
            color = 11 if i == 0 else 10 if i == 1 else 7
            pyxel.rectb(x - i, y - i, width + i*2, height + i*2, color)
    
    def draw_arrow(self, x: int, y: int, direction: str = "down"):
        """Draw animated arrow pointing to something"""
        offset = int(pyxel.sin(self.animation_timer * 0.1) * 5)
        
        if direction == "down":
            y += offset
            points = [(x, y), (x - 10, y - 10), (x - 5, y - 10), 
                     (x - 5, y - 20), (x + 5, y - 20), (x + 5, y - 10), 
                     (x + 10, y - 10)]
        elif direction == "up":
            y -= offset
            points = [(x, y), (x - 10, y + 10), (x - 5, y + 10),
                     (x - 5, y + 20), (x + 5, y + 20), (x + 5, y + 10),
                     (x + 10, y + 10)]
        elif direction == "left":
            x -= offset
            points = [(x, y), (x + 10, y - 10), (x + 10, y - 5),
                     (x + 20, y - 5), (x + 20, y + 5), (x + 10, y + 5),
                     (x + 10, y + 10)]
        else:  # right
            x += offset
            points = [(x, y), (x - 10, y - 10), (x - 10, y - 5),
                     (x - 20, y - 5), (x - 20, y + 5), (x - 10, y + 5),
                     (x - 10, y + 10)]
        
        # Draw arrow shadow
        for i in range(len(points) - 1):
            pyxel.line(points[i][0] + 1, points[i][1] + 1, 
                      points[i+1][0] + 1, points[i+1][1] + 1, 0)
        
        # Draw arrow
        for i in range(len(points) - 1):
            pyxel.line(points[i][0], points[i][1], 
                      points[i+1][0], points[i+1][1], 10)
    
    def draw_tooltip(self, x: int, y: int, text: str, width: int = 200):
        """Draw tooltip with text"""
        lines = self._wrap_text(text, width // 4)
        height = len(lines) * 10 + 10
        
        # Adjust position to fit on screen
        if x + width > self.screen_width:
            x = self.screen_width - width
        if y + height > self.screen_height:
            y = self.screen_height - height
        
        # Background
        pyxel.rect(x, y, width, height, 0)
        pyxel.rectb(x, y, width, height, 7)
        
        # Text
        for i, line in enumerate(lines):
            pyxel.text(x + 5, y + 5 + i * 10, line, 7)
    
    def _wrap_text(self, text: str, max_chars: int) -> List[str]:
        """Wrap text to fit within width"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= max_chars:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines

class TutorialManager:
    """Main tutorial management system"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.overlay = TutorialOverlay(screen_width, screen_height)
        
        # Tutorial state
        self.enabled = False
        self.progress = None
        self.current_step = None
        self.step_start_time = 0
        
        # Tutorial steps
        self.steps = self._create_tutorial_steps()
        self.stage_order = list(TutorialStage)
        
        # Callbacks
        self.on_complete = None
        self.on_skip = None
        self.on_step_complete = None
        
        # UI state
        self.show_skip_button = True
        self.show_progress = True
        self.message_timer = 0
        self.success_message = ""
    
    def _create_tutorial_steps(self) -> List[TutorialStep]:
        """Create all tutorial steps"""
        steps = []
        
        # Welcome
        steps.append(TutorialStep(
            id="welcome",
            stage=TutorialStage.WELCOME,
            title="Welcome to ConcLand!",
            japanese_title="ConcLandへようこそ！",
            description="You've been elected as the new mayor. Let's build a thriving city!",
            japanese_description="新しい市長に選ばれました。繁栄する都市を建設しましょう！",
            objective="Press any key to continue",
            japanese_objective="任意のキーを押して続ける",
            completion_condition=lambda game: pyxel.btnp(pyxel.KEY_SPACE),
            reward=1000
        ))
        
        # Camera control
        steps.append(TutorialStep(
            id="camera_control",
            stage=TutorialStage.CAMERA_CONTROL,
            title="Camera Control",
            japanese_title="カメラ操作",
            description="Use arrow keys to move the camera around the map",
            japanese_description="矢印キーでカメラを移動できます",
            objective="Move the camera in any direction",
            japanese_objective="カメラを任意の方向に移動",
            completion_condition=lambda game: game.camera_moved,
            arrow_position=(400, 300),
            reward=500
        ))
        
        # First road
        steps.append(TutorialStep(
            id="first_road",
            stage=TutorialStage.FIRST_ROAD,
            title="Building Roads",
            japanese_title="道路建設",
            description="Roads connect your city. Press 4 to select the road tool",
            japanese_description="道路は都市を接続します。4キーで道路ツールを選択",
            objective="Build 10 road tiles",
            japanese_objective="道路を10タイル建設",
            completion_condition=lambda game: self._count_buildings(game, "ROAD") >= 10,
            highlight_tool="road",
            reward=2000
        ))
        
        # First residential
        steps.append(TutorialStep(
            id="first_residential",
            stage=TutorialStage.FIRST_RESIDENTIAL,
            title="Residential Zones",
            japanese_title="住宅地区",
            description="Citizens need homes. Press 1 for residential zones",
            japanese_description="市民には家が必要です。1キーで住宅地区を選択",
            objective="Place 5 residential zones",
            japanese_objective="住宅地区を5つ配置",
            completion_condition=lambda game: self._count_buildings(game, "RESIDENTIAL") >= 5,
            highlight_tool="residential",
            reward=3000
        ))
        
        # Power plant
        steps.append(TutorialStep(
            id="power_plant",
            stage=TutorialStage.POWER_PLANT,
            title="Power Generation",
            japanese_title="発電所",
            description="Buildings need power. Press 7 to build a power plant",
            japanese_description="建物には電力が必要です。7キーで発電所を建設",
            objective="Build a power plant",
            japanese_objective="発電所を建設",
            completion_condition=lambda game: self._has_power_plant(game),
            highlight_tool="power",
            reward=5000
        ))
        
        # Power lines
        steps.append(TutorialStep(
            id="power_lines",
            stage=TutorialStage.POWER_LINES,
            title="Power Distribution",
            japanese_title="送電線",
            description="Connect power to buildings with power lines (6 key)",
            japanese_description="送電線(6キー)で建物に電力を接続",
            objective="Connect power to residential zones",
            japanese_objective="住宅地区に電力を接続",
            completion_condition=lambda game: self._has_powered_residential(game),
            highlight_tool="wire",
            reward=2000
        ))
        
        # Commercial zone
        steps.append(TutorialStep(
            id="commercial_zone",
            stage=TutorialStage.COMMERCIAL_ZONE,
            title="Commercial Development",
            japanese_title="商業開発",
            description="Commercial zones provide jobs and services (2 key)",
            japanese_description="商業地区は仕事とサービスを提供(2キー)",
            objective="Build 3 commercial zones",
            japanese_objective="商業地区を3つ建設",
            completion_condition=lambda game: self._count_buildings(game, "COMMERCIAL") >= 3,
            highlight_tool="commercial",
            reward=3000
        ))
        
        # Industrial zone
        steps.append(TutorialStep(
            id="industrial_zone",
            stage=TutorialStage.INDUSTRIAL_ZONE,
            title="Industrial Growth",
            japanese_title="工業発展",
            description="Industries provide jobs and tax revenue (3 key)",
            japanese_description="工業は仕事と税収を提供(3キー)",
            objective="Build 3 industrial zones",
            japanese_objective="工業地区を3つ建設",
            completion_condition=lambda game: self._count_buildings(game, "INDUSTRIAL") >= 3,
            highlight_tool="industrial",
            reward=3000
        ))
        
        # Advanced features info
        steps.append(TutorialStep(
            id="advanced_features",
            stage=TutorialStage.ADVANCED_FEATURES,
            title="Advanced Features",
            japanese_title="高度な機能",
            description="Press S for stats, E for economy, T for traffic, D for disasters",
            japanese_description="S:統計、E:経済、T:交通、D:災害",
            objective="Explore the advanced panels",
            japanese_objective="高度なパネルを探索",
            completion_condition=lambda game: game.panels_viewed >= 2,
            reward=5000,
            auto_advance=False
        ))
        
        # Completion
        steps.append(TutorialStep(
            id="completion",
            stage=TutorialStage.COMPLETION,
            title="Tutorial Complete!",
            japanese_title="チュートリアル完了！",
            description="You're ready to build your city! Good luck, Mayor!",
            japanese_description="都市建設の準備ができました！頑張ってください、市長！",
            objective="Start building your dream city",
            japanese_objective="夢の都市建設を始める",
            completion_condition=lambda game: True,
            reward=10000,
            auto_advance=False
        ))
        
        return steps
    
    def start_tutorial(self):
        """Start the tutorial from beginning"""
        self.enabled = True
        self.progress = TutorialProgress(
            current_stage=TutorialStage.WELCOME,
            current_step=0,
            completed_steps=[],
            total_rewards=0,
            start_time=pyxel.frame_count
        )
        self.current_step = self.steps[0]
        self.step_start_time = pyxel.frame_count
        
    def skip_tutorial(self):
        """Skip the entire tutorial"""
        if self.progress:
            self.progress.skipped = True
            self.progress.completion_time = pyxel.frame_count
        
        self.enabled = False
        
        if self.on_skip:
            self.on_skip()
    
    def next_step(self):
        """Advance to next tutorial step"""
        if not self.enabled or not self.progress:
            return
        
        # Mark current step as complete
        if self.current_step:
            self.progress.completed_steps.append(self.current_step.id)
            self.progress.total_rewards += self.current_step.reward
            
            # Show success message
            self.success_message = f"+¥{self.current_step.reward:,}"
            self.message_timer = 120
            
            if self.on_step_complete:
                self.on_step_complete(self.current_step)
        
        # Find next step
        current_index = self.steps.index(self.current_step) if self.current_step else -1
        
        if current_index < len(self.steps) - 1:
            self.current_step = self.steps[current_index + 1]
            self.progress.current_stage = self.current_step.stage
            self.progress.current_step = current_index + 1
            self.step_start_time = pyxel.frame_count
        else:
            # Tutorial complete
            self.complete_tutorial()
    
    def complete_tutorial(self):
        """Mark tutorial as complete"""
        if self.progress:
            self.progress.completion_time = pyxel.frame_count
        
        self.enabled = False
        
        if self.on_complete:
            self.on_complete(self.progress)
    
    def update(self, game_state):
        """Update tutorial state"""
        if not self.enabled or not self.current_step:
            return
        
        # Check completion condition
        if self.current_step.completion_condition(game_state):
            if self.current_step.auto_advance:
                self.next_step()
        
        # Check timeout
        if self.current_step.timeout:
            elapsed = pyxel.frame_count - self.step_start_time
            if elapsed > self.current_step.timeout:
                self.next_step()
        
        # Update animation
        self.overlay.animation_timer += 1
        
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1
    
    def draw(self, language: str = "japanese"):
        """Draw tutorial overlay"""
        if not self.enabled or not self.current_step:
            return
        
        # Draw highlight if specified
        if self.current_step.highlight_area:
            x, y, w, h = self.current_step.highlight_area
            self.overlay.draw_highlight(x, y, w, h)
        
        # Draw arrow if specified
        if self.current_step.arrow_position:
            x, y = self.current_step.arrow_position
            self.overlay.draw_arrow(x, y)
        
        # Draw tutorial panel
        self._draw_tutorial_panel(language)
        
        # Draw progress bar
        if self.show_progress:
            self._draw_progress_bar()
        
        # Draw success message
        if self.message_timer > 0:
            self._draw_success_message()
    
    def _draw_tutorial_panel(self, language: str):
        """Draw tutorial instruction panel"""
        panel_width = 400
        panel_height = 120
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = 20
        
        # Background
        pyxel.rect(panel_x, panel_y, panel_width, panel_height, 0)
        pyxel.rectb(panel_x, panel_y, panel_width, panel_height, 7)
        
        # Title
        title = self.current_step.japanese_title if language == "japanese" else self.current_step.title
        pyxel.text(panel_x + 10, panel_y + 10, title, 10)
        
        # Description
        desc = self.current_step.japanese_description if language == "japanese" else self.current_step.description
        lines = self.overlay._wrap_text(desc, panel_width // 4 - 5)
        for i, line in enumerate(lines):
            pyxel.text(panel_x + 10, panel_y + 25 + i * 10, line, 7)
        
        # Objective
        obj = self.current_step.japanese_objective if language == "japanese" else self.current_step.objective
        pyxel.text(panel_x + 10, panel_y + 65, "目標: " if language == "japanese" else "Goal: ", 11)
        pyxel.text(panel_x + 40, panel_y + 65, obj, 11)
        
        # Skip button
        if self.show_skip_button and self.current_step.skip_allowed:
            skip_text = "スキップ [X]" if language == "japanese" else "Skip [X]"
            pyxel.text(panel_x + panel_width - 70, panel_y + panel_height - 20, skip_text, 6)
        
        # Reward
        if self.current_step.reward > 0:
            reward_text = f"報酬: ¥{self.current_step.reward:,}" if language == "japanese" else f"Reward: ¥{self.current_step.reward:,}"
            pyxel.text(panel_x + 10, panel_y + panel_height - 20, reward_text, 10)
    
    def _draw_progress_bar(self):
        """Draw tutorial progress bar"""
        bar_width = 300
        bar_height = 8
        bar_x = (self.screen_width - bar_width) // 2
        bar_y = self.screen_height - 30
        
        # Background
        pyxel.rect(bar_x, bar_y, bar_width, bar_height, 1)
        
        # Progress
        if self.progress:
            progress = (self.progress.current_step + 1) / len(self.steps)
            fill_width = int(bar_width * progress)
            pyxel.rect(bar_x, bar_y, fill_width, bar_height, 11)
        
        # Border
        pyxel.rectb(bar_x, bar_y, bar_width, bar_height, 7)
        
        # Step counter
        step_text = f"{self.progress.current_step + 1}/{len(self.steps)}"
        pyxel.text(bar_x + bar_width + 10, bar_y, step_text, 7)
    
    def _draw_success_message(self):
        """Draw success animation"""
        if self.message_timer <= 0:
            return
        
        # Fade effect
        alpha = min(1.0, self.message_timer / 60.0)
        
        # Position with floating animation
        x = self.screen_width // 2 - 30
        y = self.screen_height // 2 - 50 - (120 - self.message_timer) // 2
        
        # Draw message
        pyxel.text(x + 1, y + 1, self.success_message, 0)  # Shadow
        pyxel.text(x, y, self.success_message, 10)  # Main text
    
    def _count_buildings(self, game_state, building_type: str) -> int:
        """Count buildings of specific type"""
        count = 0
        for row in game_state.grid:
            for cell in row:
                if hasattr(cell, 'name') and building_type in str(cell):
                    count += 1
        return count
    
    def _has_power_plant(self, game_state) -> bool:
        """Check if power plant exists"""
        for row in game_state.grid:
            for cell in row:
                if hasattr(cell, 'name') and 'PLANT' in str(cell):
                    return True
        return False
    
    def _has_powered_residential(self, game_state) -> bool:
        """Check if any residential zone has power"""
        for y, row in enumerate(game_state.grid):
            for x, cell in enumerate(row):
                if hasattr(cell, 'name') and 'RESIDENTIAL' in str(cell):
                    if game_state.sim_data[y][x].power:
                        return True
        return False

class TutorialGameState:
    """Mock game state for tutorial testing"""
    def __init__(self):
        self.grid = [[None for _ in range(100)] for _ in range(100)]
        self.sim_data = [[MockSimData() for _ in range(100)] for _ in range(100)]
        self.camera_moved = False
        self.panels_viewed = 0

class MockSimData:
    """Mock simulation data"""
    def __init__(self):
        self.power = False
        self.water = False
        self.population = 0

# Integration helper
def integrate_tutorial_with_game(game_instance, tutorial_manager):
    """Helper function to integrate tutorial with main game"""
    
    # Set up callbacks
    def on_tutorial_complete(progress):
        print(f"Tutorial completed! Total rewards: ¥{progress.total_rewards:,}")
        game_instance.funds += progress.total_rewards
        game_instance.tutorial_completed = True
    
    def on_tutorial_skip():
        print("Tutorial skipped")
        game_instance.tutorial_completed = True
    
    def on_step_complete(step):
        print(f"Step completed: {step.id}")
        game_instance.funds += step.reward
    
    tutorial_manager.on_complete = on_tutorial_complete
    tutorial_manager.on_skip = on_tutorial_skip
    tutorial_manager.on_step_complete = on_step_complete
    
    return tutorial_manager