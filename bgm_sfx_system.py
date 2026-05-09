"""
BGM and SFX System for ConcLand
Provides music playback, sound effects, and audio management
"""
import random
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue

# Note: This is a placeholder implementation
# Actual audio would require Pyxel's sound system or external libraries

class SoundType(Enum):
    """Types of sounds"""
    MUSIC = "music"
    SFX = "sfx"
    AMBIENT = "ambient"

class MusicTrack(Enum):
    """Background music tracks"""
    TITLE = "title"
    GAMEPLAY = "gameplay"
    MENU = "menu"
    DISASTER = "disaster"
    ACHIEVEMENT = "achievement"
    VICTORY = "victory"

class SoundEffect(Enum):
    """Sound effects"""
    # Building sounds
    BUILD_RESIDENTIAL = "build_residential"
    BUILD_COMMERCIAL = "build_commercial"
    BUILD_INDUSTRIAL = "build_industrial"
    BUILD_ROAD = "build_road"
    BUILD_RAIL = "build_rail"
    BULLDOZE = "bulldoze"

    # UI sounds
    CURSOR_MOVE = "cursor_move"
    MENU_SELECT = "menu_select"
    MENU_CONFIRM = "menu_confirm"
    MENU_CANCEL = "menu_cancel"
    NOTIFICATION = "notification"
    ACHIEVEMENT_UNLOCK = "achievement_unlock"

    # Game sounds
    MONEY_COLLECT = "money_collect"
    MONEY_SPEND = "money_spend"
    DISASTER_START = "disaster_start"
    DISASTER_END = "disaster_end"
    FIRE_ALERT = "fire_alert"
    POLICE_SIREN = "police_siren"

    # Traffic
    CAR_PASS = "car_pass"
    TRAIN_PASS = "train_pass"
    AIRPLANE_FLY = "airplane_fly"

@dataclass
class SoundEvent:
    """Scheduled sound event"""
    sound_type: SoundEffect
    volume: float = 1.0
    pitch: float = 1.0
    pan: float = 0.5  # 0.0 = left, 1.0 = right
    priority: int = 0  # Higher = more important

class AudioConfig:
    """Audio configuration"""
    def __init__(self):
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.ambient_volume = 0.5
        self.master_volume = 1.0
        self.music_enabled = True
        self.sfx_enabled = True
        self.ambient_enabled = True

class PlaceholderSound:
    """Placeholder for actual sound implementation"""
    def __init__(self, name: str, duration: float = 0.1):
        self.name = name
        self.duration = duration
        self.playing = False

    def play(self, volume: float = 1.0):
        """Simulate playing sound"""
        self.playing = True
        # In real implementation, would play actual audio
        # print(f"[SOUND] Playing {self.name} at volume {volume}")

    def stop(self):
        """Stop playing sound"""
        self.playing = False

class SoundManager:
    """Manages sound effects playback"""
    def __init__(self, config: AudioConfig):
        self.config = config
        self.sounds: Dict[SoundEffect, PlaceholderSound] = {}
        self.sound_queue: queue.Queue = queue.Queue()
        self.max_concurrent_sounds = 8
        self.active_sounds: List[PlaceholderSound] = []

        # Initialize placeholder sounds
        self._init_sounds()

        # Sound statistics
        self.sfx_played_count = 0
        self.sfx_total_count = 0

    def _init_sounds(self):
        """Initialize placeholder sounds"""
        # Create placeholder sounds for all effects
        for sfx in SoundEffect:
            duration = random.uniform(0.1, 0.5)
            self.sounds[sfx] = PlaceholderSound(sfx.value, duration)

    def play(self, sound: SoundEffect, volume: float = 1.0, pitch: float = 1.0,
             pan: float = 0.5, priority: int = 0):
        """Play a sound effect"""
        if not self.config.sfx_enabled or not self.config.sfx_enabled:
            return False

        # Check if sound exists
        if sound not in self.sounds:
            return False

        # Calculate final volume
        final_volume = volume * self.config.sfx_volume * self.config.master_volume
        if final_volume <= 0:
            return False

        # Manage concurrent sounds
        if len(self.active_sounds) >= self.max_concurrent_sounds:
            # Remove lowest priority sound
            self.active_sounds.sort(key=lambda s: 0, reverse=True)
            if self.active_sounds:
                self.active_sounds.pop().stop()

        # Play sound
        sound_obj = self.sounds[sound]
        sound_obj.play(final_volume)
        self.active_sounds.append(sound_obj)

        # Update statistics
        self.sfx_played_count += 1
        self.sfx_total_count += 1

        return True

    def play_random(self, sounds: List[SoundEffect], volume: float = 1.0):
        """Play a random sound from list"""
        if sounds:
            sound = random.choice(sounds)
            return self.play(sound, volume)
        return False

    def update(self, dt: float):
        """Update sound manager"""
        # Clean up finished sounds
        self.active_sounds = [s for s in self.active_sounds if s.playing]

    def get_statistics(self) -> Dict[str, int]:
        """Get sound statistics"""
        return {
            "active_sounds": len(self.active_sounds),
            "total_played": self.sfx_total_count,
            "currently_playing": self.sfx_played_count
        }

