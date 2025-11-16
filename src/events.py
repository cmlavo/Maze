"""
Events module for the board game simulator.
Represents various events that can occur during gameplay.
"""
from enum import Enum
from typing import Dict, List, Optional, Callable
import random


class EventType(Enum):
    """Enumeration of event types."""
    COMBAT = "combat"
    TREASURE = "treasure"
    TRAP = "trap"
    ENCOUNTER = "encounter"
    REST = "rest"
    MERCHANT = "merchant"
    PUZZLE = "puzzle"
    BOSS = "boss"
    STORY = "story"


class EventPriority(Enum):
    """Enumeration of event priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class Event:
    """
    Represents an event that can occur in the board game.
    
    Attributes:
        name (str): Event's name
        event_type (EventType): Type of event
        description (str): Event description
        priority (EventPriority): Event priority
        effects (dict): Dictionary of effects
        choices (list): Available choices for the event
        requirements (dict): Requirements to trigger the event
        probability (float): Base probability of occurrence (0.0-1.0)
        one_time (bool): Whether event can only occur once
        triggered (bool): Whether event has been triggered
    """
    
    def __init__(self,
                 name: str,
                 event_type: EventType,
                 description: str,
                 priority: EventPriority = EventPriority.NORMAL,
                 effects: dict = None,
                 choices: list = None,
                 requirements: dict = None,
                 probability: float = 1.0,
                 one_time: bool = False):
        """
        Initialize an Event.
        
        Args:
            name (str): Event's name
            event_type (EventType): Type of event
            description (str): Event description
            priority (EventPriority): Event priority
            effects (dict): Dictionary of effects
            choices (list): Available choices for the event
            requirements (dict): Requirements to trigger event
            probability (float): Base probability of occurrence
            one_time (bool): Whether event can only occur once
        """
        self.name = name
        self.event_type = event_type
        self.description = description
        self.priority = priority
        self.effects = effects or {}
        self.choices = choices or []
        self.requirements = requirements or {}
        self.probability = probability
        self.one_time = one_time
        self.triggered = False
    
    def can_trigger(self, context: dict) -> bool:
        """
        Check if event can be triggered given the current context.
        
        Args:
            context (dict): Game state context (player stats, inventory, etc.)
            
        Returns:
            bool: True if event can trigger
        """
        # Check if one-time event already triggered
        if self.one_time and self.triggered:
            return False
        
        # Check requirements
        for req_key, req_value in self.requirements.items():
            if req_key not in context:
                return False
            
            if isinstance(req_value, (int, float)):
                if context[req_key] < req_value:
                    return False
            elif isinstance(req_value, list):
                if context[req_key] not in req_value:
                    return False
            elif context[req_key] != req_value:
                return False
        
        # Check probability
        return random.random() < self.probability
    
    def trigger(self, target=None) -> Dict:
        """
        Trigger the event.
        
        Args:
            target: Target entity (player, monster, etc.)
            
        Returns:
            Dict: Event results
        """
        self.triggered = True
        
        result = {
            'event_name': self.name,
            'event_type': self.event_type.value,
            'description': self.description,
            'effects_applied': {},
            'choices_available': len(self.choices) > 0,
            'choices': [choice['description'] for choice in self.choices]
        }
        
        # Apply automatic effects
        if target:
            for effect_type, effect_value in self.effects.items():
                if hasattr(target, effect_type):
                    current_value = getattr(target, effect_type)
                    if isinstance(current_value, (int, float)):
                        setattr(target, effect_type, current_value + effect_value)
                        result['effects_applied'][effect_type] = effect_value
        
        return result
    
    def make_choice(self, choice_index: int, target=None) -> Dict:
        """
        Make a choice for events with multiple options.
        
        Args:
            choice_index (int): Index of the chosen option
            target: Target entity
            
        Returns:
            Dict: Choice results
        """
        if choice_index < 0 or choice_index >= len(self.choices):
            return {
                'success': False,
                'message': 'Invalid choice'
            }
        
        choice = self.choices[choice_index]
        result = {
            'success': True,
            'choice': choice['description'],
            'outcome': choice.get('outcome', ''),
            'effects_applied': {}
        }
        
        # Apply choice effects
        if target and 'effects' in choice:
            for effect_type, effect_value in choice['effects'].items():
                if hasattr(target, effect_type):
                    current_value = getattr(target, effect_type)
                    if isinstance(current_value, (int, float)):
                        setattr(target, effect_type, current_value + effect_value)
                        result['effects_applied'][effect_type] = effect_value
        
        return result
    
    def reset(self):
        """Reset the event so it can be triggered again."""
        self.triggered = False
    
    def __str__(self) -> str:
        """String representation of the event."""
        return f"{self.name} ({self.event_type.value}, Priority: {self.priority.value})"
    
    def __repr__(self) -> str:
        """Detailed representation of the event."""
        return (f"Event(name='{self.name}', type={self.event_type}, "
                f"priority={self.priority}, triggered={self.triggered})")


class EventManager:
    """
    Manages events in the game.
    
    Attributes:
        events (list): List of all events
        active_events (list): Currently active events
        event_history (list): History of triggered events
    """
    
    def __init__(self):
        """Initialize the EventManager."""
        self.events = []
        self.active_events = []
        self.event_history = []
    
    def add_event(self, event: Event):
        """
        Add an event to the manager.
        
        Args:
            event (Event): Event to add
        """
        self.events.append(event)
    
    def remove_event(self, event: Event):
        """
        Remove an event from the manager.
        
        Args:
            event (Event): Event to remove
        """
        if event in self.events:
            self.events.remove(event)
    
    def check_events(self, context: dict) -> List[Event]:
        """
        Check which events can trigger given the current context.
        
        Args:
            context (dict): Game state context
            
        Returns:
            List[Event]: List of events that can trigger
        """
        triggerable = []
        for event in self.events:
            if event.can_trigger(context):
                triggerable.append(event)
        
        # Sort by priority
        triggerable.sort(key=lambda e: e.priority.value, reverse=True)
        return triggerable
    
    def trigger_event(self, event: Event, target=None) -> Dict:
        """
        Trigger a specific event.
        
        Args:
            event (Event): Event to trigger
            target: Target entity
            
        Returns:
            Dict: Event results
        """
        result = event.trigger(target)
        self.event_history.append({
            'event': event,
            'result': result,
            'timestamp': len(self.event_history)
        })
        
        if event not in self.active_events:
            self.active_events.append(event)
        
        return result
    
    def resolve_active_event(self, event: Event):
        """
        Remove an event from active events.
        
        Args:
            event (Event): Event to resolve
        """
        if event in self.active_events:
            self.active_events.remove(event)
    
    def get_event_history(self) -> List[Dict]:
        """
        Get the history of triggered events.
        
        Returns:
            List[Dict]: Event history
        """
        return self.event_history.copy()
    
    def reset_all_events(self):
        """Reset all events so they can be triggered again."""
        for event in self.events:
            event.reset()
        self.active_events.clear()
        self.event_history.clear()


# Predefined event templates
class EventTemplates:
    """Common event templates for quick event creation."""
    
    @staticmethod
    def treasure_chest() -> Event:
        """Create a treasure chest event."""
        return Event(
            name="Treasure Chest",
            event_type=EventType.TREASURE,
            description="You found a treasure chest!",
            effects={'gold': 50},
            choices=[
                {'description': 'Open the chest', 'effects': {'gold': 50}, 'outcome': 'You found 50 gold!'},
                {'description': 'Check for traps first', 'effects': {'gold': 30}, 'outcome': 'Safe approach, but some gold was lost.'},
                {'description': 'Leave it alone', 'effects': {}, 'outcome': 'You walk away.'}
            ],
            probability=0.3
        )
    
    @staticmethod
    def poison_trap() -> Event:
        """Create a poison trap event."""
        return Event(
            name="Poison Trap",
            event_type=EventType.TRAP,
            description="You triggered a poison trap!",
            priority=EventPriority.HIGH,
            effects={'health': -20},
            probability=0.2
        )
    
    @staticmethod
    def healing_fountain() -> Event:
        """Create a healing fountain event."""
        return Event(
            name="Healing Fountain",
            event_type=EventType.REST,
            description="You discover a magical healing fountain.",
            effects={'health': 30},
            one_time=True,
            probability=0.15
        )
    
    @staticmethod
    def merchant_encounter() -> Event:
        """Create a merchant encounter event."""
        return Event(
            name="Wandering Merchant",
            event_type=EventType.MERCHANT,
            description="A merchant offers to trade with you.",
            choices=[
                {'description': 'Buy health potion (30 gold)', 'effects': {'gold': -30}, 'outcome': 'Purchased health potion'},
                {'description': 'Buy weapon upgrade (50 gold)', 'effects': {'gold': -50, 'attack': 5}, 'outcome': 'Weapon upgraded!'},
                {'description': 'Sell items', 'effects': {'gold': 20}, 'outcome': 'Items sold'},
                {'description': 'Leave', 'effects': {}, 'outcome': 'You walk away.'}
            ],
            requirements={'gold': 10},
            probability=0.25
        )
    
    @staticmethod
    def boss_encounter() -> Event:
        """Create a boss encounter event."""
        return Event(
            name="Boss Battle",
            event_type=EventType.BOSS,
            description="A powerful boss blocks your path!",
            priority=EventPriority.CRITICAL,
            requirements={'level': 3},
            one_time=True,
            probability=1.0
        )
