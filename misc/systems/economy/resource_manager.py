"""
Resource Management System for ConcLand
Handles resource production, consumption, storage, and trading
"""
import json
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Resource:
    """Represents a game resource"""
    id: str
    name: str
    japanese_name: str
    category: str
    description: str
    base_price: float
    storage_decay: float
    color: tuple
    icon_index: int
    availability: Dict[str, Any]
    production: Dict[str, Any]
    consumption: Dict[str, Any]

class ResourceStorage:
    """Manages resource storage and decay"""
    
    def __init__(self, capacity: int = 10000):
        self.resources: Dict[str, float] = defaultdict(float)
        self.capacity = capacity
        self.decay_rates: Dict[str, float] = {}
    
    def add_resource(self, resource_id: str, amount: float) -> float:
        """Add resource to storage, returns amount actually added"""
        if amount <= 0:
            return 0
        
        current_total = sum(self.resources.values())
        available_space = max(0, self.capacity - current_total)
        
        actual_amount = min(amount, available_space)
        self.resources[resource_id] += actual_amount
        
        return actual_amount
    
    def remove_resource(self, resource_id: str, amount: float) -> float:
        """Remove resource from storage, returns amount actually removed"""
        if amount <= 0 or resource_id not in self.resources:
            return 0
        
        available = self.resources[resource_id]
        actual_amount = min(amount, available)
        
        self.resources[resource_id] -= actual_amount
        if self.resources[resource_id] <= 0:
            del self.resources[resource_id]
        
        return actual_amount
    
    def get_resource(self, resource_id: str) -> float:
        """Get current amount of resource"""
        return self.resources.get(resource_id, 0)
    
    def apply_decay(self, resource_definitions: Dict[str, Resource]):
        """Apply storage decay to all resources"""
        for resource_id, amount in list(self.resources.items()):
            if resource_id in resource_definitions:
                decay_rate = resource_definitions[resource_id].storage_decay
                decay_amount = amount * decay_rate
                self.remove_resource(resource_id, decay_amount)
    
    def get_total_storage_used(self) -> float:
        """Get total storage space used"""
        return sum(self.resources.values())
    
    def get_storage_utilization(self) -> float:
        """Get storage utilization as percentage (0.0 to 1.0)"""
        return self.get_total_storage_used() / self.capacity

class MarketSystem:
    """Handles resource trading and price dynamics"""
    
    def __init__(self):
        self.prices: Dict[str, float] = {}
        self.price_history: Dict[str, List[float]] = defaultdict(list)
        self.supply: Dict[str, float] = defaultdict(float)
        self.demand: Dict[str, float] = defaultdict(float)
        self.trade_routes: Dict[str, Dict] = {}
    
    def update_prices(self, resource_definitions: Dict[str, Resource]):
        """Update resource prices based on supply and demand"""
        for resource_id, resource in resource_definitions.items():
            base_price = resource.base_price
            
            # Calculate supply/demand ratio
            supply = self.supply.get(resource_id, 1.0)
            demand = self.demand.get(resource_id, 1.0)
            
            # Avoid division by zero
            if supply == 0:
                supply = 0.1
            
            ratio = demand / supply
            
            # Price adjustment based on ratio
            price_modifier = 1.0
            if ratio > 1.5:  # High demand, low supply
                price_modifier = 1.0 + (ratio - 1.0) * 0.3
            elif ratio < 0.5:  # Low demand, high supply
                price_modifier = max(0.3, 1.0 - (1.0 - ratio) * 0.5)
            
            # Add some random volatility
            volatility = 0.1  # 10% random variation
            random_factor = 1.0 + random.uniform(-volatility, volatility)
            
            new_price = base_price * price_modifier * random_factor
            self.prices[resource_id] = max(1.0, new_price)  # Minimum price of 1
            
            # Update price history
            self.price_history[resource_id].append(new_price)
            if len(self.price_history[resource_id]) > 100:  # Keep last 100 prices
                self.price_history[resource_id].pop(0)
    
    def get_price(self, resource_id: str) -> float:
        """Get current market price of resource"""
        return self.prices.get(resource_id, 100.0)
    
    def buy_resource(self, resource_id: str, amount: float, funds: float) -> Tuple[float, float]:
        """Buy resource from market. Returns (amount_bought, cost)"""
        if amount <= 0 or funds <= 0:
            return 0, 0
        
        price = self.get_price(resource_id)
        max_affordable = funds / price
        actual_amount = min(amount, max_affordable)
        total_cost = actual_amount * price
        
        # Update market supply (buying reduces supply)
        self.supply[resource_id] = max(0, self.supply[resource_id] - actual_amount)
        
        return actual_amount, total_cost
    
    def sell_resource(self, resource_id: str, amount: float) -> float:
        """Sell resource to market. Returns revenue"""
        if amount <= 0:
            return 0
        
        price = self.get_price(resource_id)
        revenue = amount * price * 0.8  # Sell at 80% of market price
        
        # Update market supply (selling increases supply)
        self.supply[resource_id] += amount
        
        return revenue

