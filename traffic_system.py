"""
Advanced Traffic Management System for ConcLand
Handles buses, traffic lights, congestion optimization, and route planning
"""
import random
import math
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from collections import defaultdict, deque
from enum import Enum

class TrafficLightState(Enum):
    RED = 0
    YELLOW = 1
    GREEN = 2

class TransportType(Enum):
    PEDESTRIAN = 0
    CAR = 1
    BUS = 2
    TRAIN = 3
    BICYCLE = 4

@dataclass
class TrafficLight:
    """Traffic light with timing system"""
    x: int
    y: int
    state: TrafficLightState
    timer: int
    green_duration: int = 120  # 2 seconds at 60 FPS
    yellow_duration: int = 30   # 0.5 seconds
    red_duration: int = 90      # 1.5 seconds
    
    def update(self):
        """Update traffic light state"""
        self.timer -= 1
        if self.timer <= 0:
            if self.state == TrafficLightState.GREEN:
                self.state = TrafficLightState.YELLOW
                self.timer = self.yellow_duration
            elif self.state == TrafficLightState.YELLOW:
                self.state = TrafficLightState.RED
                self.timer = self.red_duration
            else:  # RED
                self.state = TrafficLightState.GREEN
                self.timer = self.green_duration

@dataclass
class BusStop:
    """Bus stop with passenger queue"""
    x: int
    y: int
    route_id: str
    passengers_waiting: int = 0
    max_capacity: int = 20
    
    def add_passengers(self, count: int) -> int:
        """Add passengers, returns actual number added"""
        space = self.max_capacity - self.passengers_waiting
        actual = min(count, space)
        self.passengers_waiting += actual
        return actual
    
    def pickup_passengers(self, bus_capacity: int) -> int:
        """Bus picks up passengers, returns number picked up"""
        pickup = min(self.passengers_waiting, bus_capacity)
        self.passengers_waiting -= pickup
        return pickup

@dataclass
class Bus:
    """Bus vehicle with route and schedule"""
    id: str
    route_id: str
    current_x: int
    current_y: int
    target_x: int
    target_y: int
    passengers: int = 0
    max_capacity: int = 40
    speed: float = 2.0
    next_stop_index: int = 0
    waiting_timer: int = 0
    
    def move_towards_target(self):
        """Move bus towards target"""
        if self.waiting_timer > 0:
            self.waiting_timer -= 1
            return
        
        dx = self.target_x - self.current_x
        dy = self.target_y - self.current_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance <= self.speed:
            self.current_x = self.target_x
            self.current_y = self.target_y
        else:
            self.current_x += int((dx / distance) * self.speed)
            self.current_y += int((dy / distance) * self.speed)

@dataclass
class BusRoute:
    """Bus route with stops and schedule"""
    id: str
    name: str
    japanese_name: str
    stops: List[Tuple[int, int]]  # (x, y) coordinates
    frequency: int  # Minutes between buses
    color: Tuple[int, int, int]
    active: bool = True

class TrafficFlowAnalyzer:
    """Analyzes and optimizes traffic flow"""
    
    def __init__(self, map_size: int):
        self.map_size = map_size
        self.flow_data: Dict[Tuple[int, int], int] = {}
        self.congestion_map: Dict[Tuple[int, int], float] = {}
        self.bottlenecks: List[Tuple[int, int]] = []
        
    def record_traffic(self, x: int, y: int, vehicle_count: int):
        """Record traffic at position"""
        pos = (x, y)
        if pos not in self.flow_data:
            self.flow_data[pos] = 0
        self.flow_data[pos] += vehicle_count
        
    def calculate_congestion(self):
        """Calculate congestion levels"""
        self.congestion_map.clear()
        self.bottlenecks.clear()
        
        for pos, flow in self.flow_data.items():
            # Simple congestion calculation based on flow
            congestion = min(1.0, flow / 100.0)
            self.congestion_map[pos] = congestion
            
            # Mark bottlenecks
            if congestion > 0.7:
                self.bottlenecks.append(pos)
        
        # Clear flow data for next analysis
        self.flow_data.clear()
    
    def get_congestion_at(self, x: int, y: int) -> float:
        """Get congestion level at position"""
        return self.congestion_map.get((x, y), 0.0)
    
    def suggest_improvements(self) -> List[Dict]:
        """Suggest traffic improvements"""
        suggestions = []
        
        for x, y in self.bottlenecks:
            suggestions.append({
                'type': 'traffic_light',
                'position': (x, y),
                'reason': 'High congestion detected',
                'cost': 500
            })
            
            # Suggest road expansion
            suggestions.append({
                'type': 'road_expansion',
                'position': (x, y),
                'reason': 'Bottleneck requires more capacity',
                'cost': 200
            })
        
        return suggestions

