# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ConcLand is a minimal city simulation game implemented in Python using the Pyxel game engine. The game features Game Boy-style resolution (320x288) with city simulation mechanics including RCI zoning, pollution simulation, power grid management, and advanced systems for traffic, economy, disasters, and more.

## Dependencies

### Required
- Python 3.8+
- Pyxel 2.0+ (tested with 2.7.9)

### Installation
```bash
pip install pyxel
```

### Optional Dependencies
- Japanese BDF fonts (for Japanese text rendering) - located in `assets/font/`
- pytest (for running test suite)

## Development Commands

### Running the Game
```bash
# Standard execution (recommended)
python main.py

# Explicit mode selection
python main.py --mode original    # Original Game Boy-style version
python main.py --mode modular     # Modular version (currently same as original)
python main.py --debug            # Debug mode with verbose output

# Direct execution (also works)
python concland_mini.py
```

### Testing
```bash
# Integration tests
python integration_test.py

# Unit tests (if pytest is available)
pytest misc/tests -q

# Specific system tests
python integration_test.py --system traffic
python integration_test.py --system economic
```

### Development Tools
```bash
# Project organization (see ORGANIZATION_GUIDE.md)
python3 misc/tools/organize_project_v2.py --mode analyze    # Dry-run analysis
python3 misc/tools/organize_project_v2.py --mode restructure # Execute reorganization

# Generate clean 100x100 map
python misc/tools/create_clean_map_100.py

# Terrain generation
python terrain_generator.py
```

### Code Quality (Optional)
```bash
# Linting (not enforced, but suggested)
ruff .
black .
```

## Architecture Overview

### Module System Architecture

ConcLand uses a **dynamic module loading system** via `core/module_manager.py`:

1. **Module Configuration**: `config/modules.json` defines all game systems with dependencies and enablement flags
2. **Dynamic Loading**: `ModuleManager` class handles module initialization based on configuration
3. **Dependency Resolution**: Modules automatically load in correct order based on dependencies
4. **Hot-Swapping**: Modules can be enabled/disabled via configuration without code changes

```python
# Module loading pattern
from core.module_manager import ModuleManager

manager = ModuleManager(game_instance)
manager.load_all_modules()  # Loads enabled modules from config
```

### Core Game Engine

