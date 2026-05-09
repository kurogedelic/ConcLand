"""
Historical Events System for ConcLand
Manages historical events, disasters, and random events that affect the city
"""
import json
import random
from datetime import date, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Event:
    """Represents a game event"""
    id: str
    name: str
    japanese_name: str
    category: str
    priority: str
    description: str
    effects: Dict[str, Any]
    trigger_date: Optional[date] = None
    duration_months: int = 0
    probability: float = 0.0
    seasonal: Optional[str] = None
    notification: Optional[Dict[str, str]] = None

@dataclass
class ActiveEvent:
    """Represents an active event affecting the game"""
    event: Event
    start_date: date
    end_date: date
    current_effects: Dict[str, Any]
    
class EventSystem:
    """Manages all game events"""
    
    def __init__(self):
        self.historical_events: Dict[str, Event] = {}
        self.disaster_events: Dict[str, Event] = {}
        self.random_events: Dict[str, Event] = {}
        self.event_chains: Dict[str, Dict] = {}
        
        # Active events
        self.active_events: List[ActiveEvent] = []
        self.triggered_events: set = set()
        self.event_history: List[Dict[str, Any]] = []
        
        # Event timing
        self.last_random_check = date(1945, 8, 15)
        self.random_check_interval = 30  # Check for random events every 30 days
        
        # Load event data
        self.load_event_data()
    
    def load_event_data(self):
        """Load event definitions from JSON"""
        try:
            with open('data/historical/events.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load historical events
            for event_data in data.get('historical_events', []):
                event = self._create_event_from_data(event_data)
                if event.trigger_date:
                    self.historical_events[event.id] = event
            
            # Load disaster events
            for event_data in data.get('disaster_events', []):
                event = self._create_event_from_data(event_data)
                self.disaster_events[event.id] = event
            
            # Load random events
            for event_data in data.get('random_events', []):
                event = self._create_event_from_data(event_data)
                self.random_events[event.id] = event
            
            # Load event chains
            self.event_chains = data.get('event_chains', {})
            
        except FileNotFoundError:
            print("Event data file not found. Using fallback data.")
            self._create_fallback_events()
    
    def _create_event_from_data(self, event_data: Dict[str, Any]) -> Event:
        """Create an Event object from JSON data"""
        trigger_date = None
        if 'trigger_date' in event_data:
            try:
                trigger_date = date.fromisoformat(event_data['trigger_date'])
            except ValueError:
                pass
        
        return Event(
            id=event_data['id'],
            name=event_data['name'],
            japanese_name=event_data['japanese_name'],
            category=event_data['category'],
            priority=event_data.get('priority', 'medium'),
            description=event_data['description'],
            effects=event_data.get('effects', {}),
            trigger_date=trigger_date,
            duration_months=event_data.get('duration_months', 0),
            probability=event_data.get('probability', 0.0),
            seasonal=event_data.get('seasonal'),
            notification=event_data.get('notification')
        )
    
    def _create_fallback_events(self):
        """Create basic event data if JSON loading fails"""
        fallback_event = Event(
            id="test_event",
            name="Test Event",
            japanese_name="テストイベント",
            category="test",
            priority="low",
            description="テスト用イベント",
            effects={"economic": {"funds_bonus": 1000}},
            trigger_date=date(1950, 1, 1)
        )
        self.historical_events["test_event"] = fallback_event
    
    def update(self, current_date: date, current_era: str, season: str, 
               city_state: Dict[str, Any]) -> List[Event]:
        """Update event system and return newly triggered events"""
        triggered_events = []
        
        # Check for historical events
        historical_triggers = self._check_historical_events(current_date, current_era)
        triggered_events.extend(historical_triggers)
        
        # Check for random events
        if (current_date - self.last_random_check).days >= self.random_check_interval:
            random_triggers = self._check_random_events(current_date, season, city_state)
            triggered_events.extend(random_triggers)
            self.last_random_check = current_date
        
        # Update active events
        self._update_active_events(current_date)
        
        # Process newly triggered events
        for event in triggered_events:
            self._activate_event(event, current_date)
        
        return triggered_events
    
    def _check_historical_events(self, current_date: date, current_era: str) -> List[Event]:
        """Check for historical events that should trigger"""
        triggered = []
        
        for event_id, event in self.historical_events.items():
            if (event_id not in self.triggered_events and 
                event.trigger_date and
                current_date >= event.trigger_date):
                
                # Check if event is appropriate for current era
                if hasattr(event, 'era') and event.era != current_era:
                    continue
                
                triggered.append(event)
                self.triggered_events.add(event_id)
        
        return triggered
    
    def _check_random_events(self, current_date: date, season: str, 
                           city_state: Dict[str, Any]) -> List[Event]:
        """Check for random events that might trigger"""
        triggered = []
        
        # Check disaster events
        for event_id, event in self.disaster_events.items():
            if self._should_trigger_random_event(event, season, city_state):
                triggered.append(event)
        
        # Check general random events
        for event_id, event in self.random_events.items():
            if self._should_trigger_random_event(event, season, city_state):
                triggered.append(event)
        
        return triggered
    
    def _should_trigger_random_event(self, event: Event, season: str, 
                                   city_state: Dict[str, Any]) -> bool:
        """Determine if a random event should trigger"""
        # Check base probability
        if random.random() > event.probability:
            return False
        
        # Check seasonal requirements
        if event.seasonal and event.seasonal != season:
            return False
        
        # Additional checks based on city state could be added here
        # For example, fire events more likely in dense wooden areas
        
        return True
    
    def _activate_event(self, event: Event, current_date: date):
        """Activate an event"""
        end_date = current_date
        if event.duration_months > 0:
            # Approximate month calculation
            end_date += timedelta(days=event.duration_months * 30)
        
        active_event = ActiveEvent(
            event=event,
            start_date=current_date,
            end_date=end_date,
            current_effects=event.effects.copy()
        )
        
        self.active_events.append(active_event)
        
        # Add to history
        self.event_history.append({
            "event_id": event.id,
            "event_name": event.japanese_name,
            "date": current_date.isoformat(),
            "category": event.category,
            "priority": event.priority
        })
    
    def _update_active_events(self, current_date: date):
        """Update active events and remove expired ones"""
        self.active_events = [
            active_event for active_event in self.active_events
            if current_date <= active_event.end_date
        ]
    
    def get_active_effects(self) -> Dict[str, Any]:
        """Get combined effects from all active events"""
        combined_effects = defaultdict(lambda: defaultdict(float))
        
        for active_event in self.active_events:
            effects = active_event.current_effects
            
            for category, category_effects in effects.items():
                if isinstance(category_effects, dict):
                    for effect_name, value in category_effects.items():
                        if isinstance(value, (int, float)):
                            # Multiplicative effects
                            if effect_name.endswith('_bonus') or effect_name.endswith('_penalty'):
                                if combined_effects[category][effect_name] == 0:
                                    combined_effects[category][effect_name] = value
                                else:
                                    combined_effects[category][effect_name] *= value
                            # Additive effects
                            else:
                                combined_effects[category][effect_name] += value
                        else:
                            # Non-numeric effects (like unlocks)
                            if effect_name not in combined_effects[category]:
                                combined_effects[category][effect_name] = []
                            if isinstance(value, list):
                                combined_effects[category][effect_name].extend(value)
                            else:
                                combined_effects[category][effect_name].append(value)
        
        # Convert back to regular dict
        return {cat: dict(effects) for cat, effects in combined_effects.items()}
    
    def get_economic_modifier(self, modifier_name: str) -> float:
        """Get economic modifier from active events"""
        effects = self.get_active_effects()
        economic_effects = effects.get('economic', {})
        return economic_effects.get(modifier_name, 1.0)
    
    def get_population_modifier(self, modifier_name: str) -> float:
        """Get population modifier from active events"""
        effects = self.get_active_effects()
        population_effects = effects.get('population', {})
        return population_effects.get(modifier_name, 1.0)
    
    def get_unlocked_technologies(self) -> List[str]:
        """Get technologies unlocked by active events"""
        effects = self.get_active_effects()
        tech_effects = effects.get('technology', {})
        return tech_effects.get('unlock', [])
    
    def get_unlocked_buildings(self) -> List[str]:
        """Get buildings unlocked by active events"""
        effects = self.get_active_effects()
        building_effects = effects.get('buildings', {})
        return building_effects.get('unlock', [])
    
    def get_resource_demand_modifiers(self) -> Dict[str, float]:
        """Get resource demand modifiers from active events"""
        effects = self.get_active_effects()
        economic_effects = effects.get('economic', {})
        return economic_effects.get('resource_demand', {})
    
    def get_price_modifiers(self) -> Dict[str, float]:
        """Get price modifiers from active events"""
        effects = self.get_active_effects()
        economic_effects = effects.get('economic', {})
        return economic_effects.get('price_boost', {})
    
    def get_active_event_summaries(self) -> List[Dict[str, Any]]:
        """Get summaries of currently active events for display"""
        summaries = []
        for active_event in self.active_events:
            event = active_event.event
            summaries.append({
                "id": event.id,
                "name": event.japanese_name,
                "description": event.description,
                "category": event.category,
                "priority": event.priority,
                "start_date": active_event.start_date.strftime("%Y年%m月%d日"),
                "end_date": active_event.end_date.strftime("%Y年%m月%d日"),
                "days_remaining": (active_event.end_date - active_event.start_date).days
            })
        return summaries
    
    def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent events from history"""
        return self.event_history[-limit:] if self.event_history else []
    
    def force_trigger_event(self, event_id: str, current_date: date) -> bool:
        """Force trigger an event (for testing/cheats)"""
        # Check all event collections
        event = None
        if event_id in self.historical_events:
            event = self.historical_events[event_id]
        elif event_id in self.disaster_events:
            event = self.disaster_events[event_id]
        elif event_id in self.random_events:
            event = self.random_events[event_id]
        
        if event:
            self._activate_event(event, current_date)
            if event_id in self.historical_events:
                self.triggered_events.add(event_id)
            return True
        
        return False
    
    def get_event_notifications(self) -> List[Dict[str, str]]:
        """Get pending event notifications"""
        notifications = []
        
        # Get notifications from recently activated events
        recent_events = self.get_recent_events(5)
        for event_data in recent_events:
            event_id = event_data['event_id']
            
            # Find the event to get notification data
            event = None
            if event_id in self.historical_events:
                event = self.historical_events[event_id]
            elif event_id in self.disaster_events:
                event = self.disaster_events[event_id]
            elif event_id in self.random_events:
                event = self.random_events[event_id]
            
            if event and event.notification:
                notifications.append({
                    "title": event.notification.get("title", event.japanese_name),
                    "message": event.notification.get("message", event.description),
                    "icon": event.notification.get("icon", "info"),
                    "sound": event.notification.get("sound", "notification"),
                    "priority": event.priority
                })
        
        return notifications
    
    def clear_event_history(self):
        """Clear event history (for new game)"""
        self.event_history.clear()
        self.triggered_events.clear()
        self.active_events.clear()
    
    def export_state(self) -> Dict[str, Any]:
        """Export event system state for saving"""
        return {
            "triggered_events": list(self.triggered_events),
            "event_history": self.event_history,
            "active_events": [
                {
                    "event_id": ae.event.id,
                    "start_date": ae.start_date.isoformat(),
                    "end_date": ae.end_date.isoformat(),
                    "current_effects": ae.current_effects
                }
                for ae in self.active_events
            ],
            "last_random_check": self.last_random_check.isoformat()
        }
    
    def import_state(self, state: Dict[str, Any]):
        """Import event system state from save data"""
        try:
            self.triggered_events = set(state.get("triggered_events", []))
            self.event_history = state.get("event_history", [])
            self.last_random_check = date.fromisoformat(state.get("last_random_check", "1945-08-15"))
            
            # Restore active events
            self.active_events.clear()
            for ae_data in state.get("active_events", []):
                event_id = ae_data["event_id"]
                
                # Find the event
                event = None
                if event_id in self.historical_events:
                    event = self.historical_events[event_id]
                elif event_id in self.disaster_events:
                    event = self.disaster_events[event_id]
                elif event_id in self.random_events:
                    event = self.random_events[event_id]
                
                if event:
                    active_event = ActiveEvent(
                        event=event,
                        start_date=date.fromisoformat(ae_data["start_date"]),
                        end_date=date.fromisoformat(ae_data["end_date"]),
                        current_effects=ae_data["current_effects"]
                    )
                    self.active_events.append(active_event)
        
        except (KeyError, ValueError) as e:
            print(f"Error importing event system state: {e}")

class EventNotificationManager:
    """Manages event notifications for the UI"""
    
    def __init__(self):
        self.pending_notifications: List[Dict[str, Any]] = []
        self.shown_notifications: set = set()
    
    def add_notification(self, notification: Dict[str, Any]):
        """Add a new notification"""
        notification_id = f"{notification.get('title', '')}_{notification.get('message', '')}"
        if notification_id not in self.shown_notifications:
            self.pending_notifications.append(notification)
            self.shown_notifications.add(notification_id)
    
    def get_next_notification(self) -> Optional[Dict[str, Any]]:
        """Get the next notification to show"""
        if self.pending_notifications:
            return self.pending_notifications.pop(0)
        return None
    
    def has_pending_notifications(self) -> bool:
        """Check if there are pending notifications"""
        return len(self.pending_notifications) > 0
    
    def clear_notifications(self):
        """Clear all notifications"""
        self.pending_notifications.clear()
        self.shown_notifications.clear()