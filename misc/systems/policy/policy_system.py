"""
Policy and Decision Making System for ConcLand
"""
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass

class PolicyCategory(Enum):
    ECONOMIC = "economic"
    SOCIAL = "social"
    INFRASTRUCTURE = "infrastructure"
    TECHNOLOGY = "technology"
    ENVIRONMENTAL = "environmental"
    DEFENSE = "defense"

class PolicyEffect:
    """Effects that a policy can have"""
    def __init__(self):
        self.resource_modifiers: Dict[str, float] = {}  # Resource production modifiers
        self.cost_modifiers: Dict[str, float] = {}      # Building cost modifiers
        self.growth_rate_modifier: float = 1.0          # Population growth
        self.happiness_modifier: float = 0.0            # Citizen happiness
        self.pollution_modifier: float = 1.0            # Pollution rate
        self.research_speed_modifier: float = 1.0       # Tech research speed
        self.disaster_resistance: float = 0.0           # Disaster damage reduction

@dataclass
class Policy:
    """Single policy definition"""
    id: str
    name: str
    name_jp: str
    description: str
    category: PolicyCategory
    era_required: int
    cost: int  # Implementation cost
    maintenance_cost: int  # Monthly cost
    effects: PolicyEffect
    conflicts_with: List[str]  # Policies that can't be active together
    requires_tech: Optional[str] = None
    duration: Optional[int] = None  # None = permanent, else months

