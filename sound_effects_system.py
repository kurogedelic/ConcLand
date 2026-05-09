"""
Sound and Visual Effects System for ConcLand
Manages background music, sound effects, and visual effects
"""
import pyxel
import random
import math
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

class SoundCategory(Enum):
    BGM = "bgm"
    SFX_UI = "sfx_ui"
    SFX_BUILDING = "sfx_building"
    SFX_TRAFFIC = "sfx_traffic"
    SFX_DISASTER = "sfx_disaster"
    SFX_AMBIENT = "sfx_ambient"

class VisualEffectType(Enum):
    PARTICLE = "particle"
    EXPLOSION = "explosion"
    CONSTRUCTION = "construction"
    SMOKE = "smoke"
    RAIN = "rain"
    SNOW = "snow"
    SPARKLE = "sparkle"
    FIRE = "fire"
    WATER = "water"

@dataclass
class SoundTrack:
    """Individual sound track definition"""
    id: str
    name: str
    japanese_name: str
    category: SoundCategory
    file_path: str
    loop: bool = True
    volume: float = 1.0
    pitch: float = 1.0
    fade_in: float = 0.0
    fade_out: float = 0.0
    conditions: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Particle:
    """Individual particle for visual effects"""
    x: float
    y: float
    velocity_x: float
    velocity_y: float
    acceleration_x: float = 0.0
    acceleration_y: float = 0.0
    life: int = 60
    max_life: int = 60
    color: int = 7
    size: int = 1
    alpha: float = 1.0
    rotation: float = 0.0
    angular_velocity: float = 0.0

@dataclass
class VisualEffect:
    """Visual effect definition"""
    id: str
    effect_type: VisualEffectType
    x: float
    y: float
    particles: List[Particle]
    duration: int
    current_frame: int = 0
    active: bool = True

