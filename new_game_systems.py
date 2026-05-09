"""
New Game Systems Implementation for ConcLand
Water supply, underground development, crime, fire probability, and city status
"""
import random
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

class CityStatus(Enum):
    """City development status titles"""
    VILLAGE = "village"
    TOWN = "town"
    CITY = "city"
    METROPOLIS = "metropolis"
    MEGALOPOLIS = "megalopolis"

class CrimeLevel(Enum):
    """Crime levels"""
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    SEVERE = 3

@dataclass
class WaterSupplyData:
    """Water supply system data"""
    water_sources: List[Tuple[int, int]] = field(default_factory=list)  # (x, y) of pumps
    water_towers: List[Tuple[int, int]] = field(default_factory=list)
    pipes: List[Tuple[int, int, int, int]] = field(default_factory=list)  # (x1, y1, x2, y2)
    total_supply: int = 0
    total_demand: int = 0
    coverage: float = 0.0  # Percentage of buildings with water

@dataclass
class UndergroundData:
    """Underground development data"""
    subway_stations: List[Tuple[int, int]] = field(default_factory=list)
    subway_lines: List[List[Tuple[int, int]]] = field(default_factory=list)
    underground_depth: Dict[Tuple[int, int], int] = field(default_factory=dict)
    development_level: int = 0  # 0-5 scale

@dataclass
class CrimeData:
    """Crime statistics for an area"""
    crime_rate: float = 0.0  # 0.0 to 1.0
    crime_level: CrimeLevel = CrimeLevel.LOW
    arrest_rate: float = 0.0
    police_effectiveness: float = 0.0

@dataclass
class FireRiskData:
    """Fire risk assessment"""
    fire_hazard: float = 0.0  # 0.0 to 1.0
    fire_station_coverage: float = 0.0
    last_fire_date: Optional[int] = None  # Frame count
    fire_count: int = 0

@dataclass
class MilestoneData:
    """Milestone tracking"""
    population: int = 0
    funds: int = 0
    buildings_count: int = 0
    satisfaction: float = 0.0
    achievements: List[str] = field(default_factory=list)

class WaterSupplySystem:
    """Manages water supply and distribution"""
    def __init__(self, map_size: int):
        self.map_size = map_size
        self.data = WaterSupplyData()
        self.water_grid = [[0.0 for _ in range(map_size)] for _ in range(map_size)]

    def add_water_source(self, x: int, y: int, capacity: int = 100):
        """Add a water source (pump/well)"""
        if (x, y) not in self.data.water_sources:
            self.data.water_sources.append((x, y))
            self.data.total_supply += capacity
            self._update_water_coverage()

    def remove_water_source(self, x: int, y: int, capacity: int = 100):
        """Remove a water source"""
        if (x, y) in self.data.water_sources:
            self.data.water_sources.remove((x, y))
            self.data.total_supply -= capacity
            self._update_water_coverage()

    def add_pipe(self, x1: int, y1: int, x2: int, y2: int):
        """Add water pipe connection"""
        if (x1, y1, x2, y2) not in self.data.pipes:
            self.data.pipes.append((x1, y1, x2, y2))
            self._update_water_coverage()

    def _update_water_coverage(self):
        """Update water coverage across the map"""
        # Reset coverage
        for y in range(self.map_size):
            for x in range(self.map_size):
                self.water_grid[y][x] = 0.0

        # Simple propagation from water sources
        for source_x, source_y in self.data.water_sources:
            self._propagate_water(source_x, source_y, 10)  # 10 tile radius

        # Calculate coverage percentage
        covered_tiles = sum(1 for y in range(self.map_size) for x in range(self.map_size) if self.water_grid[y][x] > 0)
        total_tiles = self.map_size * self.map_size
        self.data.coverage = covered_tiles / total_tiles if total_tiles > 0 else 0.0

    def _propagate_water(self, start_x: int, start_y: int, radius: int):
        """Propagate water from source"""
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                x, y = start_x + dx, start_y + dy
                if 0 <= x < self.map_size and 0 <= y < self.map_size:
                    distance = math.sqrt(dx * dx + dy * dy)
                    if distance <= radius:
                        # Water pressure decreases with distance
                        pressure = 1.0 - (distance / radius)
                        self.water_grid[y][x] = max(self.water_grid[y][x], pressure)

    def has_water_at(self, x: int, y: int) -> bool:
        """Check if position has water supply"""
        return 0 <= x < self.map_size and 0 <= y < self.map_size and self.water_grid[y][x] > 0.1

    def get_supply_status(self) -> Tuple[bool, float]:
        """Get overall supply status"""
        return (self.data.total_supply >= self.data.total_demand, self.data.coverage)

