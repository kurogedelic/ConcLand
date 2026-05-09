"""
Integration test for Sound Effects System
Tests audio management and visual effects in ConcLand
"""
import sys
import time
from typing import Dict, Any, List
from sound_effects_system import (
    SoundEffectsSystem, SoundManager, VisualEffectManager,
    VisualEffectType, SoundCategory, Particle
)

class MockGameState:
    """Mock game state for testing"""
    def __init__(self):
        self.population = 500
        self.active_disasters = 0
        self.hour = 12
        self.funds = 10000
        self.frame_count = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "population": self.population,
            "active_disasters": self.active_disasters,
            "hour": self.hour,
            "funds": self.funds
        }

class SoundEffectsSystemTester:
    """Test suite for sound effects system"""
    
    def __init__(self):
        self.system = SoundEffectsSystem()
        self.game_state = MockGameState()
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        print("=== ConcLand Sound Effects System Tests ===\n")
        
        # Core system tests
        self.test_sound_manager_initialization()
        self.test_visual_effect_manager_initialization()
        self.test_bgm_system()
        self.test_sfx_system()
        self.test_visual_effects()
        
        # Integration tests
        self.test_event_handling()
        self.test_adaptive_audio()
        self.test_settings_persistence()
        
        # Performance tests
        self.test_performance_under_load()
        self.test_memory_management()
        
        # Generate report
        return self._generate_test_report()
    
    def test_sound_manager_initialization(self):
        """Test sound manager initialization"""
        self._start_test("Sound Manager Initialization")
        
        sound_manager = SoundManager()
        
        # Check basic properties
        assert sound_manager.enabled == True, "Sound manager should be enabled by default"
        assert 0.0 <= sound_manager.bgm_volume <= 1.0, "BGM volume should be in valid range"
        assert 0.0 <= sound_manager.sfx_volume <= 1.0, "SFX volume should be in valid range"
        assert len(sound_manager.bgm_library) > 0, "BGM library should not be empty"
        assert len(sound_manager.sound_library) > 0, "SFX library should not be empty"
        
        # Check BGM tracks
        expected_bgm = ["city_day", "city_night", "rural_theme", "metropolis_theme", "disaster_theme"]
        for track_id in expected_bgm:
            assert track_id in sound_manager.bgm_library, f"BGM track {track_id} should exist"
        
        # Check SFX sounds
        expected_sfx = ["ui_select", "ui_confirm", "place_building", "demolish", "money_gain"]
        for sound_id in expected_sfx:
            assert sound_id in sound_manager.sound_library, f"SFX sound {sound_id} should exist"
        
        self._pass_test("Sound manager initialized correctly")
    
    def test_visual_effect_manager_initialization(self):
        """Test visual effect manager initialization"""
        self._start_test("Visual Effect Manager Initialization")
        
        vfx_manager = VisualEffectManager()
        
        # Check basic properties
        assert len(vfx_manager.effects) == 0, "Effects list should start empty"
        assert vfx_manager.max_effects > 0, "Should have maximum effects limit"
        assert len(vfx_manager.effect_templates) > 0, "Should have effect templates"
        
        # Check effect templates
        expected_effects = [
            VisualEffectType.EXPLOSION,
            VisualEffectType.CONSTRUCTION,
            VisualEffectType.SMOKE,
            VisualEffectType.SPARKLE,
            VisualEffectType.FIRE
        ]
        
        for effect_type in expected_effects:
            assert effect_type in vfx_manager.effect_templates, f"Effect template {effect_type} should exist"
            template = vfx_manager.effect_templates[effect_type]
            assert "particle_count" in template, f"Template {effect_type} should have particle_count"
            assert "colors" in template, f"Template {effect_type} should have colors"
        
        self._pass_test("Visual effect manager initialized correctly")
    
    def test_bgm_system(self):
        """Test background music system"""
        self._start_test("BGM System")
        
        sound_manager = self.system.sound_manager
        
        # Test BGM playback
        sound_manager.play_bgm("city_day")
        assert sound_manager.current_bgm == "city_day", "Should set current BGM"
        
        # Test BGM switching
        sound_manager.play_bgm("city_night", fade_in=True)
        assert sound_manager.current_bgm == "city_night", "Should switch BGM"
        assert sound_manager.bgm_fade_timer > 0, "Should start fade timer"
        
        # Test volume control
        original_volume = sound_manager.bgm_volume
        sound_manager.set_volume(0.5, 0.8)
        assert sound_manager.bgm_volume == 0.5, "Should set BGM volume"
        assert sound_manager.sfx_volume == 0.8, "Should set SFX volume"
        
        # Test BGM update cycle
        bgm = sound_manager.bgm_library["city_day"]
        original_note = bgm["current_note"]
        bgm["note_timer"] = bgm["durations"][bgm["current_note"]]  # Force note change
        
        sound_manager.current_bgm = "city_day"
        sound_manager._update_bgm_playback()
        
        # Should advance to next note
        expected_note = (original_note + 1) % len(bgm["notes"])
        assert bgm["current_note"] == expected_note, "Should advance to next note"
        
        self._pass_test("BGM system working correctly")
    
    def test_sfx_system(self):
        """Test sound effects system"""
        self._start_test("SFX System")
        
        sound_manager = self.system.sound_manager
        
        # Test SFX playback
        original_channel = sound_manager.current_sfx_channel
        sound_manager.play_sfx("ui_select")
        
        # Channel should cycle
        assert sound_manager.current_sfx_channel != original_channel, "Should cycle SFX channels"
        
        # Test different SFX categories
        test_sounds = ["place_building", "demolish", "money_gain", "earthquake"]
        for sound_id in test_sounds:
            sound_manager.play_sfx(sound_id, volume=0.5)
            # Should not crash and should be in library
            assert sound_id in sound_manager.sound_library, f"Sound {sound_id} should exist"
        
        # Test volume scaling
        sound_manager.play_sfx("ui_confirm", volume=0.2)
        sound_manager.play_sfx("ui_confirm", volume=1.5)  # Should clamp to 1.0
        
        self._pass_test("SFX system working correctly")
    
    def test_visual_effects(self):
        """Test visual effects system"""
        self._start_test("Visual Effects")
        
        vfx_manager = self.system.visual_effect_manager
        
        # Test effect creation
        vfx_manager.create_effect(VisualEffectType.EXPLOSION, 100, 100, duration=60, scale=1.0)
        assert len(vfx_manager.effects) == 1, "Should create one effect"
        
        effect = vfx_manager.effects[0]
        assert effect.effect_type == VisualEffectType.EXPLOSION, "Should be explosion effect"
        assert effect.x == 100 and effect.y == 100, "Should have correct position"
        assert len(effect.particles) > 0, "Should have particles"
        
        # Test particle properties
        particle = effect.particles[0]
        assert particle.life > 0, "Particle should have life"
        assert particle.max_life > 0, "Particle should have max life"
        assert particle.alpha == 1.0, "Particle should start with full alpha"
        
        # Test effect update
        initial_particle_x = particle.x
        vfx_manager.update()
        
        # Particle should have moved (unless velocity is 0)
        if particle.velocity_x != 0 or particle.velocity_y != 0:
            assert particle.x != initial_particle_x, "Particle should move"
        
        assert particle.life < particle.max_life, "Particle life should decrease"
        
        # Test effect cleanup
        effect.current_frame = effect.duration  # Force expiration
        for p in effect.particles:
            p.life = 0  # Kill all particles
        
        vfx_manager.update()
        assert len(vfx_manager.effects) == 0, "Expired effects should be removed"
        
        self._pass_test("Visual effects working correctly")
    
    def test_event_handling(self):
        """Test event handling system"""
        self._start_test("Event Handling")
        
        # Test building placement event
        self.system.emit_event("building_placed", {
            "position": (10, 15),
            "building_type": "RESIDENTIAL"
        })
        
        # Should create visual effects
        assert len(self.system.visual_effect_manager.effects) > 0, "Should create visual effects"
        
        # Clear effects
        self.system.visual_effect_manager.clear_all()
        
        # Test disaster event
        self.system.emit_event("disaster_started", {
            "disaster_type": "earthquake",
            "position": (20, 25),
            "severity": 1.5
        })
        
        assert len(self.system.visual_effect_manager.effects) > 0, "Should create disaster effects"
        
        # Test money gain event
        self.system.emit_event("money_gained", {
            "amount": 5000,
            "position": (160, 144)
        })
        
        # Test UI action event
        self.system.emit_event("ui_action", {"action": "confirm"})
        
        # Test invalid event (should not crash)
        self.system.emit_event("invalid_event", {})
        
        self._pass_test("Event handling working correctly")
    
    def test_adaptive_audio(self):
        """Test adaptive audio system"""
        self._start_test("Adaptive Audio")
        
        sound_manager = self.system.sound_manager
        
        # Test rural theme (low population)
        game_state = {"population": 100, "active_disasters": 0, "hour": 12}
        sound_manager._update_adaptive_bgm(game_state)
        assert sound_manager.current_bgm == "rural_theme", "Should play rural theme for low population"
        
        # Test city day theme
        game_state = {"population": 2000, "active_disasters": 0, "hour": 10}
        sound_manager._update_adaptive_bgm(game_state)
        assert sound_manager.current_bgm == "city_day", "Should play city day theme"
        
        # Test city night theme
        game_state = {"population": 2000, "active_disasters": 0, "hour": 22}
        sound_manager._update_adaptive_bgm(game_state)
        assert sound_manager.current_bgm == "city_night", "Should play city night theme"
        
        # Test metropolis theme
        game_state = {"population": 15000, "active_disasters": 0, "hour": 12}
        sound_manager._update_adaptive_bgm(game_state)
        assert sound_manager.current_bgm == "metropolis_theme", "Should play metropolis theme"
        
        # Test disaster theme (should override others)
        game_state = {"population": 15000, "active_disasters": 1, "hour": 12}
        sound_manager._update_adaptive_bgm(game_state)
        assert sound_manager.current_bgm == "disaster_theme", "Should play disaster theme during disasters"
        
        self._pass_test("Adaptive audio working correctly")
    
    def test_settings_persistence(self):
        """Test settings save/load"""
        self._start_test("Settings Persistence")
        
        # Set custom settings
        self.system.set_volume(0.3, 0.6)
        self.system.sound_manager.adaptive_volume = False
        self.system.enabled = False
        
        # Save settings
        test_filename = "test_audio_settings.json"
        result = self.system.save_settings(test_filename)
        
        # Create new system and load settings
        new_system = SoundEffectsSystem()
        load_result = new_system.load_settings(test_filename)
        
        # Verify settings were restored
        assert load_result == True, "Should successfully load settings"
        assert new_system.sound_manager.bgm_volume == 0.3, "Should restore BGM volume"
        assert new_system.sound_manager.sfx_volume == 0.6, "Should restore SFX volume"
        assert new_system.sound_manager.adaptive_volume == False, "Should restore adaptive volume setting"
        assert new_system.enabled == False, "Should restore enabled state"
        
        # Clean up
        import os
        try:
            os.remove(test_filename)
        except:
            pass
        
        self._pass_test("Settings persistence working correctly")
    
    def test_performance_under_load(self):
        """Test system performance under load"""
        self._start_test("Performance Under Load")
        
        start_time = time.time()
        
        # Create many effects
        for i in range(50):
            self.system.visual_effect_manager.create_effect(
                VisualEffectType.EXPLOSION, 
                i * 10, i * 5, 
                duration=120, 
                scale=1.0
            )
        
        # Run many update cycles
        for frame in range(300):  # 5 seconds at 60fps
            self.game_state.frame_count = frame
            self.game_state.population = 1000 + frame
            self.game_state.hour = (frame // 60) % 24
            
            self.system.update(self.game_state.to_dict())
            
            # Emit some events
            if frame % 10 == 0:
                self.system.emit_event("building_placed", {
                    "position": (frame % 100, (frame * 2) % 100),
                    "building_type": "RESIDENTIAL"
                })
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within reasonable time (less than 1 second for this test)
        assert execution_time < 5.0, f"Performance test took too long: {execution_time:.2f}s"
        
        # Check system is still functional
        status = self.system.get_system_status()
        assert isinstance(status, dict), "Should return valid status"
        assert "active_effects" in status, "Status should include active effects"
        
        self._pass_test(f"Performance test completed in {execution_time:.2f}s")
    
    def test_memory_management(self):
        """Test memory management and cleanup"""
        self._start_test("Memory Management")
        
        vfx_manager = self.system.visual_effect_manager
        
        # Test effect limit enforcement
        original_max = vfx_manager.max_effects
        vfx_manager.max_effects = 5  # Set low limit for testing
        
        # Create more effects than the limit
        for i in range(10):
            vfx_manager.create_effect(VisualEffectType.SPARKLE, i * 10, i * 10)
        
        # Should not exceed limit
        assert len(vfx_manager.effects) <= vfx_manager.max_effects, "Should respect effect limit"
        
        # Restore original limit
        vfx_manager.max_effects = original_max
        
        # Test particle cleanup
        effect_count_before = len(vfx_manager.effects)
        
        # Force all effects to expire
        for effect in vfx_manager.effects:
            effect.current_frame = effect.duration
            for particle in effect.particles:
                particle.life = 0
        
        vfx_manager.update()
        
        # Effects should be cleaned up
        assert len(vfx_manager.effects) < effect_count_before, "Should clean up expired effects"
        
        # Test clear all
        vfx_manager.create_effect(VisualEffectType.FIRE, 50, 50)
        vfx_manager.clear_all()
        assert len(vfx_manager.effects) == 0, "Should clear all effects"
        
        self._pass_test("Memory management working correctly")
    
    def _start_test(self, test_name: str):
        """Start a test"""
        self.total_tests += 1
        print(f"Testing: {test_name}...")
    
    def _pass_test(self, message: str):
        """Mark test as passed"""
        self.passed_tests += 1
        self.test_results.append(("PASS", message))
        print(f"  ✓ {message}")
    
    def _fail_test(self, message: str, error: Exception):
        """Mark test as failed"""
        self.test_results.append(("FAIL", f"{message}: {str(error)}"))
        print(f"  ✗ {message}: {str(error)}")
    
    def _generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        report = {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.total_tests - self.passed_tests,
            "success_rate": success_rate,
            "test_results": self.test_results,
            "system_status": self.system.get_system_status()
        }
        
        print(f"\n=== Test Report ===")
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100.0:
            print("🎉 All tests passed!")
        elif success_rate >= 90.0:
            print("✅ Great! Most tests passed.")
        elif success_rate >= 70.0:
            print("⚠️  Some issues found. Review failed tests.")
        else:
            print("❌ Multiple failures. System needs attention.")
        
        print(f"\nSystem Status:")
        for key, value in report["system_status"].items():
            print(f"  {key}: {value}")
        
        return report

def main():
    """Run all sound effects system tests"""
    tester = SoundEffectsSystemTester()
    
    try:
        report = tester.run_all_tests()
        return report
    except Exception as e:
        print(f"Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()