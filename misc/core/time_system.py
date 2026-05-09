"""
Time and Era Management System for ConcLand
Handles historical progression from 1945 to 1970
"""
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import date, timedelta

@dataclass
class Era:
    """Represents a historical era"""
    id: str
    name: str
    japanese_name: str
    start_year: int
    end_year: int
    description: str
    background_color: tuple
    ui_theme: str
    available_resources: List[str]
    starting_conditions: Dict[str, Any]
    economic_modifiers: Dict[str, Any]

class TimeSystem:
    """Manages game time progression and era transitions"""
    
    def __init__(self):
        self.current_date = date(1945, 8, 15)  # End of WWII
        self.current_era: Optional[Era] = None
        self.eras: Dict[str, Era] = {}
        self.transition_requirements: Dict[str, Dict] = {}
        
        # Time progression settings
        self.days_per_tick = 1
        self.paused = False
        self.speed_multiplier = 1.0  # 1.0 = normal, 2.0 = 2x speed, etc.
        
        # Seasonal system
        self.season_effects_active = True
        
        # Load era data
        self.load_era_data()
        
        # Initialize with first era
        if self.eras:
            first_era_id = list(self.eras.keys())[0]
            self.current_era = self.eras[first_era_id]
    
    def load_era_data(self):
        """Load era definitions from JSON"""
        try:
            with open('data/historical/eras.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Load eras
            for era_data in data['eras']:
                era = Era(
                    id=era_data['id'],
                    name=era_data['name'],
                    japanese_name=era_data['japanese_name'],
                    start_year=era_data['start_year'],
                    end_year=era_data['end_year'],
                    description=era_data['description'],
                    background_color=tuple(era_data['background_color']),
                    ui_theme=era_data['ui_theme'],
                    available_resources=era_data['available_resources'],
                    starting_conditions=era_data.get('starting_conditions', {}),
                    economic_modifiers=era_data.get('economic_modifiers', {})
                )
                self.eras[era.id] = era
            
            # Load transition requirements
            self.transition_requirements = data.get('transition_requirements', {})
            
        except FileNotFoundError:
            print("Era data file not found. Using fallback data.")
            self._create_fallback_eras()
    
    def _create_fallback_eras(self):
        """Create basic era data if JSON loading fails"""
        fallback_era = Era(
            id="postwar_recovery",
            name="終戦直後",
            japanese_name="終戦直後",
            start_year=1945,
            end_year=1950,
            description="焼け野原からの復興期",
            background_color=(60, 60, 60),
            ui_theme="gray",
            available_resources=["rice", "wood", "scrap_iron"],
            starting_conditions={"population": 100, "funds": 1000},
            economic_modifiers={"construction_cost": 1.5}
        )
        self.eras["postwar_recovery"] = fallback_era
    
    def update(self):
        """Update time progression"""
        if self.paused:
            return
        
        # Advance time
        days_to_advance = int(self.days_per_tick * self.speed_multiplier)
        self.current_date += timedelta(days=days_to_advance)
        
        # Check for era transitions
        self._check_era_transition()
    
    def _check_era_transition(self):
        """Check if conditions are met for era transition"""
        if not self.current_era:
            return
        
        current_year = self.current_date.year
        
        # Check if we've reached the end of current era
        if current_year >= self.current_era.end_year:
            self._advance_to_next_era()
    
    def _advance_to_next_era(self):
        """Advance to the next historical era"""
        if not self.current_era:
            return
        
        # Find next era chronologically
        next_era = None
        for era in self.eras.values():
            if era.start_year > self.current_era.start_year:
                if next_era is None or era.start_year < next_era.start_year:
                    next_era = era
        
        if next_era:
            self.current_era = next_era
            print(f"時代が変わりました: {next_era.japanese_name}")
    
    def can_build_in_era(self, building_id: str) -> bool:
        """Check if a building can be built in the current era"""
        # This would check against building availability data
        # For now, return True as placeholder
        return True
    
    def get_resource_availability(self) -> List[str]:
        """Get list of resources available in current era"""
        if self.current_era:
            return self.current_era.available_resources
        return []
    
    def get_economic_modifier(self, modifier_name: str) -> float:
        """Get economic modifier for current era"""
        if self.current_era and modifier_name in self.current_era.economic_modifiers:
            return self.current_era.economic_modifiers[modifier_name]
        return 1.0
    
    def get_season(self) -> str:
        """Get current season"""
        month = self.current_date.month
        if month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        elif month in [9, 10, 11]:
            return "autumn"
        else:
            return "winter"
    
    def get_season_effects(self) -> Dict[str, float]:
        """Get seasonal effects on various game systems"""
        if not self.season_effects_active:
            return {}
        
        season = self.get_season()
        
        effects = {
            "spring": {
                "construction_speed": 1.2,
                "population_growth": 1.1,
                "happiness_bonus": 0.1
            },
            "summer": {
                "power_consumption": 1.3,
                "tourism": 1.2,
                "fire_risk": 1.4
            },
            "autumn": {
                "harvest_bonus": 1.5,
                "tourism": 1.1,
                "construction_speed": 1.1
            },
            "winter": {
                "heating_cost": 1.4,
                "construction_speed": 0.8,
                "power_consumption": 1.2
            }
        }
        
        return effects.get(season, {})
    
    def set_speed(self, multiplier: float):
        """Set time progression speed"""
        self.speed_multiplier = max(0.1, min(10.0, multiplier))
    
    def pause(self):
        """Pause time progression"""
        self.paused = True
    
    def resume(self):
        """Resume time progression"""
        self.paused = False
    
    def is_paused(self) -> bool:
        """Check if time is paused"""
        return self.paused
    
    def jump_to_era(self, era_id: str) -> bool:
        """Jump directly to a specific era (for testing/cheats)"""
        if era_id in self.eras:
            self.current_era = self.eras[era_id]
            self.current_date = date(self.current_era.start_year, 1, 1)
            return True
        return False
    
    def get_era_progress(self) -> float:
        """Get progress through current era (0.0 to 1.0)"""
        if not self.current_era:
            return 0.0
        
        current_year = self.current_date.year
        era_duration = self.current_era.end_year - self.current_era.start_year
        era_progress = current_year - self.current_era.start_year
        
        return min(1.0, max(0.0, era_progress / era_duration))
    
    def get_time_string(self) -> str:
        """Get formatted time string for display"""
        return self.current_date.strftime("%Y年%m月%d日")
    
    def get_era_string(self) -> str:
        """Get era name for display"""
        if self.current_era:
            return self.current_era.japanese_name
        return "不明な時代"
    
    def export_state(self) -> Dict[str, Any]:
        """Export time system state for saving"""
        return {
            "current_date": self.current_date.isoformat(),
            "current_era_id": self.current_era.id if self.current_era else None,
            "speed_multiplier": self.speed_multiplier,
            "paused": self.paused
        }
    
    def import_state(self, state: Dict[str, Any]):
        """Import time system state from save data"""
        try:
            self.current_date = date.fromisoformat(state["current_date"])
            if state["current_era_id"] and state["current_era_id"] in self.eras:
                self.current_era = self.eras[state["current_era_id"]]
            self.speed_multiplier = state.get("speed_multiplier", 1.0)
            self.paused = state.get("paused", False)
        except (KeyError, ValueError) as e:
            print(f"Error importing time system state: {e}")

class HistoricalCalendar:
    """Utility class for historical date calculations"""
    
    @staticmethod
    def is_historical_date(date_obj: date, event_date: str) -> bool:
        """Check if current date matches a historical event date"""
        try:
            event_date_obj = date.fromisoformat(event_date)
            return date_obj >= event_date_obj
        except ValueError:
            return False
    
    @staticmethod
    def days_since_war_end(current_date: date) -> int:
        """Calculate days since end of WWII"""
        war_end = date(1945, 8, 15)
        return (current_date - war_end).days
    
    @staticmethod
    def get_historical_context(current_date: date) -> str:
        """Get historical context description for current date"""
        year = current_date.year
        
        if year <= 1945:
            return "終戦直後の混乱期"
        elif year <= 1950:
            return "戦後復興期"
        elif year <= 1955:
            return "朝鮮戦争特需期"
        elif year <= 1960:
            return "神武景気・岩戸景気"
        elif year <= 1965:
            return "高度経済成長期"
        elif year <= 1970:
            return "東京オリンピック・大阪万博期"
        else:
            return "現代"