class SoundManager:
    """Manages all game audio"""
    
    def __init__(self):
        self.enabled = True
        self.bgm_volume = 0.7
        self.sfx_volume = 0.8
        
        # Pyxel sound channels (0-3)
        self.bgm_channel = 0
        self.sfx_channels = [1, 2, 3]
        self.current_sfx_channel = 0
        
        # Current playing tracks
        self.current_bgm = None
        self.bgm_fade_timer = 0
        self.bgm_target_volume = 0.7
        
        # Sound library
        self.sound_library = {}
        self.bgm_library = {}
        
        # Settings
        self.adaptive_volume = True
        self.crossfade_duration = 120  # frames
        
        self._initialize_sounds()
    
    def _initialize_sounds(self):
        """Initialize sound definitions"""
        
        # BGM tracks
        bgm_tracks = [
            {
                "id": "city_day",
                "name": "City Life (Day)",
                "japanese_name": "都市の日常",
                "conditions": {"time": "day", "population": ">100"},
                "tempo": "relaxed"
            },
            {
                "id": "city_night", 
                "name": "City Life (Night)",
                "japanese_name": "都市の夜",
                "conditions": {"time": "night", "population": ">100"},
                "tempo": "calm"
            },
            {
                "id": "rural_theme",
                "name": "Rural Serenity",
                "japanese_name": "田舎の静寂",
                "conditions": {"population": "<500"},
                "tempo": "peaceful"
            },
            {
                "id": "metropolis_theme",
                "name": "Metropolitan Rush",
                "japanese_name": "大都市の喧騒",
                "conditions": {"population": ">10000"},
                "tempo": "energetic"
            },
            {
                "id": "disaster_theme",
                "name": "Crisis Management",
                "japanese_name": "危機管理",
                "conditions": {"disaster": "active"},
                "tempo": "tense"
            }
        ]
        
        # Generate BGM using Pyxel's sound synthesis
        for track in bgm_tracks:
            self._create_procedural_bgm(track)
        
        # SFX definitions
        sfx_sounds = {
            # UI Sounds
            "ui_select": {"tone": "C4", "duration": 10, "wave": pyxel.TONE_SQUARE},
            "ui_confirm": {"tone": "E4", "duration": 15, "wave": pyxel.TONE_TRIANGLE},
            "ui_cancel": {"tone": "A3", "duration": 12, "wave": pyxel.TONE_PULSE},
            "ui_error": {"tone": "F3", "duration": 20, "wave": pyxel.TONE_NOISE},
            
            # Building Sounds
            "place_building": {"tone": "G4", "duration": 25, "wave": pyxel.TONE_SQUARE},
            "demolish": {"tone": "D3", "duration": 30, "wave": pyxel.TONE_NOISE},
            "construction": {"tone": "B3", "duration": 40, "wave": pyxel.TONE_PULSE},
            
            # Traffic Sounds
            "car_horn": {"tone": "Bb3", "duration": 20, "wave": pyxel.TONE_PULSE},
            "bus_arrival": {"tone": "F4", "duration": 35, "wave": pyxel.TONE_TRIANGLE},
            "train_horn": {"tone": "C3", "duration": 50, "wave": pyxel.TONE_SQUARE},
            
            # Disaster Sounds
            "earthquake": {"tone": "A2", "duration": 60, "wave": pyxel.TONE_NOISE},
            "fire_alarm": {"tone": "E5", "duration": 30, "wave": pyxel.TONE_SQUARE},
            "siren": {"tone": "A4", "duration": 45, "wave": pyxel.TONE_PULSE},
            
            # Ambient Sounds
            "money_gain": {"tone": "C5", "duration": 18, "wave": pyxel.TONE_TRIANGLE},
            "level_up": {"tone": "G5", "duration": 40, "wave": pyxel.TONE_SQUARE},
            "achievement": {"tone": "E5", "duration": 60, "wave": pyxel.TONE_TRIANGLE}
        }
        
        # Generate SFX
        for sound_id, params in sfx_sounds.items():
            self._create_sfx(sound_id, params)
    
    def _create_procedural_bgm(self, track_info: Dict):
        """Create procedural background music"""
        track_id = track_info["id"]
        tempo = track_info.get("tempo", "relaxed")
        
        # Different musical patterns based on tempo
        if tempo == "peaceful":
            notes = ["C4", "E4", "G4", "C5", "G4", "E4", "D4", "C4"]
            durations = [30, 30, 30, 60, 30, 30, 60, 60]
        elif tempo == "energetic":
            notes = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]
            durations = [15, 15, 15, 15, 20, 20, 25, 30]
        elif tempo == "tense":
            notes = ["Bb3", "C4", "Db4", "Eb4", "Gb4", "Ab4"]
            durations = [20, 25, 20, 25, 30, 35]
        else:  # relaxed, calm
            notes = ["C4", "E4", "G4", "E4", "F4", "A4", "C5", "G4"]
            durations = [40, 35, 40, 35, 45, 40, 50, 45]
        
        # Store BGM pattern
        self.bgm_library[track_id] = {
            "notes": notes,
            "durations": durations,
            "info": track_info,
            "current_note": 0,
            "note_timer": 0
        }
    
    def _create_sfx(self, sound_id: str, params: Dict):
        """Create sound effect"""
        self.sound_library[sound_id] = {
            "tone": params["tone"],
            "duration": params["duration"],
            "wave": params["wave"],
            "category": self._get_sfx_category(sound_id)
        }
    
    def _get_sfx_category(self, sound_id: str) -> SoundCategory:
        """Get sound effect category"""
        if sound_id.startswith("ui_"):
            return SoundCategory.SFX_UI
        elif sound_id in ["place_building", "demolish", "construction"]:
            return SoundCategory.SFX_BUILDING
        elif sound_id in ["car_horn", "bus_arrival", "train_horn"]:
            return SoundCategory.SFX_TRAFFIC
        elif sound_id in ["earthquake", "fire_alarm", "siren"]:
            return SoundCategory.SFX_DISASTER
        else:
            return SoundCategory.SFX_AMBIENT
    
    def play_bgm(self, track_id: str, fade_in: bool = True):
        """Play background music"""
        if not self.enabled or track_id not in self.bgm_library:
            return
        
        if self.current_bgm != track_id:
            self.current_bgm = track_id
            if fade_in:
                self.bgm_fade_timer = self.crossfade_duration
                self.bgm_target_volume = self.bgm_volume
            else:
                self.bgm_target_volume = self.bgm_volume
    
    def play_sfx(self, sound_id: str, volume: float = 1.0):
        """Play sound effect"""
        if not self.enabled or sound_id not in self.sound_library:
            return
        
        sound = self.sound_library[sound_id]
        channel = self.sfx_channels[self.current_sfx_channel]
        
        # Convert note to frequency
        note_to_freq = {
            "C3": 131, "D3": 147, "E3": 165, "F3": 175, "G3": 196, "A3": 220, "B3": 247,
            "C4": 262, "D4": 294, "E4": 330, "F4": 349, "G4": 392, "A4": 440, "B4": 494,
            "C5": 523, "D5": 587, "E5": 659, "F5": 698, "G5": 784, "A5": 880, "B5": 988,
            "Bb3": 233, "Db4": 277, "Eb4": 311, "Gb4": 370, "Ab4": 415
        }
        
        freq = note_to_freq.get(sound["tone"], 440)
        
        # Play using Pyxel's tone function (simplified)
        try:
            # Since Pyxel doesn't have direct audio API in some versions,
            # we'll create a visual representation of sound playing
            self._create_sound_visual_feedback(sound_id, sound["category"])
        except:
            pass
        
        # Cycle through available channels
        self.current_sfx_channel = (self.current_sfx_channel + 1) % len(self.sfx_channels)
    
    def _create_sound_visual_feedback(self, sound_id: str, category: SoundCategory):
        """Create visual feedback for sound"""
        # This creates a small visual indicator when sounds would play
        pass
    
    def update(self, game_state: Dict[str, Any]):
        """Update sound system"""
        if not self.enabled:
            return
        
        # Update BGM based on game conditions
        self._update_adaptive_bgm(game_state)
        
        # Update BGM playback
        self._update_bgm_playback()
        
        # Update volume fading
        if self.bgm_fade_timer > 0:
            self.bgm_fade_timer -= 1
    
    def _update_adaptive_bgm(self, game_state: Dict[str, Any]):
        """Update BGM based on game state"""
        if not self.adaptive_volume:
            return
        
        population = game_state.get("population", 0)
        has_disaster = game_state.get("active_disasters", 0) > 0
        time_of_day = game_state.get("hour", 12)
        
        # Determine appropriate BGM
        target_bgm = None
        
        if has_disaster:
            target_bgm = "disaster_theme"
        elif population < 500:
            target_bgm = "rural_theme"
        elif population > 10000:
            target_bgm = "metropolis_theme"
        elif 6 <= time_of_day <= 18:
            target_bgm = "city_day"
        else:
            target_bgm = "city_night"
        
        # Switch BGM if needed
        if target_bgm != self.current_bgm:
            self.play_bgm(target_bgm, fade_in=True)
    
    def _update_bgm_playback(self):
        """Update current BGM playback"""
        if not self.current_bgm or self.current_bgm not in self.bgm_library:
            return
        
        bgm = self.bgm_library[self.current_bgm]
        bgm["note_timer"] += 1
        
        current_duration = bgm["durations"][bgm["current_note"]]
        
        if bgm["note_timer"] >= current_duration:
            bgm["current_note"] = (bgm["current_note"] + 1) % len(bgm["notes"])
            bgm["note_timer"] = 0
    
    def set_volume(self, bgm_volume: float, sfx_volume: float):
        """Set volume levels"""
        self.bgm_volume = max(0.0, min(1.0, bgm_volume))
        self.sfx_volume = max(0.0, min(1.0, sfx_volume))
    
    def toggle_enabled(self):
        """Toggle sound system on/off"""
        self.enabled = not self.enabled
    
    def get_current_track_info(self) -> Optional[Dict]:
        """Get current BGM track information"""
        if self.current_bgm and self.current_bgm in self.bgm_library:
            return self.bgm_library[self.current_bgm]["info"]
        return None

