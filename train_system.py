#!/usr/bin/env python3
"""
Train System for ConcLand Mini
Manages train instances that run on rail networks between stations
"""

import random
from typing import List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
import math

class TrainDirection(Enum):
    NORTH = (0, -1)
    SOUTH = (0, 1)
    EAST = (1, 0)
    WEST = (-1, 0)

@dataclass
class Train:
    """Individual train instance"""
    id: int
    x: float  # Current position (float for smooth movement)
    y: float
    target_x: int  # Target tile position
    target_y: int
    direction: TrainDirection
    speed: float = 0.02  # Tiles per frame (slower speed)
    route: List[Tuple[int, int]] = None  # Current route
    route_index: int = 0
    origin_station: Tuple[int, int] = None
    destination_station: Tuple[int, int] = None
    passengers: int = 0
    max_passengers: int = 100
    
    def move(self):
        """Move train towards target"""
        if self.route and self.route_index < len(self.route):
            target = self.route[self.route_index]
            self.target_x, self.target_y = target
            
            # Calculate direction to target
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < 0.1:  # Reached target tile
                self.x = self.target_x
                self.y = self.target_y
                self.route_index += 1
                
                # Update direction for next segment
                if self.route_index < len(self.route):
                    next_target = self.route[self.route_index]
                    dx = next_target[0] - self.x
                    dy = next_target[1] - self.y
                    if abs(dx) > abs(dy):
                        self.direction = TrainDirection.EAST if dx > 0 else TrainDirection.WEST
                    else:
                        self.direction = TrainDirection.SOUTH if dy > 0 else TrainDirection.NORTH
            else:
                # Move towards target
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed

class TrainSystem:
    """Manages all trains in the city"""
    
    def __init__(self, grid, map_size):
        self.grid = grid
        self.map_size = map_size
        self.trains: List[Train] = []
        self.next_train_id = 0
        self.stations: List[Tuple[int, int]] = []
        self.rail_network: Set[Tuple[int, int]] = set()
        
    def update_network(self, grid, cell_types):
        """Update rail network and station positions"""
        self.stations.clear()
        self.rail_network.clear()
        station_centers = set()  # Track unique station centers
        
        for y in range(self.map_size):
            for x in range(self.map_size):
                cell_type = grid[y][x]
                if cell_type == cell_types['STATION']:
                    # For 3x3 stations, only register the top-left corner as station center
                    # Check if this is the top-left of a 3x3 station
                    is_top_left = True
                    if x > 0 and grid[y][x-1] == cell_types['STATION']:
                        is_top_left = False
                    if y > 0 and grid[y-1][x] == cell_types['STATION']:
                        is_top_left = False
                    
                    if is_top_left:
                        # Use center of 3x3 station (top-left + 1, + 1)
                        station_center = (x + 1, y + 1)
                        if station_center not in station_centers:
                            station_centers.add(station_center)
                            self.stations.append(station_center)
                elif cell_type == cell_types['RAIL']:
                    self.rail_network.add((x, y))
    
    def spawn_train(self, station_pos: Tuple[int, int]) -> Optional[Train]:
        """Spawn a new train at a station"""
        if not self.stations or len(self.stations) < 2:
            print(f"🚂 Cannot spawn train: need at least 2 stations, have {len(self.stations)}")
            return None
        
        # Find another station as destination
        other_stations = [s for s in self.stations if s != station_pos]
        if not other_stations:
            print(f"🚂 Cannot spawn train: no other stations available")
            return None
        
        destination = random.choice(other_stations)
        print(f"🚂 Finding route from {station_pos} to {destination}")
        
        # Find route between stations
        route = self.find_route(station_pos, destination)
        if not route:
            print(f"🚂 No route found from {station_pos} to {destination}")
            print(f"🚂 Rail network size: {len(self.rail_network)}")
            print(f"🚂 Stations: {self.stations}")
            return None
        
        # Create train
        train = Train(
            id=self.next_train_id,
            x=station_pos[0],
            y=station_pos[1],
            target_x=station_pos[0],
            target_y=station_pos[1],
            direction=TrainDirection.NORTH,
            route=route,
            route_index=0,
            origin_station=station_pos,
            destination_station=destination,
            passengers=random.randint(10, 80)
        )
        
        self.next_train_id += 1
        self.trains.append(train)
        print(f"🚂 Train {train.id} created: route has {len(route)} stops")
        return train
    
    def find_route(self, start: Tuple[int, int], end: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """Find route between two points using A* pathfinding"""
        from heapq import heappush, heappop
        
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        # Check if both points are accessible (stations or rails)
        start_valid = start in self.rail_network or start in [(s[0], s[1]) for s in self.stations]
        end_valid = end in self.rail_network or end in [(s[0], s[1]) for s in self.stations]
        
        if not start_valid or not end_valid:
            return None
        
        # A* pathfinding
        frontier = []
        heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while frontier:
            current_cost, current = heappop(frontier)
            
            if current == end:
                # Reconstruct path
                path = []
                while current is not None:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
            
            # Check neighbors
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                next_pos = (current[0] + dx, current[1] + dy)
                
                # Check bounds
                if not (0 <= next_pos[0] < self.map_size and 0 <= next_pos[1] < self.map_size):
                    continue
                
                # Allow movement on rails or to/from stations
                is_valid_move = False
                
                if next_pos == end:
                    # Always allow reaching the destination
                    is_valid_move = True
                elif next_pos in self.rail_network:
                    # Allow movement on rails
                    is_valid_move = True
                elif next_pos in [(s[0], s[1]) for s in self.stations]:
                    # Allow movement through stations (but penalize it to prefer rails)
                    is_valid_move = True
                
                if is_valid_move:
                    # Higher cost for going through stations (except destination)
                    move_cost = 1
                    if next_pos in [(s[0], s[1]) for s in self.stations] and next_pos != end:
                        move_cost = 3  # Discourage going through intermediate stations
                    
                    new_cost = cost_so_far[current] + move_cost
                    
                    if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                        cost_so_far[next_pos] = new_cost
                        priority = new_cost + heuristic(next_pos, end)
                        heappush(frontier, (priority, next_pos))
                        came_from[next_pos] = current
        
        return None  # No path found
    
    def update(self):
        """Update all trains"""
        trains_to_remove = []
        
        for train in self.trains:
            train.move()
            
            # Check if train reached destination
            if train.route_index >= len(train.route):
                # Train reached destination station
                trains_to_remove.append(train)
                
                # Optionally spawn a new train for return journey
                if random.random() < 0.7:  # 70% chance to return
                    self.spawn_train(train.destination_station)
        
        # Remove trains that completed their journey
        for train in trains_to_remove:
            self.trains.remove(train)
        
        # Spawn new trains at stations occasionally
        if random.random() < 0.02 and len(self.trains) < 10:  # Max 10 trains
            if self.stations:
                station = random.choice(self.stations)
                self.spawn_train(station)
    
    def get_trains_at_tile(self, x: int, y: int) -> List[Train]:
        """Get all trains at or near a specific tile"""
        trains_here = []
        for train in self.trains:
            if (abs(train.x - x) < 0.5 and abs(train.y - y) < 0.5):
                trains_here.append(train)
        return trains_here