"""
Disaster Management System for ConcLand
Handles natural disasters, emergency response, and recovery
"""
import random
import math
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict

class DisasterType(Enum):
    EARTHQUAKE = "earthquake"
    FIRE = "fire"  
    TYPHOON = "typhoon"
    TSUNAMI = "tsunami"
    FLOOD = "flood"
    VOLCANIC = "volcanic"

class DisasterSeverity(Enum):
    MINOR = 1
    MODERATE = 2
    MAJOR = 3
    CATASTROPHIC = 4

@dataclass
class DisasterEvent:
    """Individual disaster event"""
    id: str
    disaster_type: DisasterType
    severity: DisasterSeverity
    center_x: int
    center_y: int
    radius: int
    duration: int  # Frames
    remaining_duration: int
    damage_per_frame: float
    spread_chance: float = 0.0
    warning_time: int = 0  # Frames of advance warning
    
    def is_active(self) -> bool:
        return self.remaining_duration > 0

@dataclass
class EmergencyService:
    """Emergency response service"""
    service_type: str
    japanese_name: str
    effectiveness: Dict[DisasterType, float]  # How effective against each disaster type
    response_radius: int
    capacity: int
    current_load: int = 0
    
    def can_respond(self) -> bool:
        return self.current_load < self.capacity
    
    def get_effectiveness(self, disaster_type: DisasterType) -> float:
        return self.effectiveness.get(disaster_type, 0.1)

@dataclass  
class DisasterPreparedness:
    """City's disaster preparedness measures"""
    earthquake_resistant_buildings: int = 0
    fire_resistant_buildings: int = 0
    flood_barriers: int = 0
    early_warning_systems: int = 0
    emergency_shelters: int = 0
    evacuation_routes: List[Tuple[int, int]] = None
    
    def __post_init__(self):
        if self.evacuation_routes is None:
            self.evacuation_routes = []

