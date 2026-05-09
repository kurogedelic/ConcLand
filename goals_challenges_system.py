"""
Goals and Challenges System for ConcLand
Provides objectives, quests, and daily challenges to guide gameplay
"""
import random
import json
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

class GoalType(Enum):
    POPULATION = "population"
    ECONOMY = "economy"
    CONSTRUCTION = "construction"
    ENVIRONMENT = "environment"
    HAPPINESS = "happiness"
    INFRASTRUCTURE = "infrastructure"
    DISASTER = "disaster"
    SPECIAL = "special"

class GoalStatus(Enum):
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CLAIMED = "claimed"

class ChallengeType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    SEASONAL = "seasonal"
    SPECIAL_EVENT = "special_event"

@dataclass
class Goal:
    """Individual goal/objective"""
    id: str
    name: str
    japanese_name: str
    description: str
    japanese_description: str
    goal_type: GoalType
    requirements: Dict[str, Any]
    rewards: Dict[str, Any]
    time_limit: Optional[int] = None  # In game days
    prerequisite_goals: List[str] = field(default_factory=list)
    status: GoalStatus = GoalStatus.LOCKED
    progress: Dict[str, Any] = field(default_factory=dict)
    start_time: Optional[int] = None
    completion_time: Optional[int] = None
    
    def check_requirements(self, game_state: Dict[str, Any]) -> bool:
        """Check if goal requirements are met"""
        for req_type, req_value in self.requirements.items():
            if req_type == "population":
                if game_state.get("population", 0) < req_value:
                    return False
            elif req_type == "funds":
                if game_state.get("funds", 0) < req_value:
                    return False
            elif req_type == "gdp":
                if game_state.get("gdp", 0) < req_value:
                    return False
            elif req_type == "buildings":
                for building_type, count in req_value.items():
                    if game_state.get("buildings", {}).get(building_type, 0) < count:
                        return False
            elif req_type == "happiness":
                if game_state.get("happiness", 0) < req_value:
                    return False
            elif req_type == "pollution":
                if game_state.get("pollution", 100) > req_value:
                    return False
            elif req_type == "disasters_survived":
                if game_state.get("disasters_survived", 0) < req_value:
                    return False
        
        return True
    
    def update_progress(self, game_state: Dict[str, Any]):
        """Update goal progress"""
        for req_type, req_value in self.requirements.items():
            if req_type == "population":
                self.progress[req_type] = min(game_state.get("population", 0), req_value)
            elif req_type == "funds":
                self.progress[req_type] = min(game_state.get("funds", 0), req_value)
            elif req_type == "buildings":
                if req_type not in self.progress:
                    self.progress[req_type] = {}
                for building_type, count in req_value.items():
                    current = game_state.get("buildings", {}).get(building_type, 0)
                    self.progress[req_type][building_type] = min(current, count)
    
    def get_progress_percentage(self) -> float:
        """Get overall progress percentage"""
        if not self.requirements:
            return 100.0 if self.status == GoalStatus.COMPLETED else 0.0
        
        total_progress = 0
        total_requirements = 0
        
        for req_type, req_value in self.requirements.items():
            if isinstance(req_value, dict):
                for sub_key, sub_value in req_value.items():
                    current = self.progress.get(req_type, {}).get(sub_key, 0)
                    total_progress += min(current / sub_value, 1.0) if sub_value > 0 else 0
                    total_requirements += 1
            else:
                current = self.progress.get(req_type, 0)
                total_progress += min(current / req_value, 1.0) if req_value > 0 else 0
                total_requirements += 1
        
        return (total_progress / total_requirements * 100) if total_requirements > 0 else 0