class UndergroundSystem:
    """Manages underground development (subway, utilities, etc.)"""
    def __init__(self, map_size: int):
        self.map_size = map_size
        self.data = UndergroundData()
        self.underground_grid = [[None for _ in range(map_size)] for _ in range(map_size)]

    def add_subway_station(self, x: int, y: int):
        """Add a subway station"""
        if (x, y) not in self.data.subway_stations:
            self.data.subway_stations.append((x, y))
            self.underground_grid[y][x] = "subway_station"

    def dig_underground(self, x: int, y: int, depth: int):
        """Dig underground at location"""
        if 0 <= x < self.map_size and 0 <= y < self.map_size:
            current_depth = self.data.underground_depth.get((x, y), 0)
            if depth > current_depth:
                self.data.underground_depth[(x, y)] = depth
                self.data.development_level = min(5, self.data.development_level + 1)

    def get_underground_level(self, x: int, y: int) -> int:
        """Get underground development level at position"""
        return self.data.underground_depth.get((x, y), 0)

    def has_subway_access(self, x: int, y: int) -> bool:
        """Check if position has subway access nearby"""
        for station_x, station_y in self.data.subway_stations:
            distance = math.sqrt((x - station_x) ** 2 + (y - station_y) ** 2)
            if distance <= 5:  # 5 tile radius
                return True
        return False

class CrimeSystem:
    """Manages crime simulation and prevention"""
    def __init__(self, map_size: int):
        self.map_size = map_size
        self.crime_grid = [[CrimeData() for _ in range(map_size)] for _ in range(map_size)]
        self.police_stations = []

    def add_police_station(self, x: int, y: int, coverage_radius: int = 10):
        """Add a police station"""
        self.police_stations.append((x, y, coverage_radius))
        self._update_crime_rates()

    def _update_crime_rates(self):
        """Update crime rates across the map"""
        for y in range(self.map_size):
            for x in range(self.map_size):
                # Base crime factors
                population_density = random.random()
                unemployment = random.random()
                education = random.random()

                # Police protection
                police_protection = 0.0
                for station_x, station_y, radius in self.police_stations:
                    distance = math.sqrt((x - station_x) ** 2 + (y - station_y) ** 2)
                    if distance <= radius:
                        police_protection = max(police_protection, 1.0 - (distance / radius))

                # Calculate crime rate
                crime_rate = (population_density * 0.3 + unemployment * 0.4 +
                             (1.0 - education) * 0.2 + (1.0 - police_protection) * 0.5)
                crime_rate = max(0.0, min(1.0, crime_rate))

                # Determine crime level
                if crime_rate < 0.25:
                    crime_level = CrimeLevel.LOW
                elif crime_rate < 0.5:
                    crime_level = CrimeLevel.MEDIUM
                elif crime_rate < 0.75:
                    crime_level = CrimeLevel.HIGH
                else:
                    crime_level = CrimeLevel.SEVERE

                self.crime_grid[y][x] = CrimeData(
                    crime_rate=crime_rate,
                    crime_level=crime_level,
                    arrest_rate=police_protection * 0.8,
                    police_effectiveness=police_protection
                )

    def get_crime_level(self, x: int, y: int) -> CrimeLevel:
        """Get crime level at position"""
        if 0 <= x < self.map_size and 0 <= y < self.map_size:
            return self.crime_grid[y][x].crime_level
        return CrimeLevel.MEDIUM

    def simulate_crime_event(self, x: int, y: int) -> bool:
        """Simulate a crime event at position"""
        crime_data = self.crime_grid[y][x] if 0 <= y < self.map_size and 0 <= x < self.map_size else None

        if crime_data:
            # Crime occurs based on crime rate
            return random.random() < crime_data.crime_rate * 0.01  # 1% base chance
        return False