class DisasterSystem:
    """Main disaster management system"""
    
    def __init__(self, map_size: int):
        self.map_size = map_size
        
        # Active disasters
        self.active_disasters: Dict[str, DisasterEvent] = {}
        self.disaster_history: List[DisasterEvent] = []
        
        # Emergency services
        self.emergency_services: Dict[Tuple[int, int], EmergencyService] = {}
        self.preparedness = DisasterPreparedness()
        
        # Disaster probability and timing
        self.base_disaster_chance = 0.0005  # Very low base chance per frame
        self.disaster_cooldown = 0
        self.warning_active = False
        self.warning_message = ""
        self.warning_timer = 0
        
        # Damage tracking
        self.total_damage_cost = 0
        self.buildings_destroyed = 0
        self.casualties = 0
        
        # Initialize emergency services
        self._initialize_emergency_services()
    
    def _initialize_emergency_services(self):
        """Initialize emergency service definitions"""
        self.service_definitions = {
            "FIRE": EmergencyService(
                service_type="FIRE",
                japanese_name="消防署",
                effectiveness={
                    DisasterType.FIRE: 0.8,
                    DisasterType.EARTHQUAKE: 0.3,
                    DisasterType.TYPHOON: 0.2,
                    DisasterType.TSUNAMI: 0.1
                },
                response_radius=8,
                capacity=3
            ),
            "POLICE": EmergencyService(
                service_type="POLICE", 
                japanese_name="警察署",
                effectiveness={
                    DisasterType.EARTHQUAKE: 0.4,
                    DisasterType.FIRE: 0.2,
                    DisasterType.TYPHOON: 0.5,
                    DisasterType.FLOOD: 0.4
                },
                response_radius=10,
                capacity=2
            ),
            "HOSPITAL": EmergencyService(
                service_type="HOSPITAL",
                japanese_name="病院", 
                effectiveness={
                    DisasterType.EARTHQUAKE: 0.6,
                    DisasterType.FIRE: 0.5,
                    DisasterType.TYPHOON: 0.4,
                    DisasterType.TSUNAMI: 0.7
                },
                response_radius=12,
                capacity=5
            )
        }
    
    def register_emergency_service(self, x: int, y: int, service_type: str):
        """Register emergency service building"""
        if service_type in self.service_definitions:
            service = EmergencyService(
                service_type=service_type,
                japanese_name=self.service_definitions[service_type].japanese_name,
                effectiveness=self.service_definitions[service_type].effectiveness.copy(),
                response_radius=self.service_definitions[service_type].response_radius,
                capacity=self.service_definitions[service_type].capacity
            )
            self.emergency_services[(x, y)] = service
    
    def remove_emergency_service(self, x: int, y: int):
        """Remove emergency service building"""
        pos = (x, y)
        if pos in self.emergency_services:
            del self.emergency_services[pos]
    
    def update(self, grid, sim_data, population: int, funds: int):
        """Update disaster system"""
        # Update disaster cooldown
        if self.disaster_cooldown > 0:
            self.disaster_cooldown -= 1
        
        # Update warning system
        if self.warning_timer > 0:
            self.warning_timer -= 1
            if self.warning_timer <= 0:
                self.warning_active = False
        
        # Check for new disasters
        if self.disaster_cooldown == 0:
            self._check_disaster_occurrence(grid, sim_data, population)
        
        # Update active disasters
        self._update_active_disasters(grid, sim_data)
        
        # Update emergency response
        self._update_emergency_response()
    
    def _check_disaster_occurrence(self, grid, sim_data, population: int):
        """Check if a disaster should occur"""
        # Calculate disaster probability based on various factors
        disaster_chance = self.base_disaster_chance
        
        # Population factor (higher population = slightly higher risk)
        population_factor = 1.0 + (population / 100000) * 0.2
        disaster_chance *= population_factor
        
        # Seasonal factors
        season_multipliers = {
            "spring": 1.0,
            "summer": 1.3,  # Typhoon season  
            "autumn": 1.2,  # Earthquake season
            "winter": 0.8
        }
        # Would need to get season from economic system
        
        if random.random() < disaster_chance:
            self._trigger_random_disaster(grid, sim_data)
    
    def _trigger_random_disaster(self, grid, sim_data):
        """Trigger a random disaster event"""
        # Choose disaster type based on probability
        disaster_weights = {
            DisasterType.EARTHQUAKE: 0.25,
            DisasterType.FIRE: 0.35,
            DisasterType.TYPHOON: 0.15,
            DisasterType.TSUNAMI: 0.05,
            DisasterType.FLOOD: 0.15,
            DisasterType.VOLCANIC: 0.05
        }
        
        disaster_type = random.choices(
            list(disaster_weights.keys()),
            weights=list(disaster_weights.values())
        )[0]
        
        # Choose severity
        severity_weights = [0.5, 0.3, 0.15, 0.05]  # Minor, Moderate, Major, Catastrophic
        severity = DisasterSeverity(random.choices([1, 2, 3, 4], weights=severity_weights)[0])
        
        # Find suitable location
        center_x, center_y = self._find_disaster_location(disaster_type, grid)
        
        # Create disaster event
        self.trigger_disaster(disaster_type, severity, center_x, center_y)
    
    def _find_disaster_location(self, disaster_type: DisasterType, grid) -> Tuple[int, int]:
        """Find appropriate location for disaster"""
        if disaster_type == DisasterType.TSUNAMI:
            # Tsunamis start from coastlines
            coastline_positions = []
            for y in range(self.map_size):
                for x in range(self.map_size):
                    # Check if position is near water
                    near_water = False
                    for dy in range(-2, 3):
                        for dx in range(-2, 3):
                            nx, ny = x + dx, y + dy
                            if (0 <= nx < self.map_size and 0 <= ny < self.map_size and
                                hasattr(grid[ny][nx], 'name') and 'WATER' in str(grid[ny][nx])):
                                near_water = True
                                break
                        if near_water:
                            break
                    if near_water:
                        coastline_positions.append((x, y))
            
            if coastline_positions:
                return random.choice(coastline_positions)
        
        elif disaster_type == DisasterType.FIRE:
            # Fires start in developed areas
            developed_positions = []
            for y in range(self.map_size):
                for x in range(self.map_size):
                    cell_type = grid[y][x]
                    if hasattr(cell_type, 'name') and any(zone in str(cell_type) for zone in ['RESIDENTIAL', 'COMMERCIAL', 'INDUSTRIAL']):
                        developed_positions.append((x, y))
            
            if developed_positions:
                return random.choice(developed_positions)
        
        # Default: random location
        return (random.randint(5, self.map_size - 5), random.randint(5, self.map_size - 5))
    
    def trigger_disaster(self, disaster_type: DisasterType, severity: DisasterSeverity, center_x: int, center_y: int):
        """Manually trigger a disaster (for events or testing)"""
        # Disaster parameters based on type and severity
        disaster_params = {
            DisasterType.EARTHQUAKE: {
                DisasterSeverity.MINOR: (3, 180, 0.5, 0.0, 60),      # radius, duration, damage, spread, warning
                DisasterSeverity.MODERATE: (6, 300, 1.2, 0.0, 120),
                DisasterSeverity.MAJOR: (10, 480, 2.5, 0.0, 240),
                DisasterSeverity.CATASTROPHIC: (15, 600, 5.0, 0.0, 480)
            },
            DisasterType.FIRE: {
                DisasterSeverity.MINOR: (2, 240, 0.8, 0.15, 0),
                DisasterSeverity.MODERATE: (3, 360, 1.5, 0.25, 0),
                DisasterSeverity.MAJOR: (5, 540, 2.8, 0.35, 30),
                DisasterSeverity.CATASTROPHIC: (8, 720, 4.5, 0.45, 60)
            },
            DisasterType.TYPHOON: {
                DisasterSeverity.MINOR: (8, 360, 0.6, 0.0, 300),
                DisasterSeverity.MODERATE: (12, 540, 1.1, 0.0, 480),
                DisasterSeverity.MAJOR: (18, 720, 2.0, 0.0, 720),
                DisasterSeverity.CATASTROPHIC: (25, 900, 3.5, 0.0, 1200)
            },
            DisasterType.TSUNAMI: {
                DisasterSeverity.MINOR: (6, 300, 1.5, 0.0, 180),
                DisasterSeverity.MODERATE: (10, 420, 2.8, 0.0, 300),
                DisasterSeverity.MAJOR: (16, 600, 4.5, 0.0, 600),
                DisasterSeverity.CATASTROPHIC: (25, 840, 8.0, 0.0, 900)
            },
            DisasterType.FLOOD: {
                DisasterSeverity.MINOR: (5, 480, 0.4, 0.1, 240),
                DisasterSeverity.MODERATE: (8, 720, 0.8, 0.15, 360),
                DisasterSeverity.MAJOR: (12, 1080, 1.5, 0.2, 600),
                DisasterSeverity.CATASTROPHIC: (18, 1440, 2.5, 0.25, 900)
            },
            DisasterType.VOLCANIC: {
                DisasterSeverity.MINOR: (4, 600, 1.0, 0.05, 120),
                DisasterSeverity.MODERATE: (7, 900, 2.0, 0.1, 300),
                DisasterSeverity.MAJOR: (12, 1200, 3.5, 0.15, 600),
                DisasterSeverity.CATASTROPHIC: (20, 1800, 6.0, 0.2, 1200)
            }
        }
        
        radius, duration, damage, spread_chance, warning_time = disaster_params[disaster_type][severity]
        
        # Create disaster event
        disaster_id = f"{disaster_type.value}_{len(self.active_disasters)}"
        disaster = DisasterEvent(
            id=disaster_id,
            disaster_type=disaster_type,
            severity=severity,
            center_x=center_x,
            center_y=center_y,
            radius=radius,
            duration=duration,
            remaining_duration=duration,
            damage_per_frame=damage,
            spread_chance=spread_chance,
            warning_time=warning_time
        )
        
        # Issue warning if applicable
        if warning_time > 0:
            self._issue_disaster_warning(disaster)
        
        self.active_disasters[disaster_id] = disaster
        
        # Set cooldown to prevent multiple disasters
        self.disaster_cooldown = 3600  # 1 minute cooldown
        
        print(f"⚠️ {disaster_type.value.title()} ({severity.name}) triggered at ({center_x}, {center_y})")
    
    def _issue_disaster_warning(self, disaster: DisasterEvent):
        """Issue disaster warning to city"""
        warning_messages = {
            DisasterType.EARTHQUAKE: "地震警報！大きな揺れに注意してください",
            DisasterType.FIRE: "大規模火災発生！避難準備をしてください", 
            DisasterType.TYPHOON: "台風警報！暴風雨に注意してください",
            DisasterType.TSUNAMI: "津波警報！直ちに高台に避難してください",
            DisasterType.FLOOD: "洪水警報！河川氾濫の危険があります",
            DisasterType.VOLCANIC: "火山噴火警報！降灰に注意してください"
        }
        
        self.warning_active = True
        self.warning_message = warning_messages.get(disaster.disaster_type, "災害警報発令中")
        self.warning_timer = disaster.warning_time
    
    def _update_active_disasters(self, grid, sim_data):
        """Update all active disasters"""
        disasters_to_remove = []
        
        for disaster_id, disaster in self.active_disasters.items():
            if disaster.remaining_duration <= 0:
                disasters_to_remove.append(disaster_id)
                self.disaster_history.append(disaster)
                continue
            
            # Apply disaster effects
            self._apply_disaster_damage(disaster, grid, sim_data)
            
            # Handle spreading disasters (fire, flood)
            if disaster.spread_chance > 0:
                self._handle_disaster_spreading(disaster, grid, sim_data)
            
            disaster.remaining_duration -= 1
        
        # Remove completed disasters
        for disaster_id in disasters_to_remove:
            del self.active_disasters[disaster_id]
    
    def _apply_disaster_damage(self, disaster: DisasterEvent, grid, sim_data):
        """Apply damage from disaster"""
        for y in range(max(0, disaster.center_y - disaster.radius), 
                      min(self.map_size, disaster.center_y + disaster.radius + 1)):
            for x in range(max(0, disaster.center_x - disaster.radius),
                          min(self.map_size, disaster.center_x + disaster.radius + 1)):
                
                # Calculate distance from disaster center
                distance = math.sqrt((x - disaster.center_x)**2 + (y - disaster.center_y)**2)
                
                if distance <= disaster.radius:
                    # Calculate damage based on distance (closer = more damage)
                    distance_factor = 1.0 - (distance / disaster.radius)
                    actual_damage = disaster.damage_per_frame * distance_factor
                    
                    # Apply damage reduction from emergency services
                    damage_reduction = self._calculate_emergency_response_effectiveness(x, y, disaster.disaster_type)
                    actual_damage *= (1.0 - damage_reduction)
                    
                    # Apply damage to building/population
                    self._damage_tile(x, y, actual_damage, grid, sim_data)
    
    def _damage_tile(self, x: int, y: int, damage: float, grid, sim_data):
        """Apply damage to a specific tile"""
        if not (0 <= x < self.map_size and 0 <= y < self.map_size):
            return
        
        data = sim_data[y][x]
        
        # Reduce population
        population_loss = min(data.population, int(damage * random.uniform(0.1, 0.3)))
        data.population = max(0, data.population - population_loss)
        self.casualties += population_loss
        
        # Reduce building density (structural damage)
        if data.density > 0 and random.random() < damage * 0.1:
            data.density = max(0, data.density - 1)
            if data.density == 0:
                self.buildings_destroyed += 1
        
        # Economic damage
        damage_cost = int(damage * 100 * random.uniform(0.8, 1.2))
        self.total_damage_cost += damage_cost
    
    def _handle_disaster_spreading(self, disaster: DisasterEvent, grid, sim_data):
        """Handle disasters that can spread (fire, flood)"""
        if random.random() < disaster.spread_chance:
            # Find adjacent tiles that can catch fire/flood
            spread_candidates = []
            
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    if dx == 0 and dy == 0:
                        continue
                    
                    new_x = disaster.center_x + dx
                    new_y = disaster.center_y + dy
                    
                    if (0 <= new_x < self.map_size and 0 <= new_y < self.map_size):
                        # Check if tile is flammable/floodable
                        cell_type = grid[new_y][new_x]
                        if hasattr(cell_type, 'name') and any(zone in str(cell_type) for zone in ['RESIDENTIAL', 'COMMERCIAL', 'INDUSTRIAL']):
                            spread_candidates.append((new_x, new_y))
            
            if spread_candidates:
                # Create new disaster event at random adjacent tile
                new_x, new_y = random.choice(spread_candidates)
                spread_disaster_id = f"{disaster.disaster_type.value}_spread_{len(self.active_disasters)}"
                
                spread_disaster = DisasterEvent(
                    id=spread_disaster_id,
                    disaster_type=disaster.disaster_type,
                    severity=DisasterSeverity.MINOR,  # Spread disasters are weaker
                    center_x=new_x,
                    center_y=new_y,
                    radius=2,
                    duration=180,
                    remaining_duration=180,
                    damage_per_frame=disaster.damage_per_frame * 0.5,
                    spread_chance=disaster.spread_chance * 0.8  # Reduce spread chance
                )
                
                self.active_disasters[spread_disaster_id] = spread_disaster
    
    def _calculate_emergency_response_effectiveness(self, x: int, y: int, disaster_type: DisasterType) -> float:
        """Calculate emergency response effectiveness at position"""
        total_effectiveness = 0.0
        
        for service_pos, service in self.emergency_services.items():
            service_x, service_y = service_pos
            distance = math.sqrt((x - service_x)**2 + (y - service_y)**2)
            
            if distance <= service.response_radius and service.can_respond():
                # Effectiveness decreases with distance
                distance_factor = 1.0 - (distance / service.response_radius)
                effectiveness = service.get_effectiveness(disaster_type) * distance_factor
                total_effectiveness += effectiveness
        
        return min(0.8, total_effectiveness)  # Cap at 80% damage reduction
    
    def _update_emergency_response(self):
        """Update emergency service load based on active disasters"""
        # Reset all service loads
        for service in self.emergency_services.values():
            service.current_load = 0
        
        # Calculate load from active disasters
        for disaster in self.active_disasters.values():
            for service_pos, service in self.emergency_services.items():
                service_x, service_y = service_pos
                distance = math.sqrt((disaster.center_x - service_x)**2 + (disaster.center_y - service_y)**2)
                
                if distance <= service.response_radius:
                    # Service is responding to this disaster
                    load_increase = 1 if disaster.severity.value <= 2 else 2
                    service.current_load += load_increase
    
    def get_disaster_status(self) -> Dict:
        """Get disaster system status"""
        return {
            "active_disasters": len(self.active_disasters),
            "total_damage_cost": self.total_damage_cost,
            "buildings_destroyed": self.buildings_destroyed,
            "casualties": self.casualties,
            "warning_active": self.warning_active,
            "warning_message": self.warning_message if self.warning_active else "",
            "emergency_services": len(self.emergency_services),
            "disaster_cooldown": self.disaster_cooldown
        }
    
    def get_active_disasters(self) -> List[Dict]:
        """Get list of active disasters for UI"""
        disasters = []
        for disaster in self.active_disasters.values():
            disasters.append({
                "type": disaster.disaster_type.value,
                "severity": disaster.severity.name,
                "center": (disaster.center_x, disaster.center_y),
                "radius": disaster.radius,
                "remaining_time": disaster.remaining_duration // 60  # Convert to seconds
            })
        return disasters
    
    def draw_disaster_overlay(self, camera_x: int, camera_y: int, view_width: int, view_height: int):
        """Draw disaster effects on screen"""
        import pyxel
        
        for disaster in self.active_disasters.values():
            # Calculate screen position
            screen_x = (disaster.center_x * 8) - camera_x
            screen_y = (disaster.center_y * 8) - camera_y
            screen_radius = disaster.radius * 8
            
            # Only draw if on screen
            if (-screen_radius <= screen_x <= view_width + screen_radius and
                -screen_radius <= screen_y <= view_height + screen_radius):
                
                # Draw disaster effect
                disaster_colors = {
                    DisasterType.EARTHQUAKE: 8,  # Red
                    DisasterType.FIRE: 9,        # Orange
                    DisasterType.TYPHOON: 12,    # Blue
                    DisasterType.TSUNAMI: 1,     # Dark blue
                    DisasterType.FLOOD: 6,       # Light blue
                    DisasterType.VOLCANIC: 2     # Dark red
                }
                
                color = disaster_colors.get(disaster.disaster_type, 8)
                
                # Draw disaster area (pulsing effect)
                pulse = int(4 + 3 * math.sin(pyxel.frame_count * 0.2))
                pyxel.circb(screen_x, screen_y, screen_radius, color)
                
                if disaster.disaster_type == DisasterType.FIRE:
                    # Fire animation
                    for i in range(5):
                        fx = screen_x + random.randint(-screen_radius//2, screen_radius//2)
                        fy = screen_y + random.randint(-screen_radius//2, screen_radius//2)
                        pyxel.pset(fx, fy, random.choice([8, 9, 10]))
                
                elif disaster.disaster_type == DisasterType.EARTHQUAKE:
                    # Earthquake shake effect
                    shake = random.randint(-2, 2)
                    pyxel.line(screen_x - screen_radius + shake, screen_y, 
                             screen_x + screen_radius + shake, screen_y, 8)
                    pyxel.line(screen_x, screen_y - screen_radius + shake,
                             screen_x, screen_y + screen_radius + shake, 8)
        
        # Draw warning message
        if self.warning_active:
            pyxel.rect(10, 10, view_width - 20, 20, 8)  # Red background
            pyxel.rectb(10, 10, view_width - 20, 20, 7)  # White border
            pyxel.text(15, 15, self.warning_message[:50], 7)  # Truncate long messages