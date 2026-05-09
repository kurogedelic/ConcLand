"""
Economic System Integration for ConcLand Mini
Integrates resource management with the main game simulation
"""
import json
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
from misc.systems.economy.resource_manager import ResourceManager

@dataclass
class EconomicPolicy:
    """Economic policy affecting city development"""
    id: str
    name: str
    japanese_name: str
    description: str
    effects: Dict[str, float]
    cost: int
    duration: int  # Duration in months
    active: bool = False
    remaining_duration: int = 0

@dataclass
class TaxPolicy:
    """Tax policy configuration"""
    residential_rate: float = 0.08  # 8% default
    commercial_rate: float = 0.12   # 12% default  
    industrial_rate: float = 0.10   # 10% default
    
    def get_tax_revenue(self, zone_type, population: int) -> int:
        """Calculate tax revenue from zone"""
        rates = {
            'RESIDENTIAL': self.residential_rate,
            'COMMERCIAL': self.commercial_rate,
            'INDUSTRIAL': self.industrial_rate
        }
        rate = rates.get(zone_type, 0.05)
        return int(population * rate * 10)  # Base tax per population

class EconomicIndicators:
    """Tracks economic health indicators"""
    
    def __init__(self):
        self.gdp = 0
        self.gdp_history = []
        self.unemployment = 0.0
        self.inflation = 0.0
        self.trade_balance = 0
        self.productivity = 1.0
        
    def update(self, population: int, employment: int, production: Dict[str, float], consumption: Dict[str, float]):
        """Update economic indicators"""
        # Calculate GDP from production value
        self.gdp = sum(production.values()) * 100
        self.gdp_history.append(self.gdp)
        if len(self.gdp_history) > 120:  # Keep 2 minutes of history
            self.gdp_history.pop(0)
        
        # Calculate unemployment rate
        if population > 0:
            self.unemployment = max(0.0, 1.0 - (employment / population))
        else:
            self.unemployment = 0.0
        
        # Simple inflation calculation based on supply/demand
        total_production = sum(production.values())
        total_consumption = sum(consumption.values())
        
        if total_production > 0:
            demand_pressure = total_consumption / total_production
            self.inflation = max(-0.05, min(0.10, (demand_pressure - 1.0) * 0.1))
        
        # Trade balance (simplified)
        self.trade_balance = int(total_production - total_consumption)
        
        # Productivity based on infrastructure and technology
        self.productivity = min(2.0, 1.0 + (employment / max(population, 1)) * 0.5)