class MusicManager:
    """Manages background music playback"""
    def __init__(self, config: AudioConfig):
        self.config = config
        self.current_track: Optional[MusicTrack] = None
        self.track_position: float = 0.0  # Seconds
        self.is_playing = False
        self.is_paused = False
        self.fade_volume = 0.0
        self.target_volume = 0.0
        self.fade_speed = 0.01

        # Track durations (placeholder)
        self.track_durations = {
            MusicTrack.TITLE: 120.0,      # 2 minutes
            MusicTrack.GAMEPLAY: 180.0,   # 3 minutes
            MusicTrack.MENU: 90.0,        # 1.5 minutes
            MusicTrack.DISASTER: 60.0,    # 1 minute
            MusicTrack.ACHIEVEMENT: 30.0, # 30 seconds
            MusicTrack.VICTORY: 45.0      # 45 seconds
        }

    def play(self, track: MusicTrack, fade_in: bool = True):
        """Play a music track"""
        if not self.config.music_enabled:
            return

        self.current_track = track
        self.track_position = 0.0
        self.is_playing = True
        self.is_paused = False

        if fade_in:
            self.fade_volume = 0.0
            self.target_volume = self.config.music_volume
        else:
            self.fade_volume = self.config.music_volume
            self.target_volume = self.config.music_volume

    def stop(self, fade_out: bool = True):
        """Stop current track"""
        if fade_out:
            self.target_volume = 0.0
        else:
            self.is_playing = False
            self.current_track = None

    def pause(self):
        """Pause current track"""
        if self.is_playing:
            self.is_paused = True

    def resume(self):
        """Resume paused track"""
        if self.is_paused:
            self.is_paused = False

    def set_volume(self, volume: float):
        """Set music volume"""
        self.config.music_volume = max(0.0, min(1.0, volume))
        if self.is_playing:
            self.target_volume = self.config.music_volume

    def update(self, dt: float):
        """Update music manager"""
        if not self.is_playing or self.is_paused:
            return

        # Update track position
        self.track_position += dt

        # Check for track end
        if self.current_track:
            duration = self.track_durations.get(self.current_track, 120.0)
            if self.track_position >= duration:
                # Loop track
                self.track_position = 0.0

        # Update fade
        if self.fade_volume < self.target_volume:
            self.fade_volume = min(self.target_volume, self.fade_volume + self.fade_speed)
        elif self.fade_volume > self.target_volume:
            self.fade_volume = max(self.target_volume, self.fade_volume - self.fade_speed)

        # Stop if fade out complete
        if self.target_volume == 0.0 and self.fade_volume <= 0.01:
            self.is_playing = False

    def get_status(self) -> Dict[str, any]:
        """Get music status"""
        status = {
            "is_playing": self.is_playing,
            "is_paused": self.is_paused,
            "current_track": self.current_track.value if self.current_track else None,
            "position": self.track_position,
            "volume": self.fade_volume
        }

        if self.current_track:
            duration = self.track_durations.get(self.current_track, 120.0)
            status["duration"] = duration
            status["progress"] = self.track_position / duration if duration > 0 else 0.0

        return status

class AmbientSystem:
    """Manages ambient sounds"""
    def __init__(self, config: AudioConfig):
        self.config = config
        self.ambient_sounds: Dict[str, PlaceholderSound] = {}
        self.active_ambients: List[str] = []

        # Initialize ambient sounds
        self._init_ambients()

    def _init_ambients(self):
        """Initialize ambient sounds"""
        ambient_types = ["city", "nature", "water", "industrial"]
        for ambient in ambient_types:
            self.ambient_sounds[ambient] = PlaceholderSound(f"ambient_{ambient}", 999.0)

    def play(self, ambient_type: str, volume: float = 1.0):
        """Play ambient sound"""
        if not self.config.ambient_enabled:
            return

        if ambient_type in self.ambient_sounds and ambient_type not in self.active_ambients:
            final_volume = volume * self.config.ambient_volume * self.config.master_volume
            self.ambient_sounds[ambient_type].play(final_volume)
            self.active_ambients.append(ambient_type)

    def stop(self, ambient_type: str):
        """Stop ambient sound"""
        if ambient_type in self.active_ambients:
            self.ambient_sounds[ambient_type].stop()
            self.active_ambients.remove(ambient_type)

    def stop_all(self):
        """Stop all ambient sounds"""
        for ambient in list(self.active_ambients):
            self.stop(ambient)

