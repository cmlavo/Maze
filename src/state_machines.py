"""
State machines for controlling player and monster behavior in the simulator.
"""
from enum import Enum
from typing import Optional, Dict
import random


class PlayerState(Enum):
    """States for player behavior."""
    EXPLORING = "exploring"
    COMBAT = "combat"
    RESTING = "resting"
    LOOTING = "looting"
    FLEEING = "fleeing"
    SHOPPING = "shopping"
    DEAD = "dead"


class MonsterState(Enum):
    """States for monster behavior."""
    IDLE = "idle"
    PATROLLING = "patrolling"
    CHASING = "chasing"
    ATTACKING = "attacking"
    FLEEING = "fleeing"
    DEAD = "dead"


class PlayerBehaviorSettings:
    """
    Settings to adjust player behavior in simulations.
    
    Attributes:
        aggression (float): How aggressive the player is (0.0-1.0)
        caution (float): How cautious the player is (0.0-1.0)
        greed (float): How greedy the player is (0.0-1.0)
        exploration (float): How much the player explores (0.0-1.0)
        health_threshold (float): Health % to retreat/rest (0.0-1.0)
    """
    
    def __init__(self,
                 aggression: float = 0.5,
                 caution: float = 0.5,
                 greed: float = 0.5,
                 exploration: float = 0.5,
                 health_threshold: float = 0.3):
        """
        Initialize player behavior settings.
        
        Args:
            aggression (float): Aggression level (0.0-1.0)
            caution (float): Caution level (0.0-1.0)
            greed (float): Greed level (0.0-1.0)
            exploration (float): Exploration tendency (0.0-1.0)
            health_threshold (float): Health % to retreat/rest (0.0-1.0)
        """
        self.aggression = max(0.0, min(1.0, aggression))
        self.caution = max(0.0, min(1.0, caution))
        self.greed = max(0.0, min(1.0, greed))
        self.exploration = max(0.0, min(1.0, exploration))
        self.health_threshold = max(0.0, min(1.0, health_threshold))
    
    @classmethod
    def aggressive(cls):
        """Create aggressive player behavior."""
        return cls(aggression=0.9, caution=0.2, greed=0.6, exploration=0.7, health_threshold=0.2)
    
    @classmethod
    def cautious(cls):
        """Create cautious player behavior."""
        return cls(aggression=0.3, caution=0.9, greed=0.3, exploration=0.4, health_threshold=0.5)
    
    @classmethod
    def greedy(cls):
        """Create greedy player behavior."""
        return cls(aggression=0.5, caution=0.4, greed=0.95, exploration=0.6, health_threshold=0.3)
    
    @classmethod
    def explorer(cls):
        """Create explorer player behavior."""
        return cls(aggression=0.4, caution=0.6, greed=0.4, exploration=0.95, health_threshold=0.4)
    
    @classmethod
    def balanced(cls):
        """Create balanced player behavior."""
        return cls(aggression=0.5, caution=0.5, greed=0.5, exploration=0.5, health_threshold=0.35)