class ConcLandEconomicSystem:
    """Main economic system for ConcLand"""
    
    def __init__(self):
        # Core systems
        self.resource_manager = ResourceManager()
        self.tax_policy = TaxPolicy()
        self.indicators = EconomicIndicators()
        
        # Policies
        self.available_policies: Dict[str, EconomicPolicy] = {}
        self.active_policies: List[str] = []
        
        # Economic state
        self.funds = 10000
        self.monthly_revenue = 0
        self.monthly_expenses = 0
        self.budget_history = []
        
        # Season and era tracking
        self.current_season = "spring"
        self.current_era = "postwar_recovery"
        self.season_timer = 0
        self.season_duration = 900  # 15 seconds per season at 60 FPS
        
        # Initialize policies
        self._load_economic_policies()
    
    def _load_economic_policies(self):
        """Load economic policies"""
        policies_data = {
            "industrial_boost": {
                "id": "industrial_boost",
                "name": "Industrial Development Boost",
                "japanese_name": "工業開発促進",
                "description": "Increases industrial production by 25%",
                "effects": {"industrial_production": 1.25, "industrial_growth": 1.3},
                "cost": 5000,
                "duration": 12
            },
            "tax_incentive": {
                "id": "tax_incentive", 
                "name": "Business Tax Incentive",
                "japanese_name": "事業税優遇措置",
                "description": "Reduces business taxes to attract companies",
                "effects": {"commercial_growth": 1.4, "tax_revenue": 0.8},
                "cost": 3000,
                "duration": 6
            },
            "housing_subsidy": {
                "id": "housing_subsidy",
                "name": "Housing Development Subsidy",
                "japanese_name": "住宅開発助成金",
                "description": "Subsidizes residential development",
                "effects": {"residential_growth": 1.35, "construction_cost": 0.85},
                "cost": 4000,
                "duration": 8
            },
            "education_investment": {
                "id": "education_investment",
                "name": "Education System Investment",
                "japanese_name": "教育投資政策",
                "description": "Improves education to boost productivity",
                "effects": {"productivity": 1.15, "research_speed": 1.2},
                "cost": 6000,
                "duration": 24
            },
            "infrastructure_program": {
                "id": "infrastructure_program",
                "name": "Infrastructure Development Program", 
                "japanese_name": "インフラ整備計画",
                "description": "Major infrastructure improvements",
                "effects": {"construction_speed": 1.3, "traffic_flow": 1.25},
                "cost": 8000,
                "duration": 18
            }
        }
        
        for policy_data in policies_data.values():
            policy = EconomicPolicy(
                id=policy_data["id"],
                name=policy_data["name"],
                japanese_name=policy_data["japanese_name"],
                description=policy_data["description"],
                effects=policy_data["effects"],
                cost=policy_data["cost"],
                duration=policy_data["duration"]
            )
            self.available_policies[policy.id] = policy
    
    def update(self, population: int, buildings: Dict[str, int], employment: int, month: int):
        """Update economic system"""
        # Update season
        self._update_season()
        
        # Update resource system
        self.resource_manager.update(population, buildings, self.current_era, self.current_season)
        
        # Update economic indicators
        production = {res_id: self.resource_manager.get_production_rate(res_id) 
                     for res_id in self.resource_manager.resources}
        consumption = {res_id: self.resource_manager.get_consumption_rate(res_id) 
                      for res_id in self.resource_manager.resources}
        
        self.indicators.update(population, employment, production, consumption)
        
        # Update policies
        self._update_policies()
        
        # Calculate monthly budget (every 60 frames = 1 second = 1 month in game)
        if month % 60 == 0:
            self._calculate_monthly_budget(population, buildings)
    
    def _update_season(self):
        """Update seasonal progression"""
        self.season_timer += 1
        if self.season_timer >= self.season_duration:
            self.season_timer = 0
            seasons = ["spring", "summer", "autumn", "winter"]
            current_index = seasons.index(self.current_season)
            self.current_season = seasons[(current_index + 1) % 4]
    
    def _update_policies(self):
        """Update active economic policies"""
        for policy_id in list(self.active_policies):
            policy = self.available_policies[policy_id]
            if policy.active:
                policy.remaining_duration -= 1
                if policy.remaining_duration <= 0:
                    policy.active = False
                    self.active_policies.remove(policy_id)
    
    def _calculate_monthly_budget(self, population: int, buildings: Dict[str, int]):
        """Calculate monthly revenue and expenses"""
        # Tax revenue
        self.monthly_revenue = 0
        for building_type, count in buildings.items():
            if building_type in ['RESIDENTIAL', 'COMMERCIAL', 'INDUSTRIAL']:
                # Assume average population per building
                avg_pop_per_building = 50 if building_type == 'RESIDENTIAL' else 20
                building_population = count * avg_pop_per_building
                self.monthly_revenue += self.tax_policy.get_tax_revenue(building_type, building_population)
        
        # Resource trade revenue
        for resource_id, resource in self.resource_manager.resources.items():
            net_rate = self.resource_manager.get_net_rate(resource_id)
            if net_rate > 0:  # Surplus - can sell
                revenue = self.resource_manager.sell_to_market(resource_id, net_rate * 0.1)  # Sell 10% of surplus
                self.monthly_revenue += int(revenue)
        
        # Apply policy effects to revenue
        revenue_multiplier = 1.0
        for policy_id in self.active_policies:
            policy = self.available_policies[policy_id]
            revenue_multiplier *= policy.effects.get("tax_revenue", 1.0)
        
        self.monthly_revenue = int(self.monthly_revenue * revenue_multiplier)
        
        # Monthly expenses
        self.monthly_expenses = 0
        
        # Building maintenance
        maintenance_costs = {
            'SCHOOL': 200,
            'HOSPITAL': 300, 
            'POLICE': 150,
            'FIRE': 120,
            'COAL_PLANT': 500,
            'NUCLEAR_PLANT': 800,
            'WATER_PLANT': 250
        }
        
        for building_type, cost in maintenance_costs.items():
            count = buildings.get(building_type, 0)
            self.monthly_expenses += count * cost
        
        # Infrastructure maintenance (roads, rails, etc.)
        infrastructure_count = sum(buildings.get(t, 0) for t in ['ROAD', 'RAIL', 'WIRE'])
        self.monthly_expenses += infrastructure_count * 5  # 5 per tile
        
        # Policy costs
        for policy_id in self.active_policies:
            policy = self.available_policies[policy_id]
            self.monthly_expenses += policy.cost // policy.duration  # Spread cost over duration
        
        # Update funds
        net_income = self.monthly_revenue - self.monthly_expenses
        self.funds += net_income
        
        # Record budget history
        self.budget_history.append({
            'revenue': self.monthly_revenue,
            'expenses': self.monthly_expenses,
            'net': net_income,
            'funds': self.funds
        })
        
        if len(self.budget_history) > 120:  # Keep 2 minutes of history
            self.budget_history.pop(0)
    
    def activate_policy(self, policy_id: str) -> bool:
        """Activate economic policy"""
        if policy_id not in self.available_policies:
            return False
        
        policy = self.available_policies[policy_id]
        if policy.active or self.funds < policy.cost:
            return False
        
        # Deduct cost
        self.funds -= policy.cost
        
        # Activate policy
        policy.active = True
        policy.remaining_duration = policy.duration * 60  # Convert months to frames
        self.active_policies.append(policy_id)
        
        return True
    
    def can_afford(self, cost: int) -> bool:
        """Check if city can afford cost"""
        return self.funds >= cost
    
    def spend_funds(self, amount: int) -> bool:
        """Spend funds if available"""
        if self.can_afford(amount):
            self.funds -= amount
            return True
        return False
    
    def get_policy_multiplier(self, effect_type: str) -> float:
        """Get combined policy effect multiplier"""
        multiplier = 1.0
        for policy_id in self.active_policies:
            policy = self.available_policies[policy_id]
            multiplier *= policy.effects.get(effect_type, 1.0)
        return multiplier
    
    def get_resource_info(self) -> Dict[str, Dict]:
        """Get resource information for UI"""
        return self.resource_manager.get_resource_summary()
    
    def get_economic_status(self) -> Dict:
        """Get economic status for UI"""
        return {
            "funds": self.funds,
            "monthly_revenue": self.monthly_revenue,
            "monthly_expenses": self.monthly_expenses,
            "gdp": self.indicators.gdp,
            "unemployment": self.indicators.unemployment,
            "inflation": self.indicators.inflation,
            "trade_balance": self.indicators.trade_balance,
            "productivity": self.indicators.productivity,
            "current_season": self.current_season,
            "current_era": self.current_era,
            "active_policies": len(self.active_policies)
        }
    
    def get_available_policies(self) -> List[Dict]:
        """Get available policies for UI"""
        policies = []
        for policy in self.available_policies.values():
            if not policy.active:
                policies.append({
                    "id": policy.id,
                    "name": policy.japanese_name,
                    "description": policy.description,
                    "cost": policy.cost,
                    "duration": policy.duration,
                    "affordable": self.can_afford(policy.cost)
                })
        return policies
    
    def set_tax_rates(self, residential: float, commercial: float, industrial: float):
        """Set tax rates"""
        self.tax_policy.residential_rate = max(0.01, min(0.20, residential))
        self.tax_policy.commercial_rate = max(0.01, min(0.25, commercial))
        self.tax_policy.industrial_rate = max(0.01, min(0.22, industrial))
    
    def export_save_data(self) -> Dict:
        """Export economic system data for saving"""
        return {
            "funds": self.funds,
            "tax_policy": {
                "residential_rate": self.tax_policy.residential_rate,
                "commercial_rate": self.tax_policy.commercial_rate,
                "industrial_rate": self.tax_policy.industrial_rate
            },
            "active_policies": [(p_id, self.available_policies[p_id].remaining_duration) 
                              for p_id in self.active_policies],
            "current_season": self.current_season,
            "current_era": self.current_era,
            "season_timer": self.season_timer,
            "resource_system": self.resource_manager.export_state()
        }
    
    def import_save_data(self, save_data: Dict):
        """Import economic system data from save"""
        try:
            self.funds = save_data.get("funds", 10000)
            
            # Tax policy
            tax_data = save_data.get("tax_policy", {})
            self.tax_policy.residential_rate = tax_data.get("residential_rate", 0.08)
            self.tax_policy.commercial_rate = tax_data.get("commercial_rate", 0.12)
            self.tax_policy.industrial_rate = tax_data.get("industrial_rate", 0.10)
            
            # Active policies
            self.active_policies.clear()
            for policy_id, remaining_duration in save_data.get("active_policies", []):
                if policy_id in self.available_policies:
                    policy = self.available_policies[policy_id]
                    policy.active = True
                    policy.remaining_duration = remaining_duration
                    self.active_policies.append(policy_id)
            
            # Season and era
            self.current_season = save_data.get("current_season", "spring")
            self.current_era = save_data.get("current_era", "postwar_recovery")
            self.season_timer = save_data.get("season_timer", 0)
            
            # Resource system
            resource_data = save_data.get("resource_system", {})
            if resource_data:
                self.resource_manager.import_state(resource_data)
                
        except Exception as e:
            print(f"Error importing economic system data: {e}")