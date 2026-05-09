# MicroPolis - Clean Room City Simulation

A SimCity-inspired city building simulation implemented from scratch in Python using Pyxel.

## Features

### Core Mechanics
- **Zone System**: Residential, Commercial, and Industrial zones that develop over time
- **Infrastructure**: Roads, rails, and power lines to connect your city
- **Power Grid**: Realistic power distribution through connected infrastructure
- **Services**: Police, Fire, Hospitals, and Schools with coverage areas
- **Environment**: Pollution, crime, and land value simulation
- **Economy**: Tax collection, maintenance costs, and city budget management

### View Modes
- **Normal**: Standard city view
- **Power**: Shows powered/unpowered areas
- **Pollution**: Displays pollution levels
- **Crime**: Shows crime density
- **Land Value**: Visualizes property values
- **Service Coverage**: Police and Fire coverage areas

### Building Types
- **Zones**: Residential (R), Commercial (C), Industrial (I)
- **Infrastructure**: Roads, Rails, Power Lines
- **Power Plants**: Coal and Nuclear
- **Services**: Police, Fire, Hospital, School
- **Recreation**: Parks, Stadium
- **Transportation**: Airport, Seaport

## Controls

### Camera
- **WASD** or **Arrow Keys**: Move camera around the map
- **Mouse**: Click to place buildings

### Simulation
- **Space**: Pause/Resume simulation
- **1-3**: Set simulation speed (1x, 2x, 4x)
- **Tab**: Cycle through view modes

### Building
- Click on tool palette to select building type
- Click on map to place building
- Green cursor = valid placement
- Red cursor = invalid placement

## Game Mechanics

### Zone Development
- Zones require power to develop
- Residential zones need low pollution and high land value
- Commercial zones need traffic to thrive
- Industrial zones grow easily but create pollution

### Power System
- Power plants generate electricity
- Power flows through all connected infrastructure
- Buildings need power connection to function

### Service Coverage
- Police stations reduce crime in their coverage area
- Fire stations provide fire protection
- Coverage decreases with distance

### Land Value Factors
- (+) Parks, low crime, service coverage, water views
- (-) Pollution, high crime, no services

### Population & Demand
- RCI indicators show demand for each zone type
- Balance residential, commercial, and industrial growth
- Population generates tax revenue

## Technical Details

- Built with Python 3 and Pyxel
- Map size: 128x128 tiles
- Viewport scrolling for large cities
- Clean room implementation (no copyrighted code)
- Modular design for easy extension

## Running the Game

```bash
python micropolis_city.py
```

## Requirements
- Python 3.8+
- Pyxel 1.9+

## Future Enhancements
- Disasters (fire, earthquake, monster)
- More building types
- Budget graphs and statistics
- Scenario challenges
- Save/Load functionality
- Sound effects and music

## License
MIT License - Feel free to use and modify!