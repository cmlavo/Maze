"""
Players module for the board game simulator.
Represents player characters with various attributes and abilities.
"""
import csv
import os
from typing import Dict, Optional


class Player:
    """
    Represents a player character in the board game.
    
    Attributes:
        name (str): Player's name
        player_type (str): Type of player (human, monster, cyborg, wartech)
        level (int): Current level of the player
        health (int): Current health points
        max_health (int): Maximum health points
        attack (int): Attack stat
        defense (int): Defense stat
        speed (int): Speed stat
        special_ability (str): Name of special ability
        position (tuple): Current position on the board (x, y)
        inventory (list): List of items the player carries
    """
    
    def __init__(self, name: str, player_type: str, level: int = 1, stats_file: str = None):
        """
        Initialize a Player with stats from CSV file.
        
        Args:
            name (str): Player's name
            player_type (str): Type of player (human, monster, cyborg, wartech)
            level (int): Starting level (default 1)
            stats_file (str): Path to CSV file with player stats
        """
        self.name = name
        self.player_type = player_type.lower()
        self.level = level
        self.position = (0, 0)
        self.inventory = []
        self.status_effects = []
        
        # Load stats from CSV file
        if stats_file is None:
            # Default to data/player_stats.csv
            current_dir = os.path.dirname(os.path.abspath(__file__))
            stats_file = os.path.join(os.path.dirname(current_dir), 'data', 'player_stats.csv')
        
        self._load_stats(stats_file)
    
    def _load_stats(self, stats_file: str):
        """Load player stats from CSV file based on type and level."""
        try:
            with open(stats_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['player_type'].lower() == self.player_type and int(row['level']) == self.level:
                        self.max_health = int(row['health'])
                        self.health = self.max_health
                        self.attack = int(row['attack'])
                        self.defense = int(row['defense'])
                        self.speed = int(row['speed'])
                        self.special_ability = row['special_ability']
                        return
                
                # If exact level not found, use level 1 stats
                raise ValueError(f"Stats not found for {self.player_type} level {self.level}")
        except FileNotFoundError:
            # Default stats if file not found
            self._set_default_stats()
    
    def _set_default_stats(self):
        """Set default stats if CSV file is not available."""
        base_stats = {
            'human': {'health': 100, 'attack': 10, 'defense': 8, 'speed': 6, 'ability': 'tactical_insight'},
            'monster': {'health': 150, 'attack': 15, 'defense': 5, 'speed': 8, 'ability': 'berserker_rage'},
            'cyborg': {'health': 110, 'attack': 12, 'defense': 10, 'speed': 7, 'ability': 'tech_enhancement'},
            'wartech': {'health': 120, 'attack': 13, 'defense': 12, 'speed': 5, 'ability': 'heavy_artillery'}
        }
        
        stats = base_stats.get(self.player_type, base_stats['human'])
        self.max_health = stats['health']
        self.health = self.max_health
        self.attack = stats['attack']
        self.defense = stats['defense']
        self.speed = stats['speed']
        self.special_ability = stats['ability']
    
    def take_damage(self, damage: int) -> int:
        """
        Apply damage to the player, reduced by defense.
        
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
        Heal the player by a specified amount.
        
        Args:
            amount (int): Amount to heal
        """
        self.health = min(self.max_health, self.health + amount)
    
    def is_alive(self) -> bool:
        """
        Check if player is still alive.
        
        Returns:
            bool: True if health > 0
        """
        return self.health > 0
    
    def move(self, new_position: tuple):
        """
        Move player to a new position on the board.
        
        Args:
            new_position (tuple): New (x, y) coordinates
        """
        self.position = new_position
    
    def add_item(self, item):
        """
        Add an item to the player's inventory.
        
        Args:
            item: Item object to add
        """
        self.inventory.append(item)
    
    def remove_item(self, item):
        """
        Remove an item from the player's inventory.
        
        Args:
            item: Item object to remove
        """
        if item in self.inventory:
            self.inventory.remove(item)
    
    def use_special_ability(self, target=None) -> Dict:
        """
        Use the player's special ability.
        
        Args:
            target: Target of the ability (if applicable)
            
        Returns:
            Dict: Result of ability use
        """
        result = {
            'ability': self.special_ability,
            'success': True,
            'effect': None
        }
        
        if self.special_ability == 'tactical_insight':
            result['effect'] = 'Next attack has +5 bonus'
        elif self.special_ability == 'berserker_rage':
            result['effect'] = 'Attack doubled, defense halved for 1 turn'
        elif self.special_ability == 'tech_enhancement':
            result['effect'] = 'All stats +2 for 2 turns'
        elif self.special_ability == 'heavy_artillery':
            result['effect'] = 'Area attack, hits all adjacent enemies'
        
        return result
    
    def level_up(self):
        """Increase player level and improve stats."""
        self.level += 1
        # Basic stat increases
        self.max_health += 20
        self.health = self.max_health
        self.attack += 3
        self.defense += 2
        self.speed += 1
    
    def __str__(self) -> str:
        """String representation of the player."""
        return (f"{self.name} ({self.player_type.capitalize()} Lv.{self.level}): "
                f"HP {self.health}/{self.max_health}, "
                f"ATK {self.attack}, DEF {self.defense}, SPD {self.speed}")
    
    def __repr__(self) -> str:
        """Detailed representation of the player."""
        return (f"Player(name='{self.name}', type='{self.player_type}', level={self.level}, "
                f"health={self.health}/{self.max_health}, position={self.position})")