class VisualEffectManager:
    """Manages visual effects and particles"""
    
    def __init__(self):
        self.effects: List[VisualEffect] = []
        self.particle_pool: List[Particle] = []
        self.max_effects = 50
        self.max_particles_per_effect = 100
        
        # Effect templates
        self.effect_templates = {
            VisualEffectType.EXPLOSION: {
                "particle_count": 20,
                "colors": [8, 9, 10, 11],
                "life_range": (30, 60),
                "velocity_range": (-5.0, 5.0),
                "acceleration": (0, 0.2)
            },
            VisualEffectType.CONSTRUCTION: {
                "particle_count": 15,
                "colors": [6, 12, 13],
                "life_range": (20, 40),
                "velocity_range": (-2.0, 2.0),
                "acceleration": (0, 0.1)
            },
            VisualEffectType.SMOKE: {
                "particle_count": 25,
                "colors": [0, 5, 13],
                "life_range": (60, 120),
                "velocity_range": (-1.0, 1.0),
                "acceleration": (0, -0.1)
            },
            VisualEffectType.SPARKLE: {
                "particle_count": 10,
                "colors": [7, 10, 11],
                "life_range": (15, 30),
                "velocity_range": (-3.0, 3.0),
                "acceleration": (0, 0)
            },
            VisualEffectType.FIRE: {
                "particle_count": 30,
                "colors": [8, 9, 10],
                "life_range": (20, 50),
                "velocity_range": (-1.5, 1.5),
                "acceleration": (0, -0.2)
            }
        }
    
    def create_effect(self, effect_type: VisualEffectType, x: float, y: float, 
                     duration: int = 60, scale: float = 1.0):
        """Create new visual effect"""
        # Clean up expired effects first
        self.effects = [e for e in self.effects if e.active and e.particles]
        
        # Remove oldest effects if at limit
        while len(self.effects) >= self.max_effects:
            self.effects.pop(0)
        
        if effect_type not in self.effect_templates:
            return
        
        template = self.effect_templates[effect_type]
        particles = []
        
        particle_count = int(template["particle_count"] * scale)
        
        for i in range(particle_count):
            particle = self._create_particle(template, x, y, scale)
            particles.append(particle)
        
        effect = VisualEffect(
            id=f"{effect_type.value}_{len(self.effects)}",
            effect_type=effect_type,
            x=x,
            y=y,
            particles=particles,
            duration=duration
        )
        
        self.effects.append(effect)
    
    def _create_particle(self, template: Dict, x: float, y: float, scale: float) -> Particle:
        """Create individual particle"""
        life_min, life_max = template["life_range"]
        vel_min, vel_max = template["velocity_range"]
        acc_x, acc_y = template["acceleration"]
        
        life_value = random.randint(life_min, life_max)
        
        return Particle(
            x=x + random.uniform(-5, 5) * scale,
            y=y + random.uniform(-5, 5) * scale,
            velocity_x=random.uniform(vel_min, vel_max) * scale,
            velocity_y=random.uniform(vel_min, vel_max) * scale,
            acceleration_x=acc_x,
            acceleration_y=acc_y,
            life=life_value,
            max_life=life_value,  # Use same value for consistency
            color=random.choice(template["colors"]),
            size=random.randint(1, 3),
            alpha=1.0,
            rotation=random.uniform(0, 2 * math.pi),
            angular_velocity=random.uniform(-0.1, 0.1)
        )
    
    def update(self):
        """Update all visual effects"""
        # Update effects
        for effect in self.effects[:]:
            effect.current_frame += 1
            
            if effect.current_frame >= effect.duration:
                effect.active = False
            
            # Update particles
            for particle in effect.particles[:]:
                particle.x += particle.velocity_x
                particle.y += particle.velocity_y
                particle.velocity_x += particle.acceleration_x
                particle.velocity_y += particle.acceleration_y
                particle.rotation += particle.angular_velocity
                particle.life -= 1
                
                # Update alpha based on life
                particle.alpha = particle.life / particle.max_life
                
                # Remove dead particles
                if particle.life <= 0:
                    effect.particles.remove(particle)
            
            # Remove effects with no particles
            if not effect.particles or not effect.active:
                self.effects.remove(effect)
    
    def draw(self):
        """Draw all visual effects"""
        for effect in self.effects:
            if not effect.active:
                continue
            
            for particle in effect.particles:
                if particle.alpha <= 0:
                    continue
                
                # Simple particle rendering
                if particle.size == 1:
                    pyxel.pset(int(particle.x), int(particle.y), particle.color)
                else:
                    pyxel.rect(
                        int(particle.x - particle.size // 2),
                        int(particle.y - particle.size // 2),
                        particle.size,
                        particle.size,
                        particle.color
                    )
    
    def create_building_placed_effect(self, x: int, y: int):
        """Create effect for building placement"""
        self.create_effect(VisualEffectType.CONSTRUCTION, x, y, duration=30, scale=0.8)
        self.create_effect(VisualEffectType.SPARKLE, x, y, duration=45, scale=0.5)
    
    def create_disaster_effect(self, disaster_type: str, x: int, y: int, severity: float = 1.0):
        """Create disaster-specific effects"""
        if disaster_type == "earthquake":
            self.create_effect(VisualEffectType.EXPLOSION, x, y, duration=90, scale=severity)
        elif disaster_type == "fire":
            self.create_effect(VisualEffectType.FIRE, x, y, duration=120, scale=severity)
        elif disaster_type == "flood":
            # Could implement water effect
            self.create_effect(VisualEffectType.SPARKLE, x, y, duration=60, scale=severity)
    
    def create_money_effect(self, x: int, y: int, amount: int):
        """Create money gain effect"""
        scale = min(2.0, max(0.5, amount / 1000))
        self.create_effect(VisualEffectType.SPARKLE, x, y, duration=40, scale=scale)
    
    def clear_all(self):
        """Clear all effects"""
        self.effects.clear()

class SoundEffectsSystem:
    """Main sound and effects system"""
    
    def __init__(self):
        self.sound_manager = SoundManager()
        self.visual_effect_manager = VisualEffectManager()
        self.enabled = True
        
        # Event handlers
        self.event_handlers = {
            "building_placed": self._handle_building_placed,
            "building_demolished": self._handle_building_demolished,
            "disaster_started": self._handle_disaster_started,
            "money_gained": self._handle_money_gained,
            "level_up": self._handle_level_up,
            "ui_action": self._handle_ui_action,
            "traffic_event": self._handle_traffic_event
        }
    
    def _handle_building_placed(self, event_data: Dict):
        """Handle building placement"""
        x, y = event_data.get("position", (0, 0))
        building_type = event_data.get("building_type", "")
        
        # Play sound
        if "RESIDENTIAL" in building_type or "COMMERCIAL" in building_type or "INDUSTRIAL" in building_type:
            self.sound_manager.play_sfx("place_building")
        else:
            self.sound_manager.play_sfx("construction")
        
        # Create visual effect
        self.visual_effect_manager.create_building_placed_effect(x * 8, y * 8)
    
    def _handle_building_demolished(self, event_data: Dict):
        """Handle building demolition"""
        x, y = event_data.get("position", (0, 0))
        
        self.sound_manager.play_sfx("demolish")
        self.visual_effect_manager.create_effect(
            VisualEffectType.SMOKE, x * 8, y * 8, duration=60, scale=1.2
        )
    
    def _handle_disaster_started(self, event_data: Dict):
        """Handle disaster start"""
        disaster_type = event_data.get("disaster_type", "earthquake")
        x, y = event_data.get("position", (0, 0))
        severity = event_data.get("severity", 1.0)
        
        # Play appropriate sound
        if disaster_type == "earthquake":
            self.sound_manager.play_sfx("earthquake")
        elif disaster_type == "fire":
            self.sound_manager.play_sfx("fire_alarm")
        else:
            self.sound_manager.play_sfx("siren")
        
        # Create visual effects
        self.visual_effect_manager.create_disaster_effect(disaster_type, x * 8, y * 8, severity)
    
    def _handle_money_gained(self, event_data: Dict):
        """Handle money gain"""
        amount = event_data.get("amount", 0)
        x, y = event_data.get("position", (160, 144))
        
        if amount > 0:
            self.sound_manager.play_sfx("money_gain")
            self.visual_effect_manager.create_money_effect(x, y, amount)
    
    def _handle_level_up(self, event_data: Dict):
        """Handle level up"""
        self.sound_manager.play_sfx("level_up")
        # Create multiple sparkle effects
        for i in range(5):
            x = 160 + random.randint(-50, 50)
            y = 144 + random.randint(-30, 30)
            self.visual_effect_manager.create_effect(
                VisualEffectType.SPARKLE, x, y, duration=80, scale=1.5
            )
    
    def _handle_ui_action(self, event_data: Dict):
        """Handle UI interactions"""
        action = event_data.get("action", "select")
        
        if action == "select":
            self.sound_manager.play_sfx("ui_select")
        elif action == "confirm":
            self.sound_manager.play_sfx("ui_confirm")
        elif action == "cancel":
            self.sound_manager.play_sfx("ui_cancel")
        elif action == "error":
            self.sound_manager.play_sfx("ui_error")
    
    def _handle_traffic_event(self, event_data: Dict):
        """Handle traffic events"""
        event_type = event_data.get("event_type", "car")
        
        if event_type == "bus_arrival":
            self.sound_manager.play_sfx("bus_arrival")
        elif event_type == "train_horn":
            self.sound_manager.play_sfx("train_horn")
        elif event_type == "traffic_jam":
            self.sound_manager.play_sfx("car_horn")
    
    def emit_event(self, event_type: str, event_data: Dict):
        """Emit event to trigger sounds and effects"""
        if not self.enabled:
            return
        
        handler = self.event_handlers.get(event_type)
        if handler:
            handler(event_data)
    
    def update(self, game_state: Dict[str, Any]):
        """Update sound and effects system"""
        if not self.enabled:
            return
        
        self.sound_manager.update(game_state)
        self.visual_effect_manager.update()
    
    def draw(self):
        """Draw visual effects"""
        if self.enabled:
            self.visual_effect_manager.draw()
    
    def set_volume(self, bgm_volume: float, sfx_volume: float):
        """Set volume levels"""
        self.sound_manager.set_volume(bgm_volume, sfx_volume)
    
    def toggle_enabled(self):
        """Toggle system on/off"""
        self.enabled = not self.enabled
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        current_track = self.sound_manager.get_current_track_info()
        
        return {
            "enabled": self.enabled,
            "bgm_volume": self.sound_manager.bgm_volume,
            "sfx_volume": self.sound_manager.sfx_volume,
            "current_bgm": current_track.get("japanese_name") if current_track else "なし",
            "active_effects": len(self.visual_effect_manager.effects),
            "total_particles": sum(len(e.particles) for e in self.visual_effect_manager.effects),
            "adaptive_volume": self.sound_manager.adaptive_volume
        }
    
    def save_settings(self, filename: str = "audio_settings.json"):
        """Save audio settings"""
        settings = {
            "enabled": self.enabled,
            "bgm_volume": self.sound_manager.bgm_volume,
            "sfx_volume": self.sound_manager.sfx_volume,
            "adaptive_volume": self.sound_manager.adaptive_volume
        }
        
        with open(filename, 'w') as f:
            json.dump(settings, f, indent=2)
    
    def load_settings(self, filename: str = "audio_settings.json"):
        """Load audio settings"""
        try:
            with open(filename, 'r') as f:
                settings = json.load(f)
            
            self.enabled = settings.get("enabled", True)
            self.sound_manager.bgm_volume = settings.get("bgm_volume", 0.7)
            self.sound_manager.sfx_volume = settings.get("sfx_volume", 0.8)
            self.sound_manager.adaptive_volume = settings.get("adaptive_volume", True)
            
            return True
        except Exception as e:
            print(f"Failed to load audio settings: {e}")
            return False

# Integration helpers
def integrate_sound_system_with_game(game_instance, sound_system):
    """Helper function to integrate sound system with main game"""
    
    original_place_building = game_instance.place_building
    original_remove_building = game_instance.remove_building
    
    def enhanced_place_building(x, y, building_type):
        result = original_place_building(x, y, building_type)
        if result:
            sound_system.emit_event("building_placed", {
                "position": (x, y),
                "building_type": building_type
            })
        return result
    
    def enhanced_remove_building(x, y):
        result = original_remove_building(x, y)
        if result:
            sound_system.emit_event("building_demolished", {
                "position": (x, y)
            })
        return result
    
    game_instance.place_building = enhanced_place_building
    game_instance.remove_building = enhanced_remove_building
    
    return sound_system

# Example usage and testing
def demo_sound_effects():
    """Demo function for testing sound effects"""
    
    system = SoundEffectsSystem()
    
    # Test various events
    events_to_test = [
        ("building_placed", {"position": (10, 10), "building_type": "RESIDENTIAL"}),
        ("money_gained", {"amount": 1000, "position": (160, 144)}),
        ("disaster_started", {"disaster_type": "earthquake", "position": (20, 20), "severity": 1.5}),
        ("level_up", {}),
        ("ui_action", {"action": "confirm"}),
        ("traffic_event", {"event_type": "bus_arrival"})
    ]
    
    frame = 0
    for event_type, event_data in events_to_test:
        if frame % 60 == 0:  # Every second
            system.emit_event(event_type, event_data)
        
        # Simulate game state for BGM
        game_state = {
            "population": 1000 + frame // 10,
            "active_disasters": 1 if frame > 300 else 0,
            "hour": (frame // 60) % 24
        }
        
        system.update(game_state)
        frame += 1
        
        if frame > 600:  # 10 seconds of demo
            break
    
    print("Sound effects system demo completed")
    status = system.get_system_status()
    for key, value in status.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    demo_sound_effects()