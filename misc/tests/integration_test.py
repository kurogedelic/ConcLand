"""
Integration Test Suite for ConcLand
Tests all integrated systems working together
"""
import sys
sys.path.append('misc')  # For economic_system dependencies

from concland_mini import ConcLandMini
from traffic_system import AdvancedTrafficSystem
from economic_system import ConcLandEconomicSystem
from disaster_system import DisasterSystem
from advanced_ui import AdvancedUI, UIPanel

def test_all_systems_initialization():
    """Test that all systems initialize correctly"""
    print("🧪 Testing system initialization...")

    game = ConcLandMini(skip_pyxel_init=True)

    # Check all systems are initialized
    assert hasattr(game, 'traffic_system'), "❌ Traffic system not initialized"
    assert hasattr(game, 'economic_system'), "❌ Economic system not initialized"
    assert hasattr(game, 'disaster_system'), "❌ Disaster system not initialized"
    assert hasattr(game, 'ui_system'), "❌ UI system not initialized"

    # Check systems are correct type
    assert isinstance(game.traffic_system, AdvancedTrafficSystem), "❌ Traffic system wrong type"
    assert isinstance(game.economic_system, ConcLandEconomicSystem), "❌ Economic system wrong type"
    assert isinstance(game.disaster_system, DisasterSystem), "❌ Disaster system wrong type"
    assert isinstance(game.ui_system, AdvancedUI), "❌ UI system wrong type"

    print("✅ All systems initialized correctly")
    return True

def test_economic_system_integration():
    """Test economic system integration with existing economy"""
    print("🧪 Testing economic system integration...")

    game = ConcLandMini(skip_pyxel_init=True)

    # Test initial sync
    assert game.economic_system.funds == game.funds, "❌ Funds not synced"
    assert game.economic_system.tax_policy.residential_rate == game.tax_rate / 100.0, "❌ Tax rate not synced"

    # Test data preparation for UI
    ui_data = game._prepare_ui_data()
    assert 'economic_system' in ui_data, "❌ Economic data not in UI"

    # Test building counting
    buildings = game._count_buildings_by_type()
    assert 'RESIDENTIAL' in buildings, "❌ Residential not counted"
    assert 'COMMERCIAL' in buildings, "❌ Commercial not counted"
    assert 'INDUSTRIAL' in buildings, "❌ Industrial not counted"

    print("✅ Economic system integration working")
    return True

def test_traffic_system_integration():
    """Test traffic system integration"""
    print("🧪 Testing traffic system integration...")

    game = ConcLandMini(skip_pyxel_init=True)

    # Test traffic system initialized
    assert len(game.traffic_system.bus_routes) > 0, "❌ Bus routes not initialized"

    # Test data preparation for UI
    ui_data = game._prepare_ui_data()
    assert 'traffic_system' in ui_data, "❌ Traffic data not in UI"

    print("✅ Traffic system integration working")
    return True

def test_disaster_system_integration():
    """Test disaster system integration"""
    print("🧪 Testing disaster system integration...")

    game = ConcLandMini(skip_pyxel_init=True)

    # Test disaster system initialized
    assert game.disaster_system.map_size == 100, "❌ Disaster system wrong map size"

    # Test data preparation for UI
    ui_data = game._prepare_ui_data()
    assert 'disaster_system' in ui_data, "❌ Disaster data not in UI"

    print("✅ Disaster system integration working")
    return True

def test_ui_system_integration():
    """Test UI system integration"""
    print("🧪 Testing UI system integration...")

    game = ConcLandMini(skip_pyxel_init=True)

    # Test UI system initialized
    assert game.ui_system.current_panel == UIPanel.MAIN_GAME, "❌ UI not in MAIN_GAME mode"

    # Test panel switching
    game.ui_system.set_panel(UIPanel.STATISTICS)
    assert game.ui_system.current_panel == UIPanel.STATISTICS, "❌ Panel switch failed"

    game.ui_system.set_panel(UIPanel.ECONOMY)
    assert game.ui_system.current_panel == UIPanel.ECONOMY, "❌ Panel switch failed"

    # Test back to main
    game.ui_system.set_panel(UIPanel.MAIN_GAME)
    assert game.ui_system.current_panel == UIPanel.MAIN_GAME, "❌ Panel switch failed"

    print("✅ UI system integration working")
    return True

def test_simulation_update():
    """Test simulation update with all systems"""
    print("🧪 Testing simulation update...")

    game = ConcLandMini(skip_pyxel_init=True)

    # Run simulation for 60 frames
    for i in range(60):
        game._update_simulation()

    # Check systems updated
    assert game.simulation_tick == 60, "❌ Simulation tick not updated"

    print("✅ Simulation update working")
    return True

def test_save_load_integration():
    """Test save/load with all system data"""
    print("🧪 Testing save/load integration...")

    game = ConcLandMini(skip_pyxel_init=True)

    # Place some buildings to generate data
    game.grid[10][10] = game.grid[10][10].RESIDENTIAL
    game.grid[10][11] = game.grid[10][11].ROAD

    # Save
    game.save_city("test_save.dat")

    # Create new game and load
    game2 = ConcLandMini(skip_pyxel_init=True)
    game2.load_city("test_save.dat")

    # Check basic data restored
    assert game2.funds == game.funds, "❌ Funds not restored"
    assert game2.total_population == game.total_population, "❌ Population not restored"

    print("✅ Save/load integration working")
    return True

def run_all_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("🚀 Starting ConcLand Integration Tests")
    print("=" * 60)

    tests = [
        ("System Initialization", test_all_systems_initialization),
        ("Economic System Integration", test_economic_system_integration),
        ("Traffic System Integration", test_traffic_system_integration),
        ("Disaster System Integration", test_disaster_system_integration),
        ("UI System Integration", test_ui_system_integration),
        ("Simulation Update", test_simulation_update),
        ("Save/Load Integration", test_save_load_integration)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        try:
            result = test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
    print("=" * 60)

    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
