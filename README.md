# ConcLand

ConcLand is a minimal city simulation game implemented in Python using the Pyxel game engine.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Page Actions](https://img.shields.io/badge/Page%20Actions-Auto%20Deploy-brightgreen.svg)](https://kurogedelic.github.io/ConcLand/)

## Quick Start

### Requirements
- Python 3.8 or higher
- Pyxel 2.0 or higher

### Installation
```bash
pip install pyxel
```

### Running the Game
```bash
# Standard execution
python main.py

# Enhanced launcher with new systems
python3 launch_with_enhancements.py

# Explicit mode selection
python main.py --mode original

# Debug mode
python main.py --debug
```

**New Features (Enhanced Version Only)**:
- Enhanced UI (notifications, tooltips, feedback)
- New Game Systems (water supply, underground, crime, fire, city status)
- Verbose Debug Mode (CLI, LLM output)
- BGM/SFX System (placeholder implementation)

## Game Controls

### ⚠️ Browser/WASM Version Notice
**Arrow keys may not work in the browser version. Please use WASD for cursor movement!**
ブラウザ版では矢印キーが動作しない場合があります。カーソル移動にはWASDキーをご使用ください！

### Basic Controls
- **WASD**: Cursor movement (⚠️ Arrow keys may not work in browser)
- **Space/Z**: Place building
- **TAB**: Cycle focus states (Game → Palette → View Mode)
- **ESC**: Return to game focus

### Focus System
The game uses a focus system to prevent key conflicts:
- **GAME Focus**: Normal cursor movement and building placement
- **PALETTE Focus**: Arrow keys navigate palette items (auto-selects)
- **VIEW_MODE Focus**: Arrow keys cycle through view modes

### Tool Selection (Number Keys)
- **1**: Residential | **2**: Commercial | **3**: Industrial
- **4**: Road | **5**: Rail (cycle) | **6**: Park (cycle)
- **7**: Wire | **8**: Power Plants (cycle) | **9**: Ports (cycle)
- **0**: Public Services (cycle) | **-**: Bulldozer | **=**: Agricultural

### UI Panels (F-keys)
- **F1**: Statistics Panel
- **F2**: Economy Panel
- **F3**: Traffic Panel
- **F4**: Disaster Panel
- **F5**: Policies Panel

### Useful Features
- **M**: Toggle minimap display
- **/**: Toggle controls guide (always available during gameplay)
- **O**: Save city (press twice to confirm)
- **I**: Load city (press twice to confirm)

### Help System
Press **/** during gameplay to show the simplified controls guide at any time.

## Game Systems

### RCI Zoning
- **Residential**: Provides population
- **Commercial**: Provides employment and tax revenue
- **Industrial**: Provides employment, generates pollution

### Infrastructure
- **Power**: Power supply via plants and transmission lines
- **Transportation**: Road and rail networks
- **Public Services**: Police, fire, hospitals

### Simulation
- **Pollution**: Spreads from industrial zones, affects land value
- **Land Value**: Determined by pollution, parks, distance to commercial
- **Growth**: Automatic development based on RCI demand balance

## Project Structure

```
ConcLand/
├── main.py                           # Main entry point
├── launch_with_enhancements.py      # Enhanced launcher
├── concland.py                      # Core game logic
├── enhanced_title_menu.py           # Enhanced title menu
├── ui_enhancements.py               # UI enhancement system
├── new_game_systems.py              # New game systems
├── verbose_debug_system.py          # Debug system
├── bgm_sfx_system.py                # Audio system
├── config/                          # Configuration files
├── assets/                          # Game assets (30+ new tiles)
├── data/                            # Save data
├── misc/                            # Tools and tests
├── docs/                            # Documentation
├── LICENSE                          # MIT License
├── README.md                        # This file (English)
├── README_JA.md                     # Japanese version
└── .github/workflows/               # CI/CD workflows
```

## For Developers

### New Systems (Implemented 2026-05-10)
- **ui_enhancements.py** - UI enhancements (notifications, tooltips, feedback)
- **new_game_systems.py** - New game systems (water, underground, crime, fire, status)
- **verbose_debug_system.py** - Verbose debug system (CLI, LLM output)
- **bgm_sfx_system.py** - Audio system (BGM, SFX, ambient)
- **enhanced_title_menu.py** - Enhanced title menu

### Existing Systems
- `traffic_system.py` - Traffic management
- `economic_system.py` - Economic simulation
- `disaster_system.py` - Disaster system
- `visual_system.py` - Visual enhancements

### Configuration and Modules
- `config/game_config.py` - Game configuration
- `config/modules.json` - Module management
- `core/module_manager.py` - Dynamic module loading

### Integration Tools
- `launch_with_enhancements.py` - Enhanced launcher
- `simple_integrate.py` - Simple integration tool

### Testing
```bash
# Integration tests
python integration_test.py

# Project analysis
python misc/tools/organize_project_v2.py --mode analyze
```

## Documentation

- **[README_JA.md](README_JA.md)** - Japanese version
- **[SIMPLIFIED_CONTROLS_GUIDE_EN.md](docs/SIMPLIFIED_CONTROLS_GUIDE_EN.md)** - Detailed controls guide (English)
- **[SIMPLIFIED_CONTROLS_GUIDE_JA.md](docs/SIMPLIFIED_CONTROLS_GUIDE_JA.md)** - 詳細な操作ガイド（日本語）
- **[docs/](docs/)** - Additional documentation

## License

This project is open source and available under the [MIT License](LICENSE).

Copyright (c) 2026 Leo Kuroshita (@kurogedelic)

## Contributing

Bug reports and feature requests are welcome!

---

**Play on Web**: [https://kurogedelic.github.io/ConcLand/](https://kurogedelic.github.io/ConcLand/)

