"""
Technology Research System for ConcLand
"""
from enum import Enum
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass

class TechCategory(Enum):
    CONSTRUCTION = "construction"
    ENERGY = "energy"
    INDUSTRY = "industry"
    AGRICULTURE = "agriculture"
    TRANSPORTATION = "transportation"
    COMMUNICATION = "communication"
    SOCIAL = "social"

@dataclass
class Technology:
    """Single technology definition"""
    id: str
    name: str
    name_jp: str
    description: str
    category: TechCategory
    era_required: int
    research_cost: int
    prerequisites: List[str]
    unlocks_buildings: List[str]
    unlocks_policies: List[str]
    resource_bonus: Dict[str, float]
    other_effects: Dict[str, Any]

class TechnologySystem:
    """Manages technology research tree"""
    
    def __init__(self):
        self.technologies: Dict[str, Technology] = {}
        self.researched_techs: Set[str] = set()
        self.current_research: Optional[str] = None
        self.research_progress: float = 0.0
        self.research_points_per_turn: float = 5.0
        
        self._initialize_tech_tree()
    
    def _initialize_tech_tree(self):
        """Initialize the technology tree"""
        # Era 1 Technologies (1945-1950)
        self.technologies["basic_construction"] = Technology(
            id="basic_construction",
            name="Basic Construction",
            name_jp="基礎建設技術",
            description="Enable basic building techniques",
            category=TechCategory.CONSTRUCTION,
            era_required=1,
            research_cost=50,
            prerequisites=[],
            unlocks_buildings=["BARRACKS", "SMALL_SHOP"],
            unlocks_policies=["reconstruction_focus"],
            resource_bonus={"wood": 1.1},
            other_effects={"construction_speed": 1.1}
        )
        
        self.technologies["agriculture_recovery"] = Technology(
            id="agriculture_recovery",
            name="Agricultural Recovery",
            name_jp="農業復興",
            description="Restore farming techniques",
            category=TechCategory.AGRICULTURE,
            era_required=1,
            research_cost=40,
            prerequisites=[],
            unlocks_buildings=["AGRICULTURAL"],
            unlocks_policies=["food_rationing"],
            resource_bonus={"rice": 1.2},
            other_effects={"food_production": 1.15}
        )
        
        self.technologies["emergency_power"] = Technology(
            id="emergency_power",
            name="Emergency Power",
            name_jp="緊急電力",
            description="Basic power generation",
            category=TechCategory.ENERGY,
            era_required=1,
            research_cost=60,
            prerequisites=[],
            unlocks_buildings=["POWERPLANT"],
            unlocks_policies=[],
            resource_bonus={"coal": 1.1},
            other_effects={"power_generation": 1.2}
        )
        
        # Era 2 Technologies (1950-1955)
        self.technologies["public_housing_tech"] = Technology(
            id="public_housing_tech",
            name="Public Housing",
            name_jp="公営住宅技術",
            description="Mass housing construction",
            category=TechCategory.CONSTRUCTION,
            era_required=2,
            research_cost=80,
            prerequisites=["basic_construction"],
            unlocks_buildings=["PUBLIC_HOUSING"],
            unlocks_policies=[],
            resource_bonus={"steel": 1.1},
            other_effects={"housing_capacity": 1.3}
        )
        
        self.technologies["light_industry"] = Technology(
            id="light_industry",
            name="Light Industry",
            name_jp="軽工業",
            description="Textile and consumer goods",
            category=TechCategory.INDUSTRY,
            era_required=2,
            research_cost=100,
            prerequisites=["emergency_power"],
            unlocks_buildings=["INDUSTRIAL"],
            unlocks_policies=["industrial_boost"],
            resource_bonus={"textiles": 1.3},
            other_effects={"industrial_output": 1.2}
        )
        
        self.technologies["basic_education"] = Technology(
            id="basic_education",
            name="Education System",
            name_jp="教育制度",
            description="Establish schools",
            category=TechCategory.SOCIAL,
            era_required=2,
            research_cost=70,
            prerequisites=[],
            unlocks_buildings=["SCHOOL"],
            unlocks_policies=["education_reform"],
            resource_bonus={},
            other_effects={"research_speed": 1.1, "happiness": 0.05}
        )
        
        # Era 3 Technologies (1955-1965)
        self.technologies["heavy_industry"] = Technology(
            id="heavy_industry",
            name="Heavy Industry",
            name_jp="重工業",
            description="Steel and machinery production",
            category=TechCategory.INDUSTRY,
            era_required=3,
            research_cost=150,
            prerequisites=["light_industry"],
            unlocks_buildings=[],
            unlocks_policies=[],
            resource_bonus={"steel": 1.5, "plastics": 1.2},
            other_effects={"industrial_output": 1.5}
        )
        
        self.technologies["urban_planning"] = Technology(
            id="urban_planning",
            name="Urban Planning",
            name_jp="都市計画",
            description="Modern city design",
            category=TechCategory.CONSTRUCTION,
            era_required=3,
            research_cost=120,
            prerequisites=["public_housing_tech"],
            unlocks_buildings=["HIGH_RISE", "DEPARTMENT_STORE"],
            unlocks_policies=[],
            resource_bonus={},
            other_effects={"city_efficiency": 1.2, "housing_capacity": 1.5}
        )
        
        self.technologies["rail_transport"] = Technology(
            id="rail_transport",
            name="Rail Transport",
            name_jp="鉄道輸送",
            description="Modern rail systems",
            category=TechCategory.TRANSPORTATION,
            era_required=3,
            research_cost=140,
            prerequisites=["heavy_industry"],
            unlocks_buildings=["TRAIN_STATION"],
            unlocks_policies=["shinkansen_project"],
            resource_bonus={},
            other_effects={"transport_efficiency": 1.3}
        )
        
        self.technologies["medical_advances"] = Technology(
            id="medical_advances",
            name="Medical Advances",
            name_jp="医療進歩",
            description="Modern healthcare",
            category=TechCategory.SOCIAL,
            era_required=3,
            research_cost=110,
            prerequisites=["basic_education"],
            unlocks_buildings=["HOSPITAL"],
            unlocks_policies=[],
            resource_bonus={},
            other_effects={"population_growth": 1.2, "happiness": 0.1}
        )
        
        # Era 4 Technologies (1965-1970)
        self.technologies["electronics"] = Technology(
            id="electronics",
            name="Electronics",
            name_jp="電子工学",
            description="Electronic components",
            category=TechCategory.INDUSTRY,
            era_required=4,
            research_cost=200,
            prerequisites=["heavy_industry"],
            unlocks_buildings=[],
            unlocks_policies=["technology_nation"],
            resource_bonus={"electronics": 1.5},
            other_effects={"tech_production": 1.4}
        )
        
        self.technologies["nuclear_power"] = Technology(
            id="nuclear_power",
            name="Nuclear Power",
            name_jp="原子力",
            description="Peaceful nuclear energy",
            category=TechCategory.ENERGY,
            era_required=4,
            research_cost=250,
            prerequisites=["emergency_power", "heavy_industry"],
            unlocks_buildings=["NUCLEAR"],
            unlocks_policies=[],
            resource_bonus={"nuclear": 2.0},
            other_effects={"power_generation": 2.0}
        )
        
        self.technologies["telecommunications"] = Technology(
            id="telecommunications",
            name="Telecommunications",
            name_jp="電気通信",
            description="TV and radio broadcasting",
            category=TechCategory.COMMUNICATION,
            era_required=4,
            research_cost=180,
            prerequisites=["electronics"],
            unlocks_buildings=["TV_TOWER"],
            unlocks_policies=[],
            resource_bonus={},
            other_effects={"happiness": 0.15, "information_spread": 1.5}
        )
        
        self.technologies["highway_system"] = Technology(
            id="highway_system",
            name="Highway System",
            name_jp="高速道路網",
            description="Modern road infrastructure",
            category=TechCategory.TRANSPORTATION,
            era_required=4,
            research_cost=160,
            prerequisites=["urban_planning", "heavy_industry"],
            unlocks_buildings=["HIGHWAY"],
            unlocks_policies=["olympic_preparation"],
            resource_bonus={},
            other_effects={"transport_efficiency": 1.5, "trade": 1.3}
        )
        
        self.technologies["semiconductors"] = Technology(
            id="semiconductors",
            name="Semiconductors",
            name_jp="半導体",
            description="Advanced chip technology",
            category=TechCategory.INDUSTRY,
            era_required=4,
            research_cost=300,
            prerequisites=["electronics"],
            unlocks_buildings=[],
            unlocks_policies=[],
            resource_bonus={"semiconductors": 2.0},
            other_effects={"tech_production": 2.0, "export_value": 1.5}
        )
    
    def can_research(self, tech_id: str) -> bool:
        """Check if a technology can be researched"""
        if tech_id not in self.technologies:
            return False
        
        tech = self.technologies[tech_id]
        
        # Already researched
        if tech_id in self.researched_techs:
            return False
        
        # Check prerequisites
        for prereq in tech.prerequisites:
            if prereq not in self.researched_techs:
                return False
        
        return True
    
    def start_research(self, tech_id: str) -> bool:
        """Start researching a technology"""
        if not self.can_research(tech_id):
            return False
        
        self.current_research = tech_id
        self.research_progress = 0.0
        return True
    
    def update_research(self, research_modifier: float = 1.0):
        """Update research progress"""
        if not self.current_research:
            return None
        
        # Add research points
        self.research_progress += self.research_points_per_turn * research_modifier
        
        tech = self.technologies[self.current_research]
        
        # Check if completed
        if self.research_progress >= tech.research_cost:
            completed_tech = self.current_research
            self.researched_techs.add(completed_tech)
            self.current_research = None
            self.research_progress = 0.0
            return completed_tech
        
        return None
    
    def get_research_progress_percent(self) -> float:
        """Get current research progress as percentage"""
        if not self.current_research:
            return 0.0
        
        tech = self.technologies[self.current_research]
        return (self.research_progress / tech.research_cost) * 100
    
    def get_available_technologies(self, current_era: int) -> List[Technology]:
        """Get list of available technologies to research"""
        available = []
        for tech_id, tech in self.technologies.items():
            if (tech.era_required <= current_era and 
                tech_id not in self.researched_techs and
                self.can_research(tech_id)):
                available.append(tech)
        return available
    
    def get_unlocked_buildings(self) -> Set[str]:
        """Get all buildings unlocked by researched technologies"""
        unlocked = set()
        for tech_id in self.researched_techs:
            tech = self.technologies[tech_id]
            unlocked.update(tech.unlocks_buildings)
        return unlocked
    
    def get_tech_bonuses(self) -> Dict[str, float]:
        """Get all resource bonuses from researched technologies"""
        bonuses = {}
        for tech_id in self.researched_techs:
            tech = self.technologies[tech_id]
            for resource, bonus in tech.resource_bonus.items():
                if resource not in bonuses:
                    bonuses[resource] = 1.0
                bonuses[resource] *= bonus
        return bonuses
    
    def set_research_speed(self, base_speed: float):
        """Set base research points per turn"""
        self.research_points_per_turn = base_speed