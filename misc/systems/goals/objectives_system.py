"""
Objectives and Victory Conditions System for ConcLand
"""
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass

class ObjectiveType(Enum):
    POPULATION = "population"
    ECONOMY = "economy"
    TECHNOLOGY = "technology"
    CULTURE = "culture"
    INFRASTRUCTURE = "infrastructure"
    ENVIRONMENT = "environment"

class ObjectiveStatus(Enum):
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Objective:
    """Single objective definition"""
    id: str
    name: str
    description: str
    type: ObjectiveType
    status: ObjectiveStatus
    required_era: Optional[int] = None
    prerequisites: List[str] = None
    target_value: float = 0
    current_value: float = 0
    reward_resources: Dict[str, float] = None
    reward_tech_points: int = 0
    victory_points: int = 0
    check_function: Optional[Callable] = None
    
    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []
        if self.reward_resources is None:
            self.reward_resources = {}

class ObjectivesSystem:
    """Manages game objectives and victory conditions"""
    
    def __init__(self):
        self.objectives: Dict[str, Objective] = {}
        self.completed_objectives: List[str] = []
        self.victory_points: int = 0
        self.victory_threshold: int = 100
        
        self._initialize_objectives()
    
    def _initialize_objectives(self):
        """Initialize all game objectives"""
        # Era 1 Objectives (1945-1950)
        self.objectives["survival"] = Objective(
            id="survival",
            name="戦後の生存",
            description="人口1万人を維持する",
            type=ObjectiveType.POPULATION,
            status=ObjectiveStatus.AVAILABLE,
            required_era=1,
            target_value=10000,
            victory_points=5
        )
        
        self.objectives["basic_housing"] = Objective(
            id="basic_housing",
            name="基本的住居",
            description="バラック住宅を50軒建設",
            type=ObjectiveType.INFRASTRUCTURE,
            status=ObjectiveStatus.AVAILABLE,
            required_era=1,
            target_value=50,
            victory_points=5
        )
        
        self.objectives["food_security"] = Objective(
            id="food_security",
            name="食糧確保",
            description="米の生産量を月100単位達成",
            type=ObjectiveType.ECONOMY,
            status=ObjectiveStatus.AVAILABLE,
            required_era=1,
            target_value=100,
            reward_resources={"rice": 500},
            victory_points=10
        )
        
        # Era 2 Objectives (1950-1955)
        self.objectives["korean_war_boost"] = Objective(
            id="korean_war_boost",
            name="朝鮮戦争特需",
            description="工業生産を月500単位達成",
            type=ObjectiveType.ECONOMY,
            status=ObjectiveStatus.LOCKED,
            required_era=2,
            prerequisites=["basic_housing"],
            target_value=500,
            reward_tech_points=20,
            victory_points=15
        )
        
        self.objectives["public_housing"] = Objective(
            id="public_housing",
            name="公営住宅整備",
            description="市営団地を20棟建設",
            type=ObjectiveType.INFRASTRUCTURE,
            status=ObjectiveStatus.LOCKED,
            required_era=2,
            target_value=20,
            victory_points=10
        )
        
        # Era 3 Objectives (1955-1965)
        self.objectives["economic_miracle"] = Objective(
            id="economic_miracle",
            name="経済の奇跡",
            description="GDPを1000達成",
            type=ObjectiveType.ECONOMY,
            status=ObjectiveStatus.LOCKED,
            required_era=3,
            prerequisites=["korean_war_boost"],
            target_value=1000,
            victory_points=25
        )
        
        self.objectives["modern_infrastructure"] = Objective(
            id="modern_infrastructure",
            name="近代インフラ",
            description="国鉄駅と高層団地を建設",
            type=ObjectiveType.INFRASTRUCTURE,
            status=ObjectiveStatus.LOCKED,
            required_era=3,
            prerequisites=["public_housing"],
            victory_points=20
        )
        
        # Era 4 Objectives (1965-1970)
        self.objectives["olympic_ready"] = Objective(
            id="olympic_ready",
            name="オリンピック準備",
            description="新幹線と高速道路を整備",
            type=ObjectiveType.INFRASTRUCTURE,
            status=ObjectiveStatus.LOCKED,
            required_era=4,
            prerequisites=["modern_infrastructure"],
            victory_points=30
        )
        
        self.objectives["technological_power"] = Objective(
            id="technological_power",
            name="技術大国",
            description="原子力発電所とテレビ塔を建設",
            type=ObjectiveType.TECHNOLOGY,
            status=ObjectiveStatus.LOCKED,
            required_era=4,
            prerequisites=["economic_miracle"],
            victory_points=25
        )
        
        # Victory Conditions
        self.objectives["economic_superpower"] = Objective(
            id="economic_superpower",
            name="経済超大国",
            description="100の勝利ポイントを獲得",
            type=ObjectiveType.ECONOMY,
            status=ObjectiveStatus.LOCKED,
            target_value=100,
            victory_points=0  # This is the final victory
        )
    
    def update_objective_progress(self, objective_id: str, value: float):
        """Update progress for a specific objective"""
        if objective_id not in self.objectives:
            return
        
        obj = self.objectives[objective_id]
        if obj.status != ObjectiveStatus.IN_PROGRESS:
            return
        
        obj.current_value = value
        
        # Check if completed
        if obj.current_value >= obj.target_value:
            self._complete_objective(objective_id)
    
    def _complete_objective(self, objective_id: str):
        """Mark objective as completed and give rewards"""
        obj = self.objectives[objective_id]
        obj.status = ObjectiveStatus.COMPLETED
        self.completed_objectives.append(objective_id)
        self.victory_points += obj.victory_points
        
        # Unlock dependent objectives
        for other_id, other_obj in self.objectives.items():
            if objective_id in other_obj.prerequisites:
                # Check if all prerequisites are met
                if all(self.objectives[prereq].status == ObjectiveStatus.COMPLETED 
                      for prereq in other_obj.prerequisites):
                    other_obj.status = ObjectiveStatus.AVAILABLE
        
        return obj.reward_resources, obj.reward_tech_points
    
    def check_era_objectives(self, current_era: int):
        """Unlock objectives for current era"""
        for obj_id, obj in self.objectives.items():
            if obj.required_era and obj.required_era <= current_era:
                if obj.status == ObjectiveStatus.LOCKED and not obj.prerequisites:
                    obj.status = ObjectiveStatus.AVAILABLE
                elif obj.status == ObjectiveStatus.LOCKED and obj.prerequisites:
                    # Check prerequisites
                    if all(self.objectives[prereq].status == ObjectiveStatus.COMPLETED 
                          for prereq in obj.prerequisites):
                        obj.status = ObjectiveStatus.AVAILABLE
    
    def get_active_objectives(self) -> List[Objective]:
        """Get list of currently active objectives"""
        active = []
        for obj in self.objectives.values():
            if obj.status in [ObjectiveStatus.AVAILABLE, ObjectiveStatus.IN_PROGRESS]:
                active.append(obj)
        return active
    
    def get_victory_progress(self) -> float:
        """Get victory progress as percentage"""
        return min(100, (self.victory_points / self.victory_threshold) * 100)
    
    def check_victory(self) -> bool:
        """Check if victory conditions are met"""
        return self.victory_points >= self.victory_threshold
    
    def get_objective_summary(self) -> Dict[str, Any]:
        """Get summary of objectives progress"""
        return {
            "total_objectives": len(self.objectives),
            "completed": len(self.completed_objectives),
            "victory_points": self.victory_points,
            "victory_progress": self.get_victory_progress(),
            "active_objectives": [obj.name for obj in self.get_active_objectives()]
        }