class AdvancedTrafficSystem:
    """Advanced traffic management system"""
    
    def __init__(self, map_size: int):
        self.map_size = map_size
        
        # Traffic infrastructure
        self.traffic_lights: Dict[Tuple[int, int], TrafficLight] = {}
        self.bus_stops: Dict[Tuple[int, int], BusStop] = {}
        self.bus_routes: Dict[str, BusRoute] = {}
        self.buses: Dict[str, Bus] = {}
        
        # Analysis
        self.flow_analyzer = TrafficFlowAnalyzer(map_size)
        
        # Pathfinding cache
        self.path_cache: Dict[Tuple[int, int, int, int], List[Tuple[int, int]]] = {}
        
        # Initialize with sample routes
        self._create_sample_routes()
        
    def _create_sample_routes(self):
        """Create sample bus routes"""
        # Route 1: East-West
        route1 = BusRoute(
            id="route_1",
            name="East-West Line",
            japanese_name="東西線",
            stops=[(10, 50), (30, 50), (50, 50), (70, 50), (90, 50)],
            frequency=5,  # 5 minutes
            color=(255, 100, 100)
        )
        self.bus_routes["route_1"] = route1
        
        # Route 2: North-South
        route2 = BusRoute(
            id="route_2", 
            name="North-South Line",
            japanese_name="南北線",
            stops=[(50, 10), (50, 30), (50, 50), (50, 70), (50, 90)],
            frequency=8,  # 8 minutes
            color=(100, 255, 100)
        )
        self.bus_routes["route_2"] = route2
        
        # Create bus stops
        for route in self.bus_routes.values():
            for x, y in route.stops:
                if (x, y) not in self.bus_stops:
                    self.bus_stops[(x, y)] = BusStop(x, y, route.id)
    
    def add_traffic_light(self, x: int, y: int):
        """Add traffic light at position"""
        if (x, y) not in self.traffic_lights:
            self.traffic_lights[(x, y)] = TrafficLight(
                x, y, TrafficLightState.GREEN, 120
            )
            return True
        return False
    
    def remove_traffic_light(self, x: int, y: int):
        """Remove traffic light at position"""
        pos = (x, y)
        if pos in self.traffic_lights:
            del self.traffic_lights[pos]
            return True
        return False
    
    def add_bus_stop(self, x: int, y: int, route_id: str):
        """Add bus stop for route"""
        pos = (x, y)
        if pos not in self.bus_stops:
            self.bus_stops[pos] = BusStop(x, y, route_id)
            return True
        return False
    
    def spawn_bus(self, route_id: str) -> bool:
        """Spawn new bus on route"""
        if route_id not in self.bus_routes:
            return False
            
        route = self.bus_routes[route_id]
        if not route.active or len(route.stops) < 2:
            return False
        
        # Create bus at first stop
        start_x, start_y = route.stops[0]
        target_x, target_y = route.stops[1]
        
        bus_id = f"{route_id}_bus_{len(self.buses)}"
        bus = Bus(
            id=bus_id,
            route_id=route_id,
            current_x=start_x,
            current_y=start_y,
            target_x=target_x,
            target_y=target_y,
            next_stop_index=1
        )
        
        self.buses[bus_id] = bus
        return True
    
    def update(self, grid, sim_data):
        """Update traffic system"""
        # Update traffic lights
        for light in self.traffic_lights.values():
            light.update()
        
        # Update buses
        self._update_buses(grid)
        
        # Generate passenger demand
        self._generate_passenger_demand(sim_data)
        
        # Analyze traffic flow
        self._analyze_traffic_flow(grid, sim_data)
        
        # Update congestion
        self.flow_analyzer.calculate_congestion()
    
    def _update_buses(self, grid):
        """Update all buses"""
        for bus in list(self.buses.values()):
            # Move towards target
            bus.move_towards_target()
            
            # Check if reached target
            if bus.current_x == bus.target_x and bus.current_y == bus.target_y:
                self._handle_bus_at_stop(bus, grid)
    
    def _handle_bus_at_stop(self, bus: Bus, grid):
        """Handle bus arriving at stop"""
        route = self.bus_routes[bus.route_id]
        
        # Pickup passengers at current stop
        stop_pos = (bus.current_x, bus.current_y)
        if stop_pos in self.bus_stops:
            stop = self.bus_stops[stop_pos]
            available_space = bus.max_capacity - bus.passengers
            picked_up = stop.pickup_passengers(available_space)
            bus.passengers += picked_up
        
        # Set next target
        bus.next_stop_index = (bus.next_stop_index + 1) % len(route.stops)
        next_x, next_y = route.stops[bus.next_stop_index]
        bus.target_x = next_x
        bus.target_y = next_y
        
        # Wait at stop
        bus.waiting_timer = 30  # 0.5 seconds
    
    def _generate_passenger_demand(self, sim_data):
        """Generate passenger demand at bus stops"""
        for pos, stop in self.bus_stops.items():
            x, y = pos
            if 0 <= x < self.map_size and 0 <= y < self.map_size:
                # Generate passengers based on nearby population
                nearby_population = 0
                for dy in range(-3, 4):
                    for dx in range(-3, 4):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.map_size and 0 <= ny < self.map_size:
                            nearby_population += sim_data[ny][nx].population
                
                # Random passenger generation
                if nearby_population > 0 and random.random() < 0.1:
                    passengers = random.randint(1, 3)
                    stop.add_passengers(passengers)
    
    def _analyze_traffic_flow(self, grid, sim_data):
        """Analyze traffic flow patterns"""
        # Simulate vehicle movement between zones
        for y in range(self.map_size):
            for x in range(self.map_size):
                data = sim_data[y][x]

                # Record traffic based on population (employment not in SimData)
                vehicle_count = int(data.population * 0.15)  # Slightly higher to compensate
                if vehicle_count > 0:
                    self.flow_analyzer.record_traffic(x, y, vehicle_count)
    
    def find_path(self, start_x: int, start_y: int, end_x: int, end_y: int, grid) -> List[Tuple[int, int]]:
        """Find path using A* with traffic consideration"""
        cache_key = (start_x, start_y, end_x, end_y)
        if cache_key in self.path_cache:
            return self.path_cache[cache_key]
        
        # A* pathfinding with traffic weights
        start = (start_x, start_y)
        goal = (end_x, end_y)
        
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self._heuristic(start, goal)}
        
        while open_set:
            current = min(open_set, key=lambda x: f_score.get(x[1], float('inf')))[1]
            open_set = [item for item in open_set if item[1] != current]
            
            if current == goal:
                path = self._reconstruct_path(came_from, current)
                self.path_cache[cache_key] = path
                return path
            
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                if not self._is_valid_position(neighbor[0], neighbor[1], grid):
                    continue
                
                # Calculate cost with traffic consideration
                traffic_weight = 1.0 + self.flow_analyzer.get_congestion_at(neighbor[0], neighbor[1])
                tentative_g = g_score.get(current, float('inf')) + traffic_weight
                
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self._heuristic(neighbor, goal)
                    
                    if neighbor not in [item[1] for item in open_set]:
                        open_set.append((f_score[neighbor], neighbor))
        
        return []  # No path found
    
    def _heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """Manhattan distance heuristic"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def _reconstruct_path(self, came_from: Dict, current: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Reconstruct path from A* search"""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return path[::-1]
    
    def _is_valid_position(self, x: int, y: int, grid) -> bool:
        """Check if position is valid for pathfinding"""
        if not (0 <= x < self.map_size and 0 <= y < self.map_size):
            return False
        
        # Allow movement on roads, rails, and through buildings
        from concland_mini import CellType
        cell_type = grid[y][x]
        return cell_type in [
            CellType.ROAD, CellType.RAIL, CellType.RESIDENTIAL, 
            CellType.COMMERCIAL, CellType.INDUSTRIAL
        ]
    
    def get_traffic_status(self) -> Dict:
        """Get overall traffic system status"""
        total_buses = len(self.buses)
        active_routes = len([r for r in self.bus_routes.values() if r.active])
        total_passengers = sum(bus.passengers for bus in self.buses.values())
        waiting_passengers = sum(stop.passengers_waiting for stop in self.bus_stops.values())
        avg_congestion = sum(self.flow_analyzer.congestion_map.values()) / max(len(self.flow_analyzer.congestion_map), 1)
        
        return {
            "total_buses": total_buses,
            "active_routes": active_routes,
            "total_passengers": total_passengers,
            "waiting_passengers": waiting_passengers,
            "average_congestion": avg_congestion,
            "bottlenecks": len(self.flow_analyzer.bottlenecks),
            "traffic_lights": len(self.traffic_lights)
        }
    
    def get_improvement_suggestions(self) -> List[Dict]:
        """Get traffic improvement suggestions"""
        return self.flow_analyzer.suggest_improvements()
    
    def draw_traffic_overlay(self, tile_manager, camera_x: int, camera_y: int, view_width: int, view_height: int):
        """Draw traffic system overlay"""
        # Draw bus routes
        for route in self.bus_routes.values():
            if route.active:
                self._draw_bus_route(tile_manager, route, camera_x, camera_y, view_width, view_height)
        
        # Draw bus stops
        for pos, stop in self.bus_stops.items():
            self._draw_bus_stop(tile_manager, stop, camera_x, camera_y)
        
        # Draw buses
        for bus in self.buses.values():
            self._draw_bus(tile_manager, bus, camera_x, camera_y)
        
        # Draw traffic lights
        for light in self.traffic_lights.values():
            self._draw_traffic_light(tile_manager, light, camera_x, camera_y)
    
    def _draw_bus_route(self, tile_manager, route: BusRoute, camera_x: int, camera_y: int, view_width: int, view_height: int):
        """Draw bus route line"""
        import pyxel
        
        stops = route.stops
        for i in range(len(stops) - 1):
            x1, y1 = stops[i]
            x2, y2 = stops[i + 1]
            
            screen_x1 = (x1 * 8) - camera_x
            screen_y1 = (y1 * 8) - camera_y
            screen_x2 = (x2 * 8) - camera_x
            screen_y2 = (y2 * 8) - camera_y
            
            # Only draw if on screen
            if (-10 <= screen_x1 <= view_width + 10 and -10 <= screen_y1 <= view_height + 10 and
                -10 <= screen_x2 <= view_width + 10 and -10 <= screen_y2 <= view_height + 10):
                pyxel.line(screen_x1 + 4, screen_y1 + 4, screen_x2 + 4, screen_y2 + 4, 8)  # Yellow line
    
    def _draw_bus_stop(self, tile_manager, stop: BusStop, camera_x: int, camera_y: int):
        """Draw bus stop"""
        import pyxel
        
        screen_x = (stop.x * 8) - camera_x
        screen_y = (stop.y * 8) - camera_y
        
        # Bus stop icon
        pyxel.rect(screen_x + 2, screen_y + 2, 4, 4, 1)  # Blue square
        
        # Show waiting passengers
        if stop.passengers_waiting > 0:
            pyxel.text(screen_x, screen_y - 6, str(stop.passengers_waiting), 7)
    
    def _draw_bus(self, tile_manager, bus: Bus, camera_x: int, camera_y: int):
        """Draw bus"""
        import pyxel
        
        screen_x = (bus.current_x * 8) - camera_x
        screen_y = (bus.current_y * 8) - camera_y
        
        # Bus body
        pyxel.rect(screen_x + 1, screen_y + 1, 6, 6, 6)  # Light blue
        pyxel.rect(screen_x + 2, screen_y + 2, 4, 4, 12)  # Blue
        
        # Show passenger count
        if bus.passengers > 0:
            pyxel.text(screen_x, screen_y - 6, str(bus.passengers), 7)
    
    def _draw_traffic_light(self, tile_manager, light: TrafficLight, camera_x: int, camera_y: int):
        """Draw traffic light"""
        import pyxel
        
        screen_x = (light.x * 8) - camera_x
        screen_y = (light.y * 8) - camera_y
        
        # Light color based on state
        color = {
            TrafficLightState.GREEN: 11,  # Green
            TrafficLightState.YELLOW: 10,  # Yellow
            TrafficLightState.RED: 8       # Red
        }[light.state]
        
        pyxel.rect(screen_x + 3, screen_y + 3, 2, 2, color)