@dataclass
class Challenge:
    """Time-limited challenge"""
    id: str
    name: str
    japanese_name: str
    description: str
    japanese_description: str
    challenge_type: ChallengeType
    objectives: List[Dict[str, Any]]
    rewards: Dict[str, Any]
    start_time: datetime
    end_time: datetime
    status: GoalStatus = GoalStatus.AVAILABLE
    progress: List[bool] = field(default_factory=list)
    
    def is_expired(self) -> bool:
        """Check if challenge has expired"""
        return datetime.now() > self.end_time
    
    def time_remaining(self) -> timedelta:
        """Get time remaining for challenge"""
        return self.end_time - datetime.now()
    
    def check_objectives(self, game_state: Dict[str, Any]) -> List[bool]:
        """Check which objectives are completed"""
        results = []
        for obj in self.objectives:
            completed = True
            for key, value in obj.items():
                if key == "action" and value == "build_roads":
                    if game_state.get("roads_built_today", 0) < obj.get("count", 1):
                        completed = False
                elif key == "action" and value == "earn_money":
                    if game_state.get("money_earned_today", 0) < obj.get("amount", 0):
                        completed = False
                elif key == "action" and value == "reduce_pollution":
                    if game_state.get("pollution_reduced_today", 0) < obj.get("amount", 0):
                        completed = False
            results.append(completed)
        return results

class QuestChain:
    """Series of connected goals forming a quest line"""
    def __init__(self, chain_id: str, name: str, japanese_name: str):
        self.id = chain_id
        self.name = name
        self.japanese_name = japanese_name
        self.goals: List[Goal] = []
        self.current_index = 0
        self.completed = False
        
    def add_goal(self, goal: Goal):
        """Add goal to quest chain"""
        self.goals.append(goal)
    
    def get_current_goal(self) -> Optional[Goal]:
        """Get current active goal in chain"""
        if self.current_index < len(self.goals):
            return self.goals[self.current_index]
        return None
    
    def advance(self) -> bool:
        """Advance to next goal in chain"""
        self.current_index += 1
        if self.current_index >= len(self.goals):
            self.completed = True
            return False
        return True
    
    def get_progress(self) -> Tuple[int, int]:
        """Get quest chain progress (completed, total)"""
        return self.current_index, len(self.goals)