class FireSystem:
    """Manages fire risk and response"""
    def __init__(self, map_size: int):
        self.map_size = map_size
        self.fire_grid = [[FireRiskData() for _ in range(map_size)] for _ in range(map_size)]
        self.fire_stations = []

    def add_fire_station(self, x: int, y: int, coverage_radius: int = 10):
        """Add a fire station"""
        self.fire_stations.append((x, y, coverage_radius))
        self._update_fire_risks()

    def _update_fire_risks(self):
        """Update fire risks across the map"""
        for y in range(self.map_size):
            for x in range(self.map_size):
                # Base risk factors
                building_density = random.random()
                industrial_proximity = random.random()
                fire_station_proximity = 0.0

                # Fire station protection
                for station_x, station_y, radius in self.fire_stations:
                    distance = math.sqrt((x - station_x) ** 2 + (y - station_y) ** 2)
                    if distance <= radius:
                        fire_station_proximity = max(fire_station_proximity,
                                                     1.0 - (distance / radius))

                # Calculate fire risk
                fire_risk = (building_density * 0.3 + industrial_proximity * 0.4 +
                           (1.0 - fire_station_proximity) * 0.6)
                fire_risk = max(0.0, min(1.0, fire_risk))

                self.fire_grid[y][x] = FireRiskData(
                    fire_hazard=fire_risk,
                    fire_station_coverage=fire_station_proximity
                )

    def get_fire_risk(self, x: int, y: int) -> float:
        """Get fire risk at position"""
        if 0 <= x < self.map_size and 0 <= y < self.map_size:
            return self.fire_grid[y][x].fire_hazard
        return 0.5

    def simulate_fire(self, x: int, y: int) -> bool:
        """Simulate fire occurrence at position"""
        fire_data = self.fire_grid[y][x] if 0 <= y < self.map_size and 0 <= x < self.map_size else None

        if fire_data:
            # Fire occurs based on risk
            fire_chance = fire_data.fire_hazard * 0.005  # 0.5% base chance
            if random.random() < fire_chance:
                fire_data.fire_count += 1
                fire_data.last_fire_date = random.randint(0, 1000000)
                return True
        return False