class PolicySystem:
    """Manages city policies and their effects"""
    
    def __init__(self):
        self.available_policies: Dict[str, Policy] = {}
        self.active_policies: Dict[str, Policy] = {}
        self.policy_history: List[Dict] = []
        self.policy_points: int = 5  # Points to enact policies
        self.max_active_policies: int = 3
        
        self._initialize_policies()
    
    def _initialize_policies(self):
        """Initialize all available policies"""
        # Era 1 Policies
        effects_rationing = PolicyEffect()
        effects_rationing.resource_modifiers["rice"] = 0.8
        effects_rationing.happiness_modifier = -0.1
        effects_rationing.cost_modifiers["RESIDENCE"] = 0.9
        
        self.available_policies["food_rationing"] = Policy(
            id="food_rationing",
            name="Food Rationing",
            name_jp="食糧配給制度",
            description="Reduce food consumption but decrease happiness",
            category=PolicyCategory.SOCIAL,
            era_required=1,
            cost=0,
            maintenance_cost=5,
            effects=effects_rationing,
            conflicts_with=["free_market"]
        )
        
        effects_reconstruction = PolicyEffect()
        effects_reconstruction.cost_modifiers["RESIDENCE"] = 0.7
        effects_reconstruction.cost_modifiers["COMMERCIAL"] = 0.7
        effects_reconstruction.growth_rate_modifier = 1.2
        
        self.available_policies["reconstruction_focus"] = Policy(
            id="reconstruction_focus",
            name="Reconstruction Priority",
            name_jp="復興最優先",
            description="Reduce building costs and boost growth",
            category=PolicyCategory.ECONOMIC,
            era_required=1,
            cost=10,
            maintenance_cost=10,
            effects=effects_reconstruction,
            conflicts_with=[]
        )
        
        # Era 2 Policies
        effects_industrial = PolicyEffect()
        effects_industrial.resource_modifiers["steel"] = 1.5
        effects_industrial.resource_modifiers["textiles"] = 1.3
        effects_industrial.pollution_modifier = 1.3
        
        self.available_policies["industrial_boost"] = Policy(
            id="industrial_boost",
            name="Industrial Expansion",
            name_jp="工業拡大政策",
            description="Boost industrial output but increase pollution",
            category=PolicyCategory.ECONOMIC,
            era_required=2,
            cost=20,
            maintenance_cost=15,
            effects=effects_industrial,
            conflicts_with=["environmental_protection"]
        )
        
        effects_education = PolicyEffect()
        effects_education.research_speed_modifier = 1.3
        effects_education.happiness_modifier = 0.1
        effects_education.growth_rate_modifier = 1.1
        
        self.available_policies["education_reform"] = Policy(
            id="education_reform",
            name="Education Reform",
            name_jp="教育改革",
            description="Boost research and happiness",
            category=PolicyCategory.SOCIAL,
            era_required=2,
            cost=25,
            maintenance_cost=20,
            effects=effects_education,
            conflicts_with=[]
        )
        
        # Era 3 Policies
        effects_income_doubling = PolicyEffect()
        effects_income_doubling.resource_modifiers["all"] = 1.2  # Special: all resources
        effects_income_doubling.growth_rate_modifier = 1.3
        effects_income_doubling.happiness_modifier = 0.2
        
        self.available_policies["income_doubling"] = Policy(
            id="income_doubling",
            name="Income Doubling Plan",
            name_jp="所得倍増計画",
            description="Massive economic growth boost",
            category=PolicyCategory.ECONOMIC,
            era_required=3,
            cost=50,
            maintenance_cost=30,
            effects=effects_income_doubling,
            conflicts_with=["austerity"],
            duration=60  # 5 years
        )
        
        effects_bullet_train = PolicyEffect()
        effects_bullet_train.cost_modifiers["TRAIN_STATION"] = 0.5
        effects_bullet_train.cost_modifiers["HIGHWAY"] = 0.7
        effects_bullet_train.growth_rate_modifier = 1.15
        
        self.available_policies["shinkansen_project"] = Policy(
            id="shinkansen_project",
            name="Shinkansen Development",
            name_jp="新幹線計画",
            description="Reduce infrastructure costs",
            category=PolicyCategory.INFRASTRUCTURE,
            era_required=3,
            cost=40,
            maintenance_cost=25,
            effects=effects_bullet_train,
            conflicts_with=[]
        )
        
        # Era 4 Policies
        effects_olympics = PolicyEffect()
        effects_olympics.happiness_modifier = 0.3
        effects_olympics.growth_rate_modifier = 1.2
        effects_olympics.cost_modifiers["PARK"] = 0.5
        effects_olympics.cost_modifiers["HIGHWAY"] = 0.6
        
        self.available_policies["olympic_preparation"] = Policy(
            id="olympic_preparation",
            name="Olympic Preparation",
            name_jp="オリンピック準備",
            description="Boost morale and infrastructure",
            category=PolicyCategory.SOCIAL,
            era_required=4,
            cost=60,
            maintenance_cost=40,
            effects=effects_olympics,
            conflicts_with=[],
            duration=24  # 2 years
        )
        
        effects_tech_nation = PolicyEffect()
        effects_tech_nation.research_speed_modifier = 1.5
        effects_tech_nation.resource_modifiers["electronics"] = 1.4
        effects_tech_nation.resource_modifiers["semiconductors"] = 1.6
        
        self.available_policies["technology_nation"] = Policy(
            id="technology_nation",
            name="Technology Nation",
            name_jp="技術立国",
            description="Focus on high-tech development",
            category=PolicyCategory.TECHNOLOGY,
            era_required=4,
            cost=70,
            maintenance_cost=35,
            effects=effects_tech_nation,
            conflicts_with=["traditional_values"]
        )
    
    def can_enact_policy(self, policy_id: str) -> bool:
        """Check if a policy can be enacted"""
        if policy_id not in self.available_policies:
            return False
        
        policy = self.available_policies[policy_id]
        
        # Check if already active
        if policy_id in self.active_policies:
            return False
        
        # Check policy limit
        if len(self.active_policies) >= self.max_active_policies:
            return False
        
        # Check conflicts
        for active_id in self.active_policies:
            if active_id in policy.conflicts_with:
                return False
        
        # Check cost
        if self.policy_points < 1:
            return False
        
        return True
    
    def enact_policy(self, policy_id: str) -> bool:
        """Enact a new policy"""
        if not self.can_enact_policy(policy_id):
            return False
        
        policy = self.available_policies[policy_id]
        self.active_policies[policy_id] = policy
        self.policy_points -= 1
        
        # Record in history
        self.policy_history.append({
            "policy_id": policy_id,
            "action": "enacted",
            "month": 0  # Should be set by game
        })
        
        return True
    
    def cancel_policy(self, policy_id: str) -> bool:
        """Cancel an active policy"""
        if policy_id not in self.active_policies:
            return False
        
        del self.active_policies[policy_id]
        
        # Record in history
        self.policy_history.append({
            "policy_id": policy_id,
            "action": "cancelled",
            "month": 0  # Should be set by game
        })
        
        return True
    
    def update_policies(self, current_month: int):
        """Update policy durations and effects"""
        to_remove = []
        
        for policy_id, policy in self.active_policies.items():
            if policy.duration:
                # Check duration
                enact_record = next((h for h in reversed(self.policy_history) 
                                   if h["policy_id"] == policy_id and h["action"] == "enacted"), None)
                if enact_record:
                    elapsed = current_month - enact_record["month"]
                    if elapsed >= policy.duration:
                        to_remove.append(policy_id)
        
        # Remove expired policies
        for policy_id in to_remove:
            self.cancel_policy(policy_id)
        
        # Add policy points periodically (every 6 months)
        if current_month % 6 == 0:
            self.policy_points = min(10, self.policy_points + 1)
    
    def get_total_effects(self) -> PolicyEffect:
        """Calculate combined effects of all active policies"""
        combined = PolicyEffect()
        
        for policy in self.active_policies.values():
            effects = policy.effects
            
            # Combine resource modifiers
            for resource, modifier in effects.resource_modifiers.items():
                if resource not in combined.resource_modifiers:
                    combined.resource_modifiers[resource] = 1.0
                combined.resource_modifiers[resource] *= modifier
            
            # Combine cost modifiers
            for building, modifier in effects.cost_modifiers.items():
                if building not in combined.cost_modifiers:
                    combined.cost_modifiers[building] = 1.0
                combined.cost_modifiers[building] *= modifier
            
            # Combine other modifiers
            combined.growth_rate_modifier *= effects.growth_rate_modifier
            combined.happiness_modifier += effects.happiness_modifier
            combined.pollution_modifier *= effects.pollution_modifier
            combined.research_speed_modifier *= effects.research_speed_modifier
            combined.disaster_resistance += effects.disaster_resistance
        
        return combined
    
    def get_maintenance_cost(self) -> int:
        """Get total maintenance cost of active policies"""
        total = 0
        for policy in self.active_policies.values():
            total += policy.maintenance_cost
        return total
    
    def get_available_policies_for_era(self, era: int) -> List[Policy]:
        """Get policies available for current era"""
        available = []
        for policy in self.available_policies.values():
            if policy.era_required <= era and policy.id not in self.active_policies:
                available.append(policy)
        return available