class GoalsManager:
    """Main goals and challenges management system"""
    
    def __init__(self):
        # Goals storage
        self.all_goals: Dict[str, Goal] = {}
        self.active_goals: List[str] = []
        self.completed_goals: List[str] = []
        
        # Challenges
        self.daily_challenges: List[Challenge] = []
        self.weekly_challenges: List[Challenge] = []
        self.active_challenges: List[Challenge] = []
        
        # Quest chains
        self.quest_chains: Dict[str, QuestChain] = {}
        self.active_chains: List[str] = []
        
        # Statistics
        self.total_goals_completed = 0
        self.total_challenges_completed = 0
        self.total_rewards_earned = {}
        
        # Initialize content
        self._create_main_goals()
        self._create_quest_chains()
        self._generate_daily_challenges()
    
    def _create_main_goals(self):
        """Create main campaign goals"""
        
        # Tutorial goals
        self.all_goals["first_citizens"] = Goal(
            id="first_citizens",
            name="First Citizens",
            japanese_name="最初の市民",
            description="Reach 100 population",
            japanese_description="人口100人に到達",
            goal_type=GoalType.POPULATION,
            requirements={"population": 100},
            rewards={"funds": 5000, "experience": 100}
        )
        
        self.all_goals["small_town"] = Goal(
            id="small_town",
            name="Small Town",
            japanese_name="小さな町",
            description="Reach 1,000 population",
            japanese_description="人口1,000人に到達",
            goal_type=GoalType.POPULATION,
            requirements={"population": 1000},
            rewards={"funds": 10000, "experience": 500, "unlock": "commercial_zone"},
            prerequisite_goals=["first_citizens"]
        )
        
        self.all_goals["city_status"] = Goal(
            id="city_status",
            name="City Status",
            japanese_name="都市への昇格",
            description="Reach 10,000 population",
            japanese_description="人口10,000人に到達",
            goal_type=GoalType.POPULATION,
            requirements={"population": 10000},
            rewards={"funds": 50000, "experience": 2000, "unlock": "metro_system"},
            prerequisite_goals=["small_town"]
        )
        
        # Economic goals
        self.all_goals["profitable"] = Goal(
            id="profitable",
            name="Profitable City",
            japanese_name="黒字経営",
            description="Achieve positive monthly income",
            japanese_description="月次収支を黒字にする",
            goal_type=GoalType.ECONOMY,
            requirements={"monthly_income": 1000},
            rewards={"funds": 5000, "experience": 200}
        )
        
        self.all_goals["economic_boom"] = Goal(
            id="economic_boom",
            name="Economic Boom",
            japanese_name="経済ブーム",
            description="Reach ¥100,000 GDP",
            japanese_description="GDP10万円を達成",
            goal_type=GoalType.ECONOMY,
            requirements={"gdp": 100000},
            rewards={"funds": 20000, "experience": 1000, "policy": "tax_reduction"}
        )
        
        # Construction goals
        self.all_goals["infrastructure"] = Goal(
            id="infrastructure",
            name="Infrastructure Network",
            japanese_name="インフラ網",
            description="Build 100 road tiles",
            japanese_description="道路を100タイル建設",
            goal_type=GoalType.CONSTRUCTION,
            requirements={"buildings": {"road": 100}},
            rewards={"funds": 3000, "experience": 150}
        )
        
        self.all_goals["mixed_zones"] = Goal(
            id="mixed_zones",
            name="Mixed Development",
            japanese_name="複合開発",
            description="Build all three zone types",
            japanese_description="全3種類のゾーンを建設",
            goal_type=GoalType.CONSTRUCTION,
            requirements={"buildings": {"residential": 10, "commercial": 5, "industrial": 5}},
            rewards={"funds": 8000, "experience": 300}
        )
        
        # Environmental goals
        self.all_goals["green_city"] = Goal(
            id="green_city",
            name="Green City",
            japanese_name="グリーンシティ",
            description="Keep pollution below 20%",
            japanese_description="汚染を20%以下に維持",
            goal_type=GoalType.ENVIRONMENT,
            requirements={"pollution": 20},
            rewards={"funds": 10000, "experience": 500, "building": "solar_plant"}
        )
        
        # Disaster goals
        self.all_goals["disaster_ready"] = Goal(
            id="disaster_ready",
            name="Disaster Preparedness",
            japanese_name="災害対策",
            description="Build emergency services",
            japanese_description="緊急サービスを建設",
            goal_type=GoalType.DISASTER,
            requirements={"buildings": {"fire_station": 2, "police": 2, "hospital": 1}},
            rewards={"funds": 15000, "experience": 800}
        )
        
        self.all_goals["survivor"] = Goal(
            id="survivor",
            name="Survivor",
            japanese_name="生存者",
            description="Survive 3 disasters",
            japanese_description="3つの災害を乗り越える",
            goal_type=GoalType.DISASTER,
            requirements={"disasters_survived": 3},
            rewards={"funds": 25000, "experience": 1500, "title": "災害マスター"}
        )
    
    def _create_quest_chains(self):
        """Create quest chains"""
        
        # Main story quest chain
        main_chain = QuestChain("main_story", "City Builder's Journey", "都市建設者の旅")
        main_chain.add_goal(self.all_goals["first_citizens"])
        main_chain.add_goal(self.all_goals["infrastructure"])
        main_chain.add_goal(self.all_goals["mixed_zones"])
        main_chain.add_goal(self.all_goals["small_town"])
        main_chain.add_goal(self.all_goals["profitable"])
        main_chain.add_goal(self.all_goals["city_status"])
        self.quest_chains["main_story"] = main_chain
        
        # Economic quest chain
        eco_chain = QuestChain("economic_mastery", "Economic Mastery", "経済マスター")
        eco_chain.add_goal(self.all_goals["profitable"])
        eco_chain.add_goal(self.all_goals["economic_boom"])
        self.quest_chains["economic_mastery"] = eco_chain
        
        # Environmental quest chain
        env_chain = QuestChain("green_revolution", "Green Revolution", "グリーン革命")
        env_chain.add_goal(self.all_goals["green_city"])
        self.quest_chains["green_revolution"] = env_chain
    
    def _generate_daily_challenges(self):
        """Generate daily challenges"""
        challenge_templates = [
            {
                "name": "Road Builder",
                "japanese_name": "道路建設者",
                "description": "Build 20 road tiles today",
                "japanese_description": "今日20の道路タイルを建設",
                "objectives": [{"action": "build_roads", "count": 20}],
                "rewards": {"funds": 2000, "experience": 100}
            },
            {
                "name": "Population Boost",
                "japanese_name": "人口増加",
                "description": "Increase population by 100",
                "japanese_description": "人口を100人増やす",
                "objectives": [{"action": "increase_population", "count": 100}],
                "rewards": {"funds": 3000, "experience": 150}
            },
            {
                "name": "Money Maker",
                "japanese_name": "金儲け",
                "description": "Earn ¥10,000 today",
                "japanese_description": "今日1万円を稼ぐ",
                "objectives": [{"action": "earn_money", "amount": 10000}],
                "rewards": {"funds": 5000, "experience": 200}
            },
            {
                "name": "Clean Air",
                "japanese_name": "きれいな空気",
                "description": "Reduce pollution by 10%",
                "japanese_description": "汚染を10%削減",
                "objectives": [{"action": "reduce_pollution", "amount": 10}],
                "rewards": {"funds": 4000, "experience": 180}
            },
            {
                "name": "Happy Citizens",
                "japanese_name": "幸せな市民",
                "description": "Achieve 80% happiness rating",
                "japanese_description": "幸福度80%を達成",
                "objectives": [{"action": "happiness", "amount": 80}],
                "rewards": {"funds": 3500, "experience": 160}
            }
        ]
        
        # Select 3 random challenges for today
        selected = random.sample(challenge_templates, min(3, len(challenge_templates)))
        
        for i, template in enumerate(selected):
            challenge = Challenge(
                id=f"daily_{datetime.now().strftime('%Y%m%d')}_{i}",
                name=template["name"],
                japanese_name=template["japanese_name"],
                description=template["description"],
                japanese_description=template["japanese_description"],
                challenge_type=ChallengeType.DAILY,
                objectives=template["objectives"],
                rewards=template["rewards"],
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(days=1)
            )
            self.daily_challenges.append(challenge)
    
    def activate_goal(self, goal_id: str) -> bool:
        """Activate a goal"""
        if goal_id not in self.all_goals:
            return False
        
        goal = self.all_goals[goal_id]
        
        # Check prerequisites
        for prereq in goal.prerequisite_goals:
            if prereq not in self.completed_goals:
                return False
        
        if goal.status == GoalStatus.LOCKED:
            goal.status = GoalStatus.AVAILABLE
        
        if goal.status == GoalStatus.AVAILABLE:
            goal.status = GoalStatus.IN_PROGRESS
            goal.start_time = datetime.now().timestamp()
            self.active_goals.append(goal_id)
            return True
        
        return False
    
    def update_goals(self, game_state: Dict[str, Any]):
        """Update all active goals"""
        for goal_id in self.active_goals[:]:
            goal = self.all_goals[goal_id]
            
            # Update progress
            goal.update_progress(game_state)
            
            # Check completion
            if goal.check_requirements(game_state):
                self.complete_goal(goal_id)
            
            # Check time limit
            if goal.time_limit and goal.start_time:
                elapsed_days = (datetime.now().timestamp() - goal.start_time) / 86400
                if elapsed_days > goal.time_limit:
                    self.fail_goal(goal_id)
    
    def complete_goal(self, goal_id: str):
        """Mark goal as completed"""
        if goal_id in self.active_goals:
            goal = self.all_goals[goal_id]
            goal.status = GoalStatus.COMPLETED
            goal.completion_time = datetime.now().timestamp()
            
            self.active_goals.remove(goal_id)
            self.completed_goals.append(goal_id)
            self.total_goals_completed += 1
            
            # Track rewards
            for reward_type, amount in goal.rewards.items():
                if reward_type not in self.total_rewards_earned:
                    self.total_rewards_earned[reward_type] = 0
                self.total_rewards_earned[reward_type] += amount
            
            # Check quest chain advancement
            for chain_id, chain in self.quest_chains.items():
                current = chain.get_current_goal()
                if current and current.id == goal_id:
                    chain.advance()
            
            # Unlock dependent goals
            for other_goal_id, other_goal in self.all_goals.items():
                if goal_id in other_goal.prerequisite_goals:
                    all_prereqs_met = all(
                        prereq in self.completed_goals 
                        for prereq in other_goal.prerequisite_goals
                    )
                    if all_prereqs_met and other_goal.status == GoalStatus.LOCKED:
                        other_goal.status = GoalStatus.AVAILABLE
    
    def fail_goal(self, goal_id: str):
        """Mark goal as failed"""
        if goal_id in self.active_goals:
            goal = self.all_goals[goal_id]
            goal.status = GoalStatus.FAILED
            self.active_goals.remove(goal_id)
    
    def claim_rewards(self, goal_id: str) -> Dict[str, Any]:
        """Claim rewards for completed goal"""
        goal = self.all_goals.get(goal_id)
        if goal and goal.status == GoalStatus.COMPLETED:
            goal.status = GoalStatus.CLAIMED
            return goal.rewards
        return {}
    
    def get_active_goals_display(self) -> List[Dict[str, Any]]:
        """Get active goals for display"""
        display_goals = []
        for goal_id in self.active_goals:
            goal = self.all_goals[goal_id]
            display_goals.append({
                "id": goal.id,
                "name": goal.japanese_name,
                "description": goal.japanese_description,
                "progress": goal.get_progress_percentage(),
                "rewards": goal.rewards,
                "time_remaining": goal.time_limit if goal.time_limit else None
            })
        return display_goals
    
    def get_available_goals(self) -> List[Goal]:
        """Get all available goals"""
        return [
            goal for goal in self.all_goals.values() 
            if goal.status == GoalStatus.AVAILABLE
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get goals statistics"""
        return {
            "total_goals": len(self.all_goals),
            "completed_goals": self.total_goals_completed,
            "active_goals": len(self.active_goals),
            "total_rewards": self.total_rewards_earned,
            "quest_chains_completed": sum(
                1 for chain in self.quest_chains.values() if chain.completed
            ),
            "challenges_completed": self.total_challenges_completed
        }
    
    def save_progress(self, filename: str = "goals_progress.json"):
        """Save goals progress"""
        data = {
            "completed_goals": self.completed_goals,
            "active_goals": self.active_goals,
            "goal_progress": {
                goal_id: {
                    "status": goal.status.value,
                    "progress": goal.progress,
                    "start_time": goal.start_time,
                    "completion_time": goal.completion_time
                }
                for goal_id, goal in self.all_goals.items()
            },
            "statistics": self.get_statistics()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_progress(self, filename: str = "goals_progress.json"):
        """Load goals progress"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.completed_goals = data.get("completed_goals", [])
            self.active_goals = data.get("active_goals", [])
            
            # Restore goal states
            for goal_id, progress_data in data.get("goal_progress", {}).items():
                if goal_id in self.all_goals:
                    goal = self.all_goals[goal_id]
                    goal.status = GoalStatus(progress_data["status"])
                    goal.progress = progress_data["progress"]
                    goal.start_time = progress_data.get("start_time")
                    goal.completion_time = progress_data.get("completion_time")
            
            return True
        except Exception as e:
            print(f"Failed to load goals progress: {e}")
            return False