class PlayerStateMachine:
    """
    State machine for controlling player behavior.
    
    Attributes:
        player: Player object
        state (PlayerState): Current state
        settings (PlayerBehaviorSettings): Behavior settings
        state_history (list): History of state changes
    """
    
    def __init__(self, player, settings: Optional[PlayerBehaviorSettings] = None):
        """
        Initialize the player state machine.
        
        Args:
            player: Player object to control
            settings (PlayerBehaviorSettings): Behavior settings
        """
        self.player = player
        self.state = PlayerState.EXPLORING
        self.settings = settings or PlayerBehaviorSettings.balanced()
        self.state_history = [self.state]
    
    def update(self, context: Dict) -> PlayerState:
        """
        Update the state machine based on context.
        
        Args:
            context (dict): Game state context
            
        Returns:
            PlayerState: New state
        """
        if not self.player.is_alive():
            self._change_state(PlayerState.DEAD)
            return self.state
        
        # Check health threshold
        health_ratio = self.player.health / self.player.max_health
        
        if self.state == PlayerState.EXPLORING:
            return self._update_exploring(context, health_ratio)
        elif self.state == PlayerState.COMBAT:
            return self._update_combat(context, health_ratio)
        elif self.state == PlayerState.RESTING:
            return self._update_resting(context, health_ratio)
        elif self.state == PlayerState.LOOTING:
            return self._update_looting(context, health_ratio)
        elif self.state == PlayerState.FLEEING:
            return self._update_fleeing(context, health_ratio)
        elif self.state == PlayerState.SHOPPING:
            return self._update_shopping(context, health_ratio)
        
        return self.state
    
    def _update_exploring(self, context: Dict, health_ratio: float) -> PlayerState:
        """Update logic for exploring state."""
        # Low health -> rest
        if health_ratio < self.settings.health_threshold:
            self._change_state(PlayerState.RESTING)
            return self.state
        
        # Enemy nearby -> combat or flee
        if context.get('enemies_nearby', 0) > 0:
            if random.random() < self.settings.aggression:
                self._change_state(PlayerState.COMBAT)
            elif random.random() < self.settings.caution:
                self._change_state(PlayerState.FLEEING)
            return self.state
        
        # Treasure nearby -> looting
        if context.get('treasure_nearby', False) and random.random() < self.settings.greed:
            self._change_state(PlayerState.LOOTING)
            return self.state
        
        # Merchant nearby -> shopping
        if context.get('merchant_nearby', False) and random.random() < self.settings.greed * 0.7:
            self._change_state(PlayerState.SHOPPING)
            return self.state
        
        return self.state
    
    def _update_combat(self, context: Dict, health_ratio: float) -> PlayerState:
        """Update logic for combat state."""
        # Low health and cautious -> flee
        if health_ratio < self.settings.health_threshold and random.random() < self.settings.caution:
            self._change_state(PlayerState.FLEEING)
            return self.state
        
        # No enemies -> back to exploring
        if context.get('enemies_nearby', 0) == 0:
            self._change_state(PlayerState.EXPLORING)
            return self.state
        
        return self.state
    
    def _update_resting(self, context: Dict, health_ratio: float) -> PlayerState:
        """Update logic for resting state."""
        # Health recovered -> exploring
        if health_ratio > 0.7:
            self._change_state(PlayerState.EXPLORING)
            return self.state
        
        # Enemy nearby and aggressive -> combat
        if context.get('enemies_nearby', 0) > 0 and random.random() < self.settings.aggression * 0.5:
            self._change_state(PlayerState.COMBAT)
            return self.state
        
        return self.state
    
    def _update_looting(self, context: Dict, health_ratio: float) -> PlayerState:
        """Update logic for looting state."""
        # Finished looting -> exploring
        if not context.get('treasure_nearby', False):
            self._change_state(PlayerState.EXPLORING)
            return self.state
        
        # Enemy nearby -> flee or combat
        if context.get('enemies_nearby', 0) > 0:
            if health_ratio < self.settings.health_threshold or random.random() < self.settings.caution:
                self._change_state(PlayerState.FLEEING)
            else:
                self._change_state(PlayerState.COMBAT)
            return self.state
        
        return self.state
    
    def _update_fleeing(self, context: Dict, health_ratio: float) -> PlayerState:
        """Update logic for fleeing state."""
        # Safe distance -> rest or explore
        if context.get('enemies_nearby', 0) == 0:
            if health_ratio < 0.5:
                self._change_state(PlayerState.RESTING)
            else:
                self._change_state(PlayerState.EXPLORING)
            return self.state
        
        return self.state
    
    def _update_shopping(self, context: Dict, health_ratio: float) -> PlayerState:
        """Update logic for shopping state."""
        # Finished shopping -> exploring
        if not context.get('merchant_nearby', False):
            self._change_state(PlayerState.EXPLORING)
            return self.state
        
        return self.state
    
    def _change_state(self, new_state: PlayerState):
        """Change to a new state."""
        if new_state != self.state:
            self.state = new_state
            self.state_history.append(new_state)
    
    def get_action(self) -> str:
        """
        Get the recommended action for the current state.
        
        Returns:
            str: Recommended action
        """
        actions = {
            PlayerState.EXPLORING: "explore",
            PlayerState.COMBAT: "attack",
            PlayerState.RESTING: "rest",
            PlayerState.LOOTING: "loot",
            PlayerState.FLEEING: "flee",
            PlayerState.SHOPPING: "shop",
            PlayerState.DEAD: "none"
        }
        return actions.get(self.state, "explore")


class MonsterBehaviorSettings:
    """
    Settings to adjust monster behavior in simulations.
    
    Attributes:
        aggression (float): How aggressive the monster is (0.0-1.0)
        patrol_range (int): How far the monster patrols
        chase_range (int): How far the monster chases players
        flee_health_threshold (float): Health % to flee (0.0-1.0)
    """
    
    def __init__(self,
                 aggression: float = 0.7,
                 patrol_range: int = 5,
                 chase_range: int = 8,
                 flee_health_threshold: float = 0.2):
        """
        Initialize monster behavior settings.
        
        Args:
            aggression (float): Aggression level (0.0-1.0)
            patrol_range (int): Patrol range
            chase_range (int): Chase range
            flee_health_threshold (float): Health % to flee (0.0-1.0)
        """
        self.aggression = max(0.0, min(1.0, aggression))
        self.patrol_range = max(1, patrol_range)
        self.chase_range = max(1, chase_range)
        self.flee_health_threshold = max(0.0, min(1.0, flee_health_threshold))
    
    @classmethod
    def aggressive(cls):
        """Create aggressive monster behavior."""
        return cls(aggression=0.95, patrol_range=7, chase_range=12, flee_health_threshold=0.1)
    
    @classmethod
    def defensive(cls):
        """Create defensive monster behavior."""
        return cls(aggression=0.4, patrol_range=3, chase_range=5, flee_health_threshold=0.4)
    
    @classmethod
    def balanced(cls):
        """Create balanced monster behavior."""
        return cls(aggression=0.7, patrol_range=5, chase_range=8, flee_health_threshold=0.2)