class CityStatusSystem:
    """Manages city status titles and milestones"""
    def __init__(self):
        self.milestones = self._init_milestones()
        self.achievements = []
        self.current_status = CityStatus.VILLAGE

    def _init_milestones(self) -> Dict[CityStatus, Dict]:
        """Initialize milestone requirements"""
        return {
            CityStatus.VILLAGE: {
                "population": 0,
                "buildings": 0,
                "funds": 0
            },
            CityStatus.TOWN: {
                "population": 500,
                "buildings": 50,
                "funds": 10000
            },
            CityStatus.CITY: {
                "population": 5000,
                "buildings": 200,
                "funds": 100000
            },
            CityStatus.METROPOLIS: {
                "population": 50000,
                "buildings": 1000,
                "funds": 1000000
            },
            CityStatus.MEGALOPOLIS: {
                "population": 500000,
                "buildings": 5000,
                "funds": 10000000
            }
        }

    def update_status(self, population: int, buildings: int, funds: int) -> CityStatus:
        """Update city status based on metrics"""
        # Check each status level
        for status in [CityStatus.MEGALOPOLIS, CityStatus.METROPOLIS,
                      CityStatus.CITY, CityStatus.TOWN, CityStatus.VILLAGE]:
            requirements = self.milestones[status]
            if (population >= requirements["population"] and
                buildings >= requirements["buildings"] and
                funds >= requirements["funds"]):
                new_status = status
                if new_status != self.current_status:
                    self.current_status = new_status
                    self._check_achievements(population, buildings, funds)
                return self.current_status

        return self.current_status

    def _check_achievements(self, population: int, buildings: int, funds: int):
        """Check for new achievements"""
        achievements = [
            ("first_settler", population >= 1, "最初の入植者"),
            ("growing_community", population >= 100, "成長する共同体"),
            ("boom_town", population >= 1000, "ブームタウン"),
            ("urban_sprawl", population >= 10000, "都市圏"),
            ("metropolis", population >= 100000, "大都市"),
            ("megalopolis", population >= 1000000, "メガロポリス"),
            ("wealthy_city", funds >= 1000000, "裕福な都市"),
            ("building_spree", buildings >= 500, "建設ラッシュ"),
        ]

        for achievement_id, condition, jp_name in achievements:
            if condition and achievement_id not in self.achievements:
                self.achievements.append(achievement_id)
                # Trigger notification or callback here
                return achievement_id, jp_name

        return None

    def get_status_title(self, status: CityStatus) -> Tuple[str, str]:
        """Get status title in both languages"""
        titles = {
            CityStatus.VILLAGE: ("Village", "村"),
            CityStatus.TOWN: ("Town", "町"),
            CityStatus.CITY: ("City", "市"),
            CityStatus.METROPOLIS: ("Metropolis", "大都市"),
            CityStatus.MEGALOPOLIS: ("Megalopolis", "メガロポリス")
        }
        return titles.get(status, ("Unknown", "不明"))

    def get_next_milestone(self, current_status: CityStatus) -> Optional[Dict]:
        """Get requirements for next status level"""
        status_order = [CityStatus.VILLAGE, CityStatus.TOWN, CityStatus.CITY,
                       CityStatus.METROPOLIS, CityStatus.MEGALOPOLIS]

        try:
            current_index = status_order.index(current_status)
            if current_index < len(status_order) - 1:
                next_status = status_order[current_index + 1]
                return self.milestones[next_status]
        except ValueError:
            pass

        return None

class NewGameSystems:
    """Integrates all new game systems"""
    def __init__(self, map_size: int):
        self.map_size = map_size

        # Individual systems
        self.water_supply = WaterSupplySystem(map_size)
        self.underground = UndergroundSystem(map_size)
        self.crime = CrimeSystem(map_size)
        self.fire = FireSystem(map_size)
        self.city_status = CityStatusSystem()

        # Shared data
        self.population = 0
        self.buildings_count = 0
        self.funds = 5000

    def update(self, grid, sim_data):
        """Update all systems"""
        # Update city status
        self.city_status.update_status(self.population, self.buildings_count, self.funds)

        # Periodic updates (less frequent for performance)
        if random.random() < 0.01:  # 1% chance per frame
            self.crime._update_crime_rates()
            self.fire._update_fire_risks()

    def get_system_status(self) -> Dict:
        """Get status of all systems"""
        return {
            "water": {
                "supply": self.water_supply.data.total_supply,
                "demand": self.water_supply.data.total_demand,
                "coverage": self.water_supply.data.coverage * 100
            },
            "underground": {
                "stations": len(self.underground.data.subway_stations),
                "development_level": self.underground.data.development_level
            },
            "crime": {
                "level": self.city_status.current_status.value
            },
            "fire": {
                "stations": len(self.fire.fire_stations),
                "fires_total": sum(data.fire_count for row in self.fire.fire_grid for data in row)
            },
            "city_status": {
                "current": self.city_status.get_status_title(self.city_status.current_status),
                "achievements": len(self.city_status.achievements)
            }
        }

# Example usage
if __name__ == "__main__":
    # Test new systems
    systems = NewGameSystems(100)

    # Add some infrastructure
    systems.water_supply.add_water_source(50, 50, 100)
    systems.underground.add_subway_station(50, 50)
    systems.crime.add_police_station(50, 50, 10)
    systems.fire.add_fire_station(50, 50, 10)

    # Set metrics
    systems.population = 1000
    systems.buildings_count = 150
    systems.funds = 50000

    # Update systems
    systems.update(None, None)

    # Get status
    status = systems.get_system_status()
    print("System Status:")
    for system_name, system_data in status.items():
        print(f"  {system_name}: {system_data}")

    print(f"\nCity Status: {systems.city_status.get_status_title(systems.city_status.current_status)}")
