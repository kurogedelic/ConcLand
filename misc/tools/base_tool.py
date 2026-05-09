"""
Base tool class for ConcLand city simulation tools
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple

class BaseTool(ABC):
    """Base class for all city simulation tools"""
    
    def __init__(self, tool_id: str, name: str, japanese_name: str, 
                 category: str, cost: int = 0, icon_index: int = 0):
        self.tool_id = tool_id
        self.name = name
        self.japanese_name = japanese_name
        self.category = category
        self.cost = cost
        self.icon_index = icon_index
        self.enabled = True
        
    @abstractmethod
    def can_place(self, city, x: int, y: int) -> bool:
        """Check if this tool can be used at the given position"""
        pass
    
    @abstractmethod
    def use_tool(self, city, x: int, y: int) -> bool:
        """Use the tool at the given position. Returns True if successful"""
        pass
    
    def get_preview_info(self, city, x: int, y: int) -> Optional[Dict[str, Any]]:
        """Get preview information for this tool at the given position"""
        return None
    
    def get_tooltip(self) -> str:
        """Get tooltip text for this tool"""
        return f"{self.japanese_name} (¥{self.cost})"
    
    def check_requirements(self, city) -> bool:
        """Check if tool requirements are met (funds, tech, etc.)"""
        return city.funds >= self.cost

class BuildingTool(BaseTool):
    """Base class for building placement tools"""
    
    def __init__(self, tool_id: str, name: str, japanese_name: str,
                 category: str, cost: int, icon_index: int,
                 building_type: str, size: Tuple[int, int] = (1, 1)):
        super().__init__(tool_id, name, japanese_name, category, cost, icon_index)
        self.building_type = building_type
        self.size = size
    
    def can_place(self, city, x: int, y: int) -> bool:
        """Check if building can be placed at position"""
        # Check bounds
        if not (0 <= x < city.width and 0 <= y < city.height):
            return False
        
        # Check if area is clear
        for dx in range(self.size[0]):
            for dy in range(self.size[1]):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < city.width and 0 <= ny < city.height):
                    return False
                if city.buildings[ny][nx] is not None:
                    return False
        
        return True
    
    def use_tool(self, city, x: int, y: int) -> bool:
        """Place building at position"""
        if not self.can_place(city, x, y) or not self.check_requirements(city):
            return False
        
        # Deduct cost
        city.funds -= self.cost
        
        # Place building
        for dx in range(self.size[0]):
            for dy in range(self.size[1]):
                nx, ny = x + dx, y + dy
                city.buildings[ny][nx] = self.building_type
        
        return True

class InfrastructureTool(BaseTool):
    """Base class for infrastructure tools (roads, power lines, etc.)"""
    
    def __init__(self, tool_id: str, name: str, japanese_name: str,
                 category: str, cost: int, icon_index: int,
                 infrastructure_type: str):
        super().__init__(tool_id, name, japanese_name, category, cost, icon_index)
        self.infrastructure_type = infrastructure_type
    
    def can_place(self, city, x: int, y: int) -> bool:
        """Check if infrastructure can be placed"""
        if not (0 <= x < city.width and 0 <= y < city.height):
            return False
        
        # Allow placing over existing infrastructure of same type
        current = city.infrastructure.get((x, y))
        return current is None or current == self.infrastructure_type
    
    def use_tool(self, city, x: int, y: int) -> bool:
        """Place infrastructure at position"""
        if not self.can_place(city, x, y) or not self.check_requirements(city):
            return False
        
        # Only charge if not replacing same type
        current = city.infrastructure.get((x, y))
        if current != self.infrastructure_type:
            city.funds -= self.cost
            city.infrastructure[(x, y)] = self.infrastructure_type
        
        return True

class TerrainTool(BaseTool):
    """Base class for terrain modification tools"""
    
    def __init__(self, tool_id: str, name: str, japanese_name: str,
                 category: str, cost: int, icon_index: int,
                 terrain_type: str):
        super().__init__(tool_id, name, japanese_name, category, cost, icon_index)
        self.terrain_type = terrain_type
    
    def can_place(self, city, x: int, y: int) -> bool:
        """Check if terrain can be modified"""
        if not (0 <= x < city.width and 0 <= y < city.height):
            return False
        
        # Can't modify if there's a building
        return city.buildings[y][x] is None
    
    def use_tool(self, city, x: int, y: int) -> bool:
        """Modify terrain at position"""
        if not self.can_place(city, x, y) or not self.check_requirements(city):
            return False
        
        city.funds -= self.cost
        city.terrain[y][x] = self.terrain_type
        return True

class UtilityTool(BaseTool):
    """Base class for utility tools (bulldozer, inspector, etc.)"""
    
    def __init__(self, tool_id: str, name: str, japanese_name: str,
                 category: str, cost: int, icon_index: int):
        super().__init__(tool_id, name, japanese_name, category, cost, icon_index)
    
    def can_place(self, city, x: int, y: int) -> bool:
        """Utility tools can generally be used anywhere"""
        return 0 <= x < city.width and 0 <= y < city.height
    
    def use_tool(self, city, x: int, y: int) -> bool:
        """Default utility tool behavior - override in specific tools"""
        return self.can_place(city, x, y)