class MonsterStateMachine:
    """
    State machine for controlling monster behavior.
    
    Attributes:
        monster: Monster object
        state (MonsterState): Current state
        settings (MonsterBehaviorSettings): Behavior settings
        home_position (tuple): Original patrol position
        state_history (list): History of state changes
    """
    
    def __init__(self, monster, settings: Optional[MonsterBehaviorSettings] = None):
        """
        Initialize the monster state machine.
        
        Args:
            monster: Monster object to control
            settings (MonsterBehaviorSettings): Behavior settings
        """
        self.monster = monster
        self.state = MonsterState.IDLE
        self.settings = settings or MonsterBehaviorSettings.balanced()
        self.home_position = monster.position
        self.state_history = [self.state]
        self.target = None
    
    def update(self, context: Dict) -> MonsterState:
        """
        Update the state machine based on context.
        
        Args:
            context (dict): Game state context
            
        Returns:
            MonsterState: New state
        """
        if not self.monster.is_alive():
            self._change_state(MonsterState.DEAD)
            return self.state
        
        # Check health threshold
        health_ratio = self.monster.health / self.monster.max_health
        
        if self.state == MonsterState.IDLE:
            return self._update_idle(context, health_ratio)
        elif self.state == MonsterState.PATROLLING:
            return self._update_patrolling(context, health_ratio)
        elif self.state == MonsterState.CHASING:
            return self._update_chasing(context, health_ratio)
        elif self.state == MonsterState.ATTACKING:
            return self._update_attacking(context, health_ratio)
        elif self.state == MonsterState.FLEEING:
            return self._update_fleeing(context, health_ratio)
        
        return self.state
    
    def _update_idle(self, context: Dict, health_ratio: float) -> MonsterState:
        """Update logic for idle state."""
        # Start patrolling
        if random.random() < 0.3:
            self._change_state(MonsterState.PATROLLING)
            return self.state
        
        # Player nearby -> chase or attack
        player_distance = context.get('nearest_player_distance', float('inf'))
        if player_distance <= self.settings.chase_range:
            if random.random() < self.monster.aggression:
                self._change_state(MonsterState.CHASING)
            return self.state
        
        return self.state
    
    def _update_patrolling(self, context: Dict, health_ratio: float) -> MonsterState:
        """Update logic for patrolling state."""
        # Player nearby -> chase
        player_distance = context.get('nearest_player_distance', float('inf'))
        if player_distance <= self.settings.chase_range and random.random() < self.monster.aggression:
            self._change_state(MonsterState.CHASING)
            return self.state
        
        # Too far from home -> return to idle
        distance_from_home = context.get('distance_from_home', 0)
        if distance_from_home > self.settings.patrol_range:
            self._change_state(MonsterState.IDLE)
            return self.state
        
        return self.state
    
    def _update_chasing(self, context: Dict, health_ratio: float) -> MonsterState:
        """Update logic for chasing state."""
        # Low health -> flee
        if health_ratio < self.settings.flee_health_threshold:
            self._change_state(MonsterState.FLEEING)
            return self.state
        
        # Close enough to attack
        player_distance = context.get('nearest_player_distance', float('inf'))
        if player_distance <= 1:
            self._change_state(MonsterState.ATTACKING)
            return self.state
        
        # Lost player -> patrol
        if player_distance > self.settings.chase_range * 1.5:
            self._change_state(MonsterState.PATROLLING)
            return self.state
        
        return self.state
    
    def _update_attacking(self, context: Dict, health_ratio: float) -> MonsterState:
        """Update logic for attacking state."""
        # Low health -> flee
        if health_ratio < self.settings.flee_health_threshold:
            self._change_state(MonsterState.FLEEING)
            return self.state
        
        # Player moved away -> chase
        player_distance = context.get('nearest_player_distance', float('inf'))
        if player_distance > 1:
            self._change_state(MonsterState.CHASING)
            return self.state
        
        return self.state
    
    def _update_fleeing(self, context: Dict, health_ratio: float) -> MonsterState:
        """Update logic for fleeing state."""
        # Health recovered and far from player -> patrol
        player_distance = context.get('nearest_player_distance', float('inf'))
        if health_ratio > 0.5 and player_distance > self.settings.chase_range:
            self._change_state(MonsterState.PATROLLING)
            return self.state
        
        return self.state
    
    def _change_state(self, new_state: MonsterState):
        """Change to a new state."""
        if new_state != self.state:
            self.state = new_state
            self.state_history.append(new_state)
    
    def get_action(self) -> str:
        """
        Get the recommended action for the current state.
        
        Returns:
            str: Recommended action
        """
        actions = {
            MonsterState.IDLE: "idle",
            MonsterState.PATROLLING: "patrol",
            MonsterState.CHASING: "chase",
            MonsterState.ATTACKING: "attack",
            MonsterState.FLEEING: "flee",
            MonsterState.DEAD: "none"
        }
        return actions.get(self.state, "idle")
