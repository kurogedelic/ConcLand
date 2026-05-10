# 🏙️ ConcLand - City Simulation Game

ConcLand is a minimal city simulation game inspired by the original SimCity (1989), implemented in Python using the Pyxel game engine.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🚀 Quick Start

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
- 🎨 Enhanced UI (notifications, tooltips, feedback)
- 🏛️ New Game Systems (water supply, underground, crime, fire, city status)
- 🔧 Verbose Debug Mode (CLI, LLM output)
- 🎵 BGM/SFX System (placeholder implementation)

## 🎮 Game Controls

### Basic Controls
- **Arrow Keys**: Cursor movement (K/J/H/L also works)
- **Space/Z**: Place building
- **X**: Demolish building

### Tool Selection (Intuitive QWERTY Layout)
- **Q**: Residential Zone
- **W**: Commercial Zone
- **E**: Industrial Zone
- **R**: Road
- **T**: Rail/Rail Station (cycle through)
- **Y**: Park (cycle through)
- **U**: Wire
- **I**: Power Plant (cycle through)
- **O**: Port Facilities (cycle through)
- **P**: Public Facilities (cycle through)
- **A**: Agricultural
- **Backslash (\)**: Bulldoze (delete)

### Useful Features
- **H**: Toggle controls guide (always available during gameplay)
- **V**: Cycle view modes (normal/pollution/land value/power/traffic)
- **B**: Tool palette (select from all tools)

### Detailed UI Panels
- **S**: Statistics Panel
- **E**: Economy Panel
- **T**: Traffic Panel
- **D**: Disaster Panel
- **P**: Policies Panel

### Other Controls
- **M**: RCI merge check
- **N**: Save (press twice to confirm)
- **ESC**: Close UI panels (does not quit game)

### How to Quit
- Click the window close button (×) to quit
- ESC key does not quit the game (only closes panels)

### Help System
Press **H** during gameplay to show the simplified controls guide at any time. A tutorial is automatically displayed on first launch.

## 🏗️ Game Systems

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

## 📁 Project Structure

```
ConcLand/
├── main.py                           # Main entry point
├── launch_with_enhancements.py      # Enhanced launcher
├── concland_mini.py                 # Core game logic
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

## 🔧 For Developers

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

## 📚 Documentation

- **[README_JA.md](README_JA.md)** - Japanese version
- **[SIMPLIFIED_CONTROLS_GUIDE_EN.md](docs/SIMPLIFIED_CONTROLS_GUIDE_EN.md)** - Detailed controls guide (English)
- **[SIMPLIFIED_CONTROLS_GUIDE_JA.md](docs/SIMPLIFIED_CONTROLS_GUIDE_JA.md)** - 詳細な操作ガイド（日本語）
- **[docs/](docs/)** - Additional documentation

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

Copyright (c) 2026 Leo Kuroshita (@kurogedelic)

## 🤝 Contributing

Bug reports and feature requests are welcome!

---

🎮 **Happy City Building!**