class AudioSystem:
    """Main audio system combining all audio components"""
    def __init__(self):
        self.config = AudioConfig()
        self.sound_manager = SoundManager(self.config)
        self.music_manager = MusicManager(self.config)
        self.ambient_system = AmbientSystem(self.config)

        # System state
        self.is_initialized = False
        self.dt = 0.016  # 60 FPS

        # Audio hooks for game events
        self.hooks = {
            "building_placed": self._on_building_placed,
            "building_bulldozed": self._on_building_bulldozed,
            "menu_navigate": self._on_menu_navigate,
            "menu_select": self._on_menu_select,
            "notification": self._on_notification,
            "achievement": self._on_achievement,
            "disaster_start": self._on_disaster_start,
            "money_change": self._on_money_change
        }

    def initialize(self):
        """Initialize audio system"""
        # In real implementation, would initialize audio hardware
        self.is_initialized = True

    def shutdown(self):
        """Shutdown audio system"""
        self.music_manager.stop(fade_out=False)
        self.ambient_system.stop_all()

    def update(self, dt: float = None):
        """Update all audio components"""
        if dt:
            self.dt = dt

        if not self.is_initialized:
            return

        self.sound_manager.update(self.dt)
        self.music_manager.update(self.dt)

    # Audio hooks
    def _on_building_placed(self, building_type: str):
        """Handle building placement sound"""
        building_sounds = {
            "residential": SoundEffect.BUILD_RESIDENTIAL,
            "commercial": SoundEffect.BUILD_COMMERCIAL,
            "industrial": SoundEffect.BUILD_INDUSTRIAL,
            "road": SoundEffect.BUILD_ROAD,
            "rail": SoundEffect.BUILD_RAIL
        }
        sound = building_sounds.get(building_type, SoundEffect.BUILD_RESIDENTIAL)
        self.sound_manager.play(sound)

    def _on_building_bulldozed(self):
        """Handle bulldoze sound"""
        self.sound_manager.play(SoundEffect.BULLDOZE)

    def _on_menu_navigate(self):
        """Handle menu navigation sound"""
        self.sound_manager.play(SoundEffect.CURSOR_MOVE, volume=0.5)

    def _on_menu_select(self):
        """Handle menu selection sound"""
        self.sound_manager.play(SoundEffect.MENU_CONFIRM)

    def _on_notification(self):
        """Handle notification sound"""
        self.sound_manager.play(SoundEffect.NOTIFICATION)

    def _on_achievement(self):
        """Handle achievement unlock sound"""
        self.music_manager.play(MusicTrack.ACHIEVEMENT)
        self.sound_manager.play(SoundEffect.ACHIEVEMENT_UNLOCK)

    def _on_disaster_start(self, disaster_type: str):
        """Handle disaster start sound"""
        self.music_manager.play(MusicTrack.DISASTER)
        self.sound_manager.play(SoundEffect.DISASTER_START)

    def _on_money_change(self, amount: int):
        """Handle money change sound"""
        if amount > 0:
            self.sound_manager.play(SoundEffect.MONEY_COLLECT)
        else:
            self.sound_manager.play(SoundEffect.MONEY_SPEND, volume=0.7)

    # Public API
    def trigger_hook(self, hook_name: str, *args, **kwargs):
        """Trigger an audio hook"""
        if hook_name in self.hooks:
            self.hooks[hook_name](*args, **kwargs)

    def play_music(self, track: MusicTrack):
        """Play music track"""
        self.music_manager.play(track)

    def play_sfx(self, sound: SoundEffect, **kwargs):
        """Play sound effect"""
        return self.sound_manager.play(sound, **kwargs)

    def set_music_volume(self, volume: float):
        """Set music volume"""
        self.music_manager.set_volume(volume)

    def set_sfx_volume(self, volume: float):
        """Set SFX volume"""
        self.config.sfx_volume = max(0.0, min(1.0, volume))

    def set_master_volume(self, volume: float):
        """Set master volume"""
        self.config.master_volume = max(0.0, min(1.0, volume))

    def get_system_status(self) -> Dict[str, any]:
        """Get status of all audio systems"""
        return {
            "config": {
                "music_volume": self.config.music_volume,
                "sfx_volume": self.config.sfx_volume,
                "ambient_volume": self.config.ambient_volume,
                "master_volume": self.config.master_volume,
                "music_enabled": self.config.music_enabled,
                "sfx_enabled": self.config.sfx_enabled,
                "ambient_enabled": self.config.ambient_enabled
            },
            "music": self.music_manager.get_status(),
            "sfx": self.sound_manager.get_statistics(),
            "ambient": {
                "active": self.ambient_system.active_ambients
            }
        }

# Example usage
if __name__ == "__main__":
    # Create audio system
    audio = AudioSystem()
    audio.initialize()

    # Simulate game events
    print("=== Audio System Test ===")

    # Play title music
    audio.play_music(MusicTrack.TITLE)
    print(f"Music: {audio.music_manager.get_status()}")

    # Simulate building placement
    audio.trigger_hook("building_placed", "residential")
    audio.trigger_hook("money_change", -100)

    # Update system
    for i in range(10):
        audio.update(0.016)

    print(f"SFX Stats: {audio.sound_manager.get_statistics()}")
    print(f"System Status: {audio.get_system_status()}")

    # Cleanup
    audio.shutdown()
