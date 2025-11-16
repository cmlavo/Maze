"""
Monsters module for the board game simulator.
Represents enemy monsters with various attributes and behaviors.
"""
from typing import Optional, Dict
from enum import Enum


class MonsterType(Enum):
    """Enumeration of monster types."""
    GOBLIN = "goblin"
    ORC = "orc"
    TROLL = "troll"
    DRAGON = "dragon"
    UNDEAD = "undead"
    DEMON = "demon"


class Monster:
    """
    Represents a monster enemy in the board game.
    
    Attributes:
        name (str): Monster's name
        monster_type (MonsterType): Type of monster
        level (int): Monster's level
        health (int): Current health points
        max_health (int): Maximum health points
        attack (int): Attack stat
        defense (int): Defense stat
        speed (int): Speed stat
        aggression (float): Aggression level (0.0-1.0)
        position (tuple): Current position on the board (x, y)
        loot (list): Items dropped when defeated
    """
    
    MONSTER_BASE_STATS = {
        MonsterType.GOBLIN: {'health': 50, 'attack': 8, 'defense': 4, 'speed': 7, 'aggression': 0.6},
        MonsterType.ORC: {'health': 100, 'attack': 12, 'defense': 8, 'speed': 5, 'aggression': 0.8},
        MonsterType.TROLL: {'health': 150, 'attack': 15, 'defense': 12, 'speed': 3, 'aggression': 0.7},
        MonsterType.DRAGON: {'health': 300, 'attack': 25, 'defense': 20, 'speed': 8, 'aggression': 0.9},
        MonsterType.UNDEAD: {'health': 80, 'attack': 10, 'defense': 6, 'speed': 4, 'aggression': 0.5},
        MonsterType.DEMON: {'health': 200, 'attack': 20, 'defense': 15, 'speed': 9, 'aggression': 1.0}
    }
    
    def __init__(self, name: str, monster_type: MonsterType, level: int = 1):
        """
        Initialize a Monster.
        
        Args:
            name (str): Monster's name
            monster_type (MonsterType): Type of monster
            level (int): Monster's level (default 1)
        """
        self.name = name
        self.monster_type = monster_type
        self.level = level
        self.position = (0, 0)
        self.loot = []
        self.status_effects = []
        self.is_boss = False
        
        # Load base stats and scale with level
        base_stats = self.MONSTER_BASE_STATS[monster_type]
        level_multiplier = 1 + (level - 1) * 0.2
        
        self.max_health = int(base_stats['health'] * level_multiplier)
        self.health = self.max_health
        self.attack = int(base_stats['attack'] * level_multiplier)
        self.defense = int(base_stats['defense'] * level_multiplier)
        self.speed = int(base_stats['speed'] * level_multiplier)
        self.aggression = base_stats['aggression']
    
    def take_damage(self, damage: int) -> int:
        """
        Apply damage to the monster, reduced by defense.
        
        Args:
            damage (int): Amount of incoming damage
            
        Returns:
            int: Actual damage taken
        """
        actual_damage = max(1, damage - self.defense // 2)
        self.health = max(0, self.health - actual_damage)
        return actual_damage
    
    def heal(self, amount: int):
        """
        Heal the monster by a specified amount.
        
        Args:
            amount (int): Amount to heal
        """
        self.health = min(self.max_health, self.health + amount)
    
    def is_alive(self) -> bool:
        """
        Check if monster is still alive.
        
        Returns:
            bool: True if health > 0
        """
        return self.health > 0
    
    def move(self, new_position: tuple):
        """
        Move monster to a new position on the board.
        
        Args:
            new_position (tuple): New (x, y) coordinates
        """
        self.position = new_position
    
    def add_loot(self, item):
        """
        Add an item to the monster's loot table.
        
        Args:
            item: Item object to add
        """
        self.loot.append(item)
    
    def get_loot(self) -> list:
        """
        Get the monster's loot when defeated.
        
        Returns:
            list: List of loot items
        """
        return self.loot.copy()
    
    def special_attack(self) -> Dict:
        """
        Perform a special attack based on monster type.
        
        Returns:
            Dict: Special attack details
        """
        special_attacks = {
            MonsterType.GOBLIN: {
                'name': 'Backstab',
                'damage_multiplier': 1.5,
                'effect': 'Ignores half of defense'
            },
            MonsterType.ORC: {
                'name': 'War Cry',
                'damage_multiplier': 1.3,
                'effect': 'Reduces target defense by 20%'
            },
            MonsterType.TROLL: {
                'name': 'Regeneration',
                'damage_multiplier': 1.0,
                'effect': 'Heals 10% of max health'
            },
            MonsterType.DRAGON: {
                'name': 'Fire Breath',
                'damage_multiplier': 2.0,
                'effect': 'Area damage to all adjacent targets'
            },
            MonsterType.UNDEAD: {
                'name': 'Life Drain',
                'damage_multiplier': 1.2,
                'effect': 'Heals for 50% of damage dealt'
            },
            MonsterType.DEMON: {
                'name': 'Dark Pact',
                'damage_multiplier': 1.8,
                'effect': 'Takes 10% recoil damage'
            }
        }
        
        return special_attacks.get(self.monster_type, {
            'name': 'Basic Attack',
            'damage_multiplier': 1.0,
            'effect': 'None'
        })
    
    def set_as_boss(self, boss: bool = True):
        """
        Mark monster as a boss, increasing stats.
        
        Args:
            boss (bool): Whether this is a boss monster
        """
        self.is_boss = boss
        if boss:
            # Boss monsters get stat boost
            self.max_health = int(self.max_health * 2)
            self.health = self.max_health
            self.attack = int(self.attack * 1.5)
            self.defense = int(self.defense * 1.5)
    
    def __str__(self) -> str:
        """String representation of the monster."""
        boss_prefix = "BOSS " if self.is_boss else ""
        return (f"{boss_prefix}{self.name} ({self.monster_type.value.capitalize()} Lv.{self.level}): "
                f"HP {self.health}/{self.max_health}, "
                f"ATK {self.attack}, DEF {self.defense}, SPD {self.speed}")
    
    def __repr__(self) -> str:
        """Detailed representation of the monster."""
        return (f"Monster(name='{self.name}', type={self.monster_type}, level={self.level}, "
                f"health={self.health}/{self.max_health}, position={self.position})")