**Main Game** (`concland_mini.py`)
- Resolution: 320x288 (2x scaled from Game Boy's 160x144)
- Map size: 100x100 tiles (configurable, currently 100x100)
- Tile size: 8x8 pixels (individual PNG tiles)
- Real-time simulation at 60 FPS
- Staggered updates for performance (pollution every 4 frames, land value every 8 frames, RCI every 16 frames)

**Entry Point** (`main.py`)
- Command-line interface for mode selection
- Handles both original and modular versions
- Debug mode support
- Error handling and graceful fallbacks

### Key Systems (Top-Level Modules)

#### Simulation Systems
- **`traffic_system.py`** (753 lines) - A* pathfinding, bus routes, traffic lights, congestion analysis
- **`economic_system.py`** (485 lines) - 10 resource types, market dynamics, tax policies, seasonal effects
- **`disaster_system.py`** (776 lines) - 6 disaster types, emergency services, damage simulation
- **`train_system.py`** - Railway management with automatic train spawning

#### Game Mechanics
- **`difficulty_system.py`** - Difficulty scaling with multiple presets
- **`goals_challenges_system.py`** - Quest system with daily challenges
- **`tutorial_system.py`** - Interactive tutorial framework
- **`rci_zone_fix.py`** - RCI zone management with 3x3 unified placement

#### UI & Visualization
- **`advanced_ui.py`** (833 lines) - Multi-panel interface with real-time graphs
- **`advanced_window_system.py`** - 9-slice window system with docking support
- **`data_visualization.py`** - Dashboard with chart rendering
- **`visual_system.py`** - Particle effects and visual enhancements
- **`title_menu_system.py`** - Animated title screen with menu navigation

#### World Generation
- **`image_tile_system.py`** (32,395 bytes) - Individual PNG tile loading with two-pass rendering for large buildings
- **`terrain_generator.py`** - Voronoi-based procedural terrain generation
- **`diagonal_coastline_system.py`** - Diagonal coastline rendering support

### File Structure

```
ConcLand/
├── main.py                        # Entry point with CLI
├── concland_mini.py              # Core game logic (245KB)
├── integration_test.py           # Comprehensive test suite
│
├── core/                         # Core framework
│   ├── module_manager.py         # Dynamic module loading
│   └── base_game.py              # Base game class (if exists)
│
├── config/                       # Configuration files
│   ├── game_config.py            # Game constants and settings
│   ├── modules.json              # Module definitions and dependencies
│   └── user_settings.json        # User preferences (auto-generated)
│
├── data/                         # Runtime data
│   ├── economy/
│   │   └── resources.json        # Economic system configuration
│   └── saves/                    # Save files (savegame.dat, etc.)
│
├── assets/                       # Game assets
│   ├── tiles/                    # Individual 8x8 PNG tiles by category
│   ├── icons/                    # 8x8 UI icons
│   ├── font/                     # Japanese BDF fonts
│   └── palette256_magenta.png    # 256-color palette
│
├── docs/                         # Documentation
│   ├── API_REFERENCE.md          # System API documentation
│   └── GAME_ARCHITECTURE.md      # Architecture documentation
│
├── misc/                         # Legacy/experimental code
│   ├── micropolis/               # Original SimCity source reference
│   ├── systems/                  # Modular system implementations
│   ├── tests/                    # Test files
│   └── tools/                    # Development utilities
│
├── AGENTS.md                     # AI agent guidelines
├── ORGANIZATION_GUIDE.md         # Project reorganization guide
├── PROJECT_STRUCTURE.md          # Planned folder structure
├── CLAUDE.md                     # This file
└── README.md                     # Basic project information
```

### Configuration System

**`config/modules.json`** - Module registry with dependencies:
```json
{
  "modules": [
    {
      "name": "traffic_system",
      "class_name": "AdvancedTrafficSystem",
      "dependencies": [],
      "enabled": true,
      "config": { ... }
    }
  ]
}
```

**`config/game_config.py`** - Game constants:
- Screen dimensions (SCREEN_WIDTH, SCREEN_HEIGHT)
- Map settings (MAP_SIZE, TILE_SIZE)
- Building costs
- Simulation parameters
- Economic settings

### Building System Architecture

**Tile Sizes & Rendering:**
- Standard tiles: 8x8 pixels
- Large buildings: 24x24 (public buildings), 32x32 (power plants)
- Two-pass rendering: regular tiles first, then large buildings to prevent overlap

**RCI Zones:**
- Historically 3x3 unified zones, now transitioning to 1x1 continuous placement
- Population-based growth following 1989 SimCity algorithms
- Density stages: 1-4 for each zone type
- Growth factors: land value, pollution (negative), power supply, traffic access

**Infrastructure:**
- Roads, rails, power lines: 1x1 tiles with continuous placement
- Power grid: spreads through adjacent buildings
- Automatic connection patterns for roads (12 variants) and rails (8 variants)

### Simulation Mechanics

**Pollution:**
- Source: Industrial zones
- Spread: 5% diffusion to adjacent tiles per tick
- Decay: 30% natural decay per tick
- Affects: Land value (1:1 negative ratio), RCI growth

**Land Value:**
- Base: Distance-based calculation
- Modifiers: Parks (+10 in 2-tile radius), Commercial (+5 in 3-tile radius)
- Pollution: Direct negative impact
- Range: 0-255

**RCI Demand:**
- Residential needs: Commercial, low pollution, road access
- Commercial needs: Residential + Industrial, traffic access
- Industrial needs: Residential (workers), road access
- Balance: Auto-calculated based on current population ratios

## Development Guidelines

### Code Conventions

**File Naming:**
- System modules: `{feature}_system.py` (e.g., `traffic_system.py`)
- UI modules: `{feature}_ui.py` or similar
- Tests: `test_{feature}.py` or in `integration_test.py`

**Code Style:**
- 4-space indentation (PEP 8)
- Type hints encouraged (Python 3.8+)
- Docstrings for modules, classes, and public functions
- No side effects at import time

**Naming Conventions:**
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

### Module Integration Pattern

When adding new systems:

1. **Create system file** (e.g., `new_system.py`)
2. **Add to `config/modules.json`**:
   ```json
   {
     "name": "new_system",
     "class_name": "NewSystem",
     "dependencies": ["existing_system"],
     "enabled": true
   }
   ```

3. **Integrate in `concland_mini.py`**:
   ```python
   from new_system import NewSystem

   class ConcLandMini:
       def __init__(self):
           self.new_system = NewSystem(MAP_SIZE)

       def update(self):
           self.new_system.update(self.grid, self.sim_data)
   ```

4. **Add to `integration_test.py`** for validation

### Asset Creation Guidelines

- All tiles: Exactly 8x8 pixels (except large buildings: 24x24, 32x32)
- Format: PNG with 256-color palette
- Transparency: Magenta (#FF00FF) at index 255
- Organization: `assets/tiles/{category}/{name}.png`
- Road/rail tiles: Must include all connection variants (12 road, 8 rail)

### Save/Load System

**Save Format:** Pickle-based serialization to `savegame.dat`
- Grid state
- Simulation data (pollution, land value, traffic)
- Economic state
- System-specific data (if integrated)

**Hotkeys:**
- O: Save city to `savegame.dat`
- I: Load from `savegame.dat`
- T: Save terrain only to `terrain_100.dat`

**Auto-load:** If `terrain_100.dat` exists, it loads automatically on startup

### Testing Guidelines

**Integration Testing:**
- Comprehensive suite in `integration_test.py`
- 24 test cases covering all major systems
- 91.7% pass rate (22/24 tests)
- Run with: `python integration_test.py`

**Unit Testing:**
- Test files in `misc/tests/`
- Name: `test_*.py`
- Framework: pytest (optional)
- Pyxel-dependent tests: Use skip guards

### Known Issues & Solutions

1. **Pathfinding edge case**: Empty paths for invalid positions
   - Fix: Add position validation before pathfinding

2. **Disaster iteration bug**: Dictionary size change during iteration
   - Fix: Use list comprehension for iteration

3. **Large building rendering**: Fixed via two-pass rendering in `ImageTileSystem`

4. **Module import paths**: Systems are in root, plan to move to `systems/` directory
   - See `ORGANIZATION_GUIDE.md` for reorganization plan

## Performance Characteristics

- **Target FPS**: 60
- **Map size**: 100x100 tiles (10,000 cells)
- **Memory usage**: ~7MB for all systems
- **CPU impact**: <5% additional load from enhanced systems
- **Update frequency**: Staggered (pollution: every 4 frames, land value: every 8 frames, RCI: every 16 frames)

## Multi-language Support

- Primary language: Japanese (with English fallback)
- Font system: BDF renderer for Japanese characters
- Font files: `assets/font/umplus_j10r.bdf`, `umplus_j12r.bdf`
- Fallback: English when fonts unavailable
- Graceful degradation for missing fonts

## Control Scheme

**Basic Controls:**
- Arrow keys: Cursor movement
- 1-9: Tool selection (Residential, Commercial, Industrial, Road, Rail, Wire, Power, Police, Park)
- 0: Bulldozer tool
- Space/Z: Place building
- X: Delete building
- V: Cycle display modes (normal, pollution, land value, power, traffic)
- Q: Quit game

**Save/Load:**
- O: Save game
- I: Load game
- T: Save terrain only

**UI Panels:**
- S: Statistics panel
- E: Economy panel
- T: Traffic panel
- D: Disaster panel
- P: Policies panel

## Reference Materials

**Original SimCity Mechanics:**
- `misc/micropolis/` - Original Micropolis (SimCity) source code
- Authentic algorithms adapted for Python/Pyxel

**Development Documentation:**
- `docs/API_REFERENCE.md` - Complete API documentation
- `docs/GAME_ARCHITECTURE.md` - System architecture details
- `ENHANCED_FEATURES_GUIDE.md` - Enhanced systems implementation guide
- `COMPLETE_GAME_SYSTEM_PLAN.md` - Full development roadmap

**Project Organization:**
- `PROJECT_STRUCTURE.md` - Planned folder structure
- `ORGANIZATION_GUIDE.md` - Reorganization instructions
- `AGENTS.md` - AI agent development guidelines

## Development Status

**Completed Systems (✅):**
- Core city simulation (RCI, pollution, land value, power grid)
- Traffic system (A* pathfinding, buses, traffic lights)
- Economic system (resources, policies, taxes, seasons)
- Disaster system (6 disaster types, emergency services)
- Advanced UI (real-time graphs, multi-panel interface)
- Title/menu system (animated, user settings)
- Tile system (individual PNG files, two-pass rendering)
- Terrain generation (Voronoi-based)

**Recently Completed (2026-05-10):**
- ✅ Enhanced UI/UX systems (notifications, tooltips, feedback effects)
- ✅ New game systems (water supply, underground, crime, fire, city status)
- ✅ Verbose debug system with CLI interface
- ✅ BGM/SFX audio system architecture
- ✅ Enhanced title menu with particles
- ✅ 30 new tile assets generated
- ✅ Integration tools and enhanced launcher

**In Progress (🚧):**
- Module reorganization (planned move to `systems/`, `ui/`, `world/`)
- Tutorial system integration
- Sound system implementation (placeholder complete, real audio data needed)

**Planned (📋):**
- Tourism system
- Education system
- Environmental system
- Multiplayer support

## Quick Reference

### Running the Game
```bash
python main.py                         # Standard launch
python3 launch_with_enhancements.py  # Enhanced launcher (new systems)
python main.py --debug                   # Debug mode
python concland_mini.py                  # Direct execution
```

### Testing
```bash
python integration_test.py  # Run all tests
pytest misc/tests -q        # Unit tests (if pytest available)
```

### Key Files
- `main.py` - Entry point
- `launch_with_enhancements.py` - Enhanced launcher (NEW)
- `concland_mini.py` - Core game (245KB, 7000+ lines)
- `ui_enhancements.py` - UI enhancements (NEW)
- `new_game_systems.py` - New game systems (NEW)
- `verbose_debug_system.py` - Debug system (NEW)
- `bgm_sfx_system.py` - Audio system (NEW)
- `config/modules.json` - Module registry
- `config/game_config.py` - Game constants
- `integration_test.py` - Test suite

### Common Tasks
- **Try new systems**: Use `python3 launch_with_enhancements.py` (no code changes needed)
- **Add new system**: Create file, add to `config/modules.json`, integrate in `concland_mini.py`
- **Add building type**: Update `CellType` enum, add tile PNGs, update costs in `game_config.py`
- **Modify simulation balance**: Adjust parameters in `game_config.py`
- **Debug module**: Enable in `modules.json`, set `debug_mode: true` in system settings
- **Integrate new systems**: Follow `ENHANCED_SYSTEMS_GUIDE.md` or `INTEGRATION_GUIDE.md`