class ResourceManager:
    """Main resource management system"""
    
    def __init__(self):
        self.resources: Dict[str, Resource] = {}
        self.storage = ResourceStorage()
        self.market = MarketSystem()
        
        # Production and consumption tracking
        self.production_rates: Dict[str, float] = defaultdict(float)
        self.consumption_rates: Dict[str, float] = defaultdict(float)
        
        # Load resource definitions
        self.load_resource_data()
        
        # Initialize market prices
        self.market.update_prices(self.resources)
    
    def load_resource_data(self):
        """Load resource definitions from JSON"""
        try:
            with open('data/economy/resources.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for resource_data in data['resources'].values():
                resource = Resource(
                    id=resource_data['id'],
                    name=resource_data['name'],
                    japanese_name=resource_data['japanese_name'],
                    category=resource_data['category'],
                    description=resource_data['description'],
                    base_price=resource_data['base_price'],
                    storage_decay=resource_data['storage_decay'],
                    color=tuple(resource_data['color']),
                    icon_index=resource_data['icon_index'],
                    availability=resource_data['availability'],
                    production=resource_data['production'],
                    consumption=resource_data['consumption']
                )
                self.resources[resource.id] = resource
                
        except FileNotFoundError:
            print("Resource data file not found. Using fallback data.")
            self._create_fallback_resources()
    
    def _create_fallback_resources(self):
        """Create basic resource data if JSON loading fails"""
        fallback_resources = [
            ("rice", "米", 100, (200, 180, 120)),
            ("wood", "木材", 80, (139, 90, 43)),
            ("iron", "鉄鋼", 200, (120, 120, 130))
        ]
        
        for i, (res_id, jp_name, price, color) in enumerate(fallback_resources):
            resource = Resource(
                id=res_id,
                name=res_id.title(),
                japanese_name=jp_name,
                category="basic",
                description=f"{jp_name}の説明",
                base_price=price,
                storage_decay=0.01,
                color=color,
                icon_index=i,
                availability={"start_era": "postwar_recovery", "end_era": None},
                production={"sources": [], "base_rate": 5},
                consumption={"per_population": 0.1, "buildings": {}}
            )
            self.resources[res_id] = resource
    
    def update(self, population: int, buildings: Dict[str, int], current_era: str, season: str):
        """Update resource system for one tick"""
        # Calculate production
        self._calculate_production(buildings, current_era, season)
        
        # Calculate consumption
        self._calculate_consumption(population, buildings)
        
        # Apply production and consumption
        self._apply_production_consumption()
        
        # Apply storage decay
        self.storage.apply_decay(self.resources)
        
        # Update market
        self._update_market()
    
    def _calculate_production(self, buildings: Dict[str, int], current_era: str, season: str):
        """Calculate resource production from buildings"""
        self.production_rates.clear()
        
        for resource_id, resource in self.resources.items():
            # Check if resource is available in current era
            if not self._is_resource_available(resource, current_era):
                continue
            
            total_production = 0
            
            # Production from buildings
            for source in resource.production.get('sources', []):
                building_count = buildings.get(source, 0)
                base_rate = resource.production.get('base_rate', 0)
                
                # Apply seasonal modifiers
                seasonal_modifier = resource.production.get('seasonal_modifier', {}).get(season, 1.0)
                
                production = building_count * base_rate * seasonal_modifier
                total_production += production
            
            self.production_rates[resource_id] = total_production
    
    def _calculate_consumption(self, population: int, buildings: Dict[str, int]):
        """Calculate resource consumption"""
        self.consumption_rates.clear()
        
        for resource_id, resource in self.resources.items():
            total_consumption = 0
            
            # Population consumption
            per_pop_consumption = resource.consumption.get('per_population', 0)
            total_consumption += population * per_pop_consumption
            
            # Building consumption
            building_consumption = resource.consumption.get('buildings', {})
            for building_type, consumption_rate in building_consumption.items():
                building_count = buildings.get(building_type, 0)
                total_consumption += building_count * consumption_rate
            
            self.consumption_rates[resource_id] = total_consumption
    
    def _apply_production_consumption(self):
        """Apply calculated production and consumption"""
        for resource_id in self.resources:
            production = self.production_rates.get(resource_id, 0)
            consumption = self.consumption_rates.get(resource_id, 0)
            
            net_change = production - consumption
            
            if net_change > 0:
                self.storage.add_resource(resource_id, net_change)
            elif net_change < 0:
                self.storage.remove_resource(resource_id, -net_change)
    
    def _update_market(self):
        """Update market system"""
        # Update supply and demand based on production and consumption
        for resource_id in self.resources:
            self.market.supply[resource_id] = self.production_rates.get(resource_id, 0)
            self.market.demand[resource_id] = self.consumption_rates.get(resource_id, 0)
        
        # Update prices
        self.market.update_prices(self.resources)
    
    def _is_resource_available(self, resource: Resource, current_era: str) -> bool:
        """Check if resource is available in current era"""
        start_era = resource.availability.get('start_era')
        end_era = resource.availability.get('end_era')
        
        # Simple era ordering check (would need proper era system integration)
        era_order = ['postwar_recovery', 'korean_war_boom', 'high_growth_early', 'olympic_era']
        
        try:
            current_index = era_order.index(current_era)
            start_index = era_order.index(start_era) if start_era else 0
            end_index = era_order.index(end_era) if end_era else len(era_order) - 1
            
            return start_index <= current_index <= end_index
        except ValueError:
            return True  # If era not found, assume available
    
    def get_resource_amount(self, resource_id: str) -> float:
        """Get current amount of resource"""
        return self.storage.get_resource(resource_id)
    
    def get_resource_price(self, resource_id: str) -> float:
        """Get current market price of resource"""
        return self.market.get_price(resource_id)
    
    def get_production_rate(self, resource_id: str) -> float:
        """Get current production rate of resource"""
        return self.production_rates.get(resource_id, 0)
    
    def get_consumption_rate(self, resource_id: str) -> float:
        """Get current consumption rate of resource"""
        return self.consumption_rates.get(resource_id, 0)
    
    def get_net_rate(self, resource_id: str) -> float:
        """Get net production rate (production - consumption)"""
        return self.get_production_rate(resource_id) - self.get_consumption_rate(resource_id)
    
    def buy_from_market(self, resource_id: str, amount: float, available_funds: float) -> Tuple[float, float]:
        """Buy resource from market"""
        return self.market.buy_resource(resource_id, amount, available_funds)
    
    def sell_to_market(self, resource_id: str, amount: float) -> float:
        """Sell resource to market"""
        actual_amount = self.storage.remove_resource(resource_id, amount)
        return self.market.sell_resource(resource_id, actual_amount)
    
    def get_available_resources(self, current_era: str) -> List[str]:
        """Get list of resources available in current era"""
        available = []
        for resource_id, resource in self.resources.items():
            if self._is_resource_available(resource, current_era):
                available.append(resource_id)
        return available
    
    def get_resource_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of all resources for display"""
        summary = {}
        for resource_id, resource in self.resources.items():
            summary[resource_id] = {
                "name": resource.japanese_name,
                "amount": self.get_resource_amount(resource_id),
                "price": self.get_resource_price(resource_id),
                "production": self.get_production_rate(resource_id),
                "consumption": self.get_consumption_rate(resource_id),
                "net": self.get_net_rate(resource_id),
                "color": resource.color
            }
        return summary
    
    def export_state(self) -> Dict[str, Any]:
        """Export resource system state for saving"""
        return {
            "storage": dict(self.storage.resources),
            "prices": dict(self.market.prices),
            "price_history": dict(self.market.price_history)
        }
    
    def import_state(self, state: Dict[str, Any]):
        """Import resource system state from save data"""
        try:
            # Restore storage
            self.storage.resources.clear()
            for resource_id, amount in state.get("storage", {}).items():
                self.storage.resources[resource_id] = amount
            
            # Restore prices
            self.market.prices.update(state.get("prices", {}))
            
            # Restore price history
            for resource_id, history in state.get("price_history", {}).items():
                self.market.price_history[resource_id] = history
                
        except (KeyError, ValueError) as e:
            print(f"Error importing resource system state: {e}")