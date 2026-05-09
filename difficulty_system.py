"""
Difficulty and Game Balance System for ConcLand
Manages game difficulty settings and progression scaling
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
import math

class DifficultyLevel(Enum):
    SANDBOX = "sandbox"
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    EXPERT = "expert"
    CUSTOM = "custom"

@dataclass
class DifficultySettings:
    """Difficulty configuration parameters"""
    # Economic settings
    starting_funds: int
    tax_multiplier: float
    maintenance_cost_multiplier: float
    building_cost_multiplier: float
    resource_production_multiplier: float
    resource_consumption_multiplier: float
    
    # Growth settings
    population_growth_rate: float
    commercial_growth_rate: float
    industrial_growth_rate: float
    land_value_growth_rate: float
    
    # Disaster settings
    disaster_frequency: float
    disaster_severity_multiplier: float
    disaster_damage_multiplier: float
    disaster_warning_time_multiplier: float
    
    # Pollution settings
    pollution_generation_rate: float
    pollution_decay_rate: float
    pollution_spread_rate: float
    
    # Traffic settings
    traffic_capacity_multiplier: float
    traffic_congestion_threshold: float
    
    # Gameplay settings
    unlock_speed: float  # How fast new features unlock
    tutorial_hints: bool
    auto_save_enabled: bool
    pause_on_disaster: bool
    
    # Challenge modifiers
    limited_resources: bool
    random_events: bool
    economic_cycles: bool
    seasonal_effects: bool

class DifficultyPresets:
    """Predefined difficulty configurations"""
    
    SANDBOX = DifficultySettings(
        starting_funds=999999,
        tax_multiplier=2.0,
        maintenance_cost_multiplier=0.0,
        building_cost_multiplier=0.1,
        resource_production_multiplier=2.0,
        resource_consumption_multiplier=0.5,
        population_growth_rate=2.0,
        commercial_growth_rate=2.0,
        industrial_growth_rate=2.0,
        land_value_growth_rate=1.5,
        disaster_frequency=0.0,
        disaster_severity_multiplier=0.0,
        disaster_damage_multiplier=0.0,
        disaster_warning_time_multiplier=2.0,
        pollution_generation_rate=0.2,
        pollution_decay_rate=2.0,
        pollution_spread_rate=0.1,
        traffic_capacity_multiplier=2.0,
        traffic_congestion_threshold=0.9,
        unlock_speed=3.0,
        tutorial_hints=True,
        auto_save_enabled=True,
        pause_on_disaster=False,
        limited_resources=False,
        random_events=False,
        economic_cycles=False,
        seasonal_effects=False
    )
    
    EASY = DifficultySettings(
        starting_funds=20000,
        tax_multiplier=1.3,
        maintenance_cost_multiplier=0.7,
        building_cost_multiplier=0.8,
        resource_production_multiplier=1.3,
        resource_consumption_multiplier=0.8,
        population_growth_rate=1.5,
        commercial_growth_rate=1.4,
        industrial_growth_rate=1.4,
        land_value_growth_rate=1.2,
        disaster_frequency=0.0001,
        disaster_severity_multiplier=0.5,
        disaster_damage_multiplier=0.5,
        disaster_warning_time_multiplier=1.5,
        pollution_generation_rate=0.7,
        pollution_decay_rate=1.3,
        pollution_spread_rate=0.2,
        traffic_capacity_multiplier=1.3,
        traffic_congestion_threshold=0.7,
        unlock_speed=1.5,
        tutorial_hints=True,
        auto_save_enabled=True,
        pause_on_disaster=True,
        limited_resources=False,
        random_events=False,
        economic_cycles=False,
        seasonal_effects=True
    )
    
    NORMAL = DifficultySettings(
        starting_funds=10000,
        tax_multiplier=1.0,
        maintenance_cost_multiplier=1.0,
        building_cost_multiplier=1.0,
        resource_production_multiplier=1.0,
        resource_consumption_multiplier=1.0,
        population_growth_rate=1.0,
        commercial_growth_rate=1.0,
        industrial_growth_rate=1.0,
        land_value_growth_rate=1.0,
        disaster_frequency=0.0005,
        disaster_severity_multiplier=1.0,
        disaster_damage_multiplier=1.0,
        disaster_warning_time_multiplier=1.0,
        pollution_generation_rate=1.0,
        pollution_decay_rate=1.0,
        pollution_spread_rate=0.25,
        traffic_capacity_multiplier=1.0,
        traffic_congestion_threshold=0.5,
        unlock_speed=1.0,
        tutorial_hints=True,
        auto_save_enabled=True,
        pause_on_disaster=False,
        limited_resources=False,
        random_events=True,
        economic_cycles=True,
        seasonal_effects=True
    )
    
    HARD = DifficultySettings(
        starting_funds=5000,
        tax_multiplier=0.8,
        maintenance_cost_multiplier=1.5,
        building_cost_multiplier=1.3,
        resource_production_multiplier=0.8,
        resource_consumption_multiplier=1.3,
        population_growth_rate=0.7,
        commercial_growth_rate=0.7,
        industrial_growth_rate=0.7,
        land_value_growth_rate=0.8,
        disaster_frequency=0.001,
        disaster_severity_multiplier=1.5,
        disaster_damage_multiplier=1.5,
        disaster_warning_time_multiplier=0.7,
        pollution_generation_rate=1.5,
        pollution_decay_rate=0.7,
        pollution_spread_rate=0.35,
        traffic_capacity_multiplier=0.8,
        traffic_congestion_threshold=0.3,
        unlock_speed=0.7,
        tutorial_hints=False,
        auto_save_enabled=True,
        pause_on_disaster=False,
        limited_resources=True,
        random_events=True,
        economic_cycles=True,
        seasonal_effects=True
    )
    
    EXPERT = DifficultySettings(
        starting_funds=2000,
        tax_multiplier=0.6,
        maintenance_cost_multiplier=2.0,
        building_cost_multiplier=1.5,
        resource_production_multiplier=0.6,
        resource_consumption_multiplier=1.5,
        population_growth_rate=0.5,
        commercial_growth_rate=0.5,
        industrial_growth_rate=0.5,
        land_value_growth_rate=0.6,
        disaster_frequency=0.002,
        disaster_severity_multiplier=2.0,
        disaster_damage_multiplier=2.0,
        disaster_warning_time_multiplier=0.5,
        pollution_generation_rate=2.0,
        pollution_decay_rate=0.5,
        pollution_spread_rate=0.5,
        traffic_capacity_multiplier=0.6,
        traffic_congestion_threshold=0.2,
        unlock_speed=0.5,
        tutorial_hints=False,
        auto_save_enabled=False,
        pause_on_disaster=False,
        limited_resources=True,
        random_events=True,
        economic_cycles=True,
        seasonal_effects=True
    )

class GameSpeedController:
    """Controls game simulation speed"""
    
    SPEED_SETTINGS = {
        "pause": 0,
        "slow": 0.5,
        "normal": 1.0,
        "fast": 2.0,
        "ultra": 4.0
    }
    
    def __init__(self):
        self.current_speed = "normal"
        self.speed_multiplier = 1.0
        self.paused = False
        self.frame_skip = 0
        self.accumulated_time = 0.0
    
    def set_speed(self, speed: str):
        """Set game speed"""
        if speed in self.SPEED_SETTINGS:
            self.current_speed = speed
            self.speed_multiplier = self.SPEED_SETTINGS[speed]
            self.paused = (speed == "pause")
    
    def toggle_pause(self):
        """Toggle pause state"""
        if self.paused:
            self.set_speed("normal")
        else:
            self.set_speed("pause")
    
    def should_update(self, delta_time: float) -> bool:
        """Check if simulation should update this frame"""
        if self.paused:
            return False
        
        self.accumulated_time += delta_time * self.speed_multiplier
        
        if self.accumulated_time >= 1.0:
            self.accumulated_time -= 1.0
            return True
        
        return False
    
    def get_time_scale(self) -> float:
        """Get current time scale for animations"""
        return self.speed_multiplier if not self.paused else 0.0

class ProgressionSystem:
    """Manages player progression and unlocks"""
    
    def __init__(self, unlock_speed: float = 1.0):
        self.unlock_speed = unlock_speed
        self.player_level = 1
        self.experience = 0
        self.unlocked_features = set(["basic"])
        self.milestones = []
        
        # Feature unlock requirements
        self.unlock_requirements = {
            "basic": 0,
            "public_services": 3,
            "education": 5,
            "healthcare": 7,
            "transportation": 10,
            "entertainment": 12,
            "policies": 15,
            "advanced_buildings": 18,
            "special_projects": 20,
            "megaprojects": 25
        }
    
    def add_experience(self, amount: int):
        """Add experience points"""
        self.experience += int(amount * self.unlock_speed)
        self._check_level_up()
    
    def _check_level_up(self):
        """Check if player has leveled up"""
        required_exp = self._get_required_experience(self.player_level + 1)
        
        while self.experience >= required_exp:
            self.experience -= required_exp
            self.player_level += 1
            self._unlock_features()
            required_exp = self._get_required_experience(self.player_level + 1)
    
    def _get_required_experience(self, level: int) -> int:
        """Calculate experience required for level"""
        return int(100 * math.pow(1.5, level - 1))
    
    def _unlock_features(self):
        """Unlock features based on level"""
        for feature, required_level in self.unlock_requirements.items():
            if self.player_level >= required_level and feature not in self.unlocked_features:
                self.unlocked_features.add(feature)
                self._add_milestone(f"Unlocked: {feature}")
    
    def _add_milestone(self, description: str):
        """Add milestone to history"""
        self.milestones.append({
            "level": self.player_level,
            "description": description,
            "timestamp": None  # Would be actual game time
        })
    
    def is_unlocked(self, feature: str) -> bool:
        """Check if feature is unlocked"""
        return feature in self.unlocked_features
    
    def get_next_unlock(self) -> Optional[tuple]:
        """Get next feature to unlock"""
        for feature, required_level in sorted(self.unlock_requirements.items(), key=lambda x: x[1]):
            if feature not in self.unlocked_features:
                return feature, required_level
        return None
    
    def get_progress_to_next_level(self) -> float:
        """Get progress to next level as percentage"""
        required = self._get_required_experience(self.player_level + 1)
        return self.experience / required if required > 0 else 1.0

class DifficultyManager:
    """Main difficulty management system"""
    
    def __init__(self):
        self.current_difficulty = DifficultyLevel.NORMAL
        self.settings = DifficultyPresets.NORMAL
        self.custom_settings = None
        
        self.speed_controller = GameSpeedController()
        self.progression_system = ProgressionSystem(self.settings.unlock_speed)
        
        # Dynamic difficulty adjustment
        self.dynamic_adjustment_enabled = False
        self.performance_history = []
        self.adjustment_counter = 0
    
    def set_difficulty(self, level: DifficultyLevel, custom_settings: Optional[DifficultySettings] = None):
        """Set game difficulty"""
        self.current_difficulty = level
        
        if level == DifficultyLevel.CUSTOM and custom_settings:
            self.settings = custom_settings
            self.custom_settings = custom_settings
        else:
            preset_map = {
                DifficultyLevel.SANDBOX: DifficultyPresets.SANDBOX,
                DifficultyLevel.EASY: DifficultyPresets.EASY,
                DifficultyLevel.NORMAL: DifficultyPresets.NORMAL,
                DifficultyLevel.HARD: DifficultyPresets.HARD,
                DifficultyLevel.EXPERT: DifficultyPresets.EXPERT
            }
            self.settings = preset_map.get(level, DifficultyPresets.NORMAL)
        
        # Update progression system speed
        self.progression_system.unlock_speed = self.settings.unlock_speed
    
    def apply_to_game(self, game_instance):
        """Apply difficulty settings to game instance"""
        game = game_instance
        
        # Apply economic settings
        game.funds = self.settings.starting_funds
        
        # Apply to economic system if present
        if hasattr(game, 'economic_system'):
            eco = game.economic_system
            eco.tax_multiplier = self.settings.tax_multiplier
            eco.maintenance_multiplier = self.settings.maintenance_cost_multiplier
        
        # Apply to disaster system if present
        if hasattr(game, 'disaster_system'):
            disaster = game.disaster_system
            disaster.base_disaster_chance = self.settings.disaster_frequency
            disaster.severity_multiplier = self.settings.disaster_severity_multiplier
        
        # Apply growth rates
        if hasattr(game, 'growth_rates'):
            game.growth_rates['residential'] = self.settings.population_growth_rate
            game.growth_rates['commercial'] = self.settings.commercial_growth_rate
            game.growth_rates['industrial'] = self.settings.industrial_growth_rate
    
    def enable_dynamic_adjustment(self):
        """Enable dynamic difficulty adjustment"""
        self.dynamic_adjustment_enabled = True
    
    def update_performance_metrics(self, metrics: Dict[str, Any]):
        """Update player performance metrics for dynamic adjustment"""
        if not self.dynamic_adjustment_enabled:
            return
        
        self.performance_history.append(metrics)
        
        # Keep only recent history
        if len(self.performance_history) > 100:
            self.performance_history.pop(0)
        
        # Check for adjustment every 50 updates
        self.adjustment_counter += 1
        if self.adjustment_counter >= 50:
            self._adjust_difficulty()
            self.adjustment_counter = 0
    
    def _adjust_difficulty(self):
        """Dynamically adjust difficulty based on performance"""
        if len(self.performance_history) < 20:
            return
        
        # Calculate average performance
        avg_funds = sum(m.get('funds', 0) for m in self.performance_history) / len(self.performance_history)
        avg_population = sum(m.get('population', 0) for m in self.performance_history) / len(self.performance_history)
        disasters_survived = sum(m.get('disasters_survived', 0) for m in self.performance_history)
        
        # Determine if adjustment needed
        if avg_funds < 1000 and avg_population < 100:
            # Player struggling - make easier
            self._make_easier()
        elif avg_funds > 50000 and avg_population > 5000 and disasters_survived > 3:
            # Player doing very well - make harder
            self._make_harder()
    
    def _make_easier(self):
        """Make game slightly easier"""
        self.settings.tax_multiplier = min(2.0, self.settings.tax_multiplier * 1.1)
        self.settings.maintenance_cost_multiplier = max(0.5, self.settings.maintenance_cost_multiplier * 0.9)
        self.settings.disaster_frequency = max(0.0, self.settings.disaster_frequency * 0.8)
        print("Difficulty adjusted: Slightly easier")
    
    def _make_harder(self):
        """Make game slightly harder"""
        self.settings.tax_multiplier = max(0.5, self.settings.tax_multiplier * 0.95)
        self.settings.maintenance_cost_multiplier = min(2.0, self.settings.maintenance_cost_multiplier * 1.05)
        self.settings.disaster_frequency = min(0.01, self.settings.disaster_frequency * 1.1)
        print("Difficulty adjusted: Slightly harder")
    
    def get_difficulty_info(self) -> Dict[str, Any]:
        """Get current difficulty information"""
        return {
            "level": self.current_difficulty.value,
            "starting_funds": self.settings.starting_funds,
            "tax_multiplier": self.settings.tax_multiplier,
            "disaster_frequency": self.settings.disaster_frequency,
            "unlock_speed": self.settings.unlock_speed,
            "player_level": self.progression_system.player_level,
            "unlocked_features": list(self.progression_system.unlocked_features),
            "game_speed": self.speed_controller.current_speed,
            "dynamic_adjustment": self.dynamic_adjustment_enabled
        }
    
    def save_settings(self, filename: str = "difficulty_settings.json"):
        """Save custom difficulty settings"""
        if self.custom_settings:
            data = {
                "difficulty": self.current_difficulty.value,
                "settings": self.custom_settings.__dict__,
                "progression": {
                    "level": self.progression_system.player_level,
                    "experience": self.progression_system.experience,
                    "unlocked": list(self.progression_system.unlocked_features)
                }
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
    
    def load_settings(self, filename: str = "difficulty_settings.json"):
        """Load custom difficulty settings"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Reconstruct settings
            settings_dict = data.get('settings', {})
            custom_settings = DifficultySettings(**settings_dict)
            
            # Apply settings
            self.set_difficulty(DifficultyLevel(data.get('difficulty', 'normal')), custom_settings)
            
            # Restore progression
            prog_data = data.get('progression', {})
            self.progression_system.player_level = prog_data.get('level', 1)
            self.progression_system.experience = prog_data.get('experience', 0)
            self.progression_system.unlocked_features = set(prog_data.get('unlocked', ['basic']))
            
            return True
        except Exception as e:
            print(f"Failed to load difficulty settings: {e}")
            return False

# Helper function for UI
def get_difficulty_descriptions() -> Dict[str, Dict[str, str]]:
    """Get descriptions of difficulty levels for UI"""
    return {
        "sandbox": {
            "name": "サンドボックス",
            "name_en": "Sandbox",
            "description": "制限なしの創造的なプレイ",
            "description_en": "Unlimited creative play"
        },
        "easy": {
            "name": "簡単",
            "name_en": "Easy",
            "description": "初心者向け、リラックスしたプレイ",
            "description_en": "For beginners, relaxed gameplay"
        },
        "normal": {
            "name": "普通",
            "name_en": "Normal",
            "description": "バランスの取れた挑戦",
            "description_en": "Balanced challenge"
        },
        "hard": {
            "name": "困難",
            "name_en": "Hard",
            "description": "経験豊富なプレイヤー向け",
            "description_en": "For experienced players"
        },
        "expert": {
            "name": "エキスパート",
            "name_en": "Expert",
            "description": "究極の挑戦",
            "description_en": "Ultimate challenge"
        }
    }