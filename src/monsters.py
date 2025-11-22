"""
Monsters module for the board game simulator.
Represents non-player monsters with various attributes and abilities.
"""
import csv
import os
from typing import Tuple
import copy
from abc import ABC, abstractmethod
from src.dice_roller import DiceRoller
from players import Entity

class Monster(Entity):
    """
    Represents a monster in the game.
    Inherits from Entity.

    Attributes:
        name (str): Name of the monster.
        life_points (int): Current life points of the monster.
        ac (int): Armour class of the monster.
        is_alive (bool): Status indicating if the monster is alive.

        _max_life_points (int): Initial life points of the monster.
        _attack_mod (int): Attack modifier for the monster.
        _damage_dice (List[int]): List of dice sides for damage calculation.
        _num_attacks (int): Number of attacks the monster can make per turn.
    """

    def __init__(self, name: str, stats_file: str):
        super().__init__(name)
        self._load_stats(name, stats_file)
        self.life_points = self._max_life_points
        self.is_alive = True

    def _load_stats(self, name: str, stats_file: str):
        """
        Load monster stats from a CSV file.

        Args:
            name (str): Name of the monster to load.
            stats_file (str): Path to the CSV file containing stats.
        """
        if not os.path.exists(stats_file):
            raise FileNotFoundError(f"Stats file {stats_file} not found.")

        with open(stats_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['name'] == name:
                    self._max_life_points = int(row['max_life_points'])
                    self._attack_mod = int(row['attack_mod'])
                    self.ac = int(row['ac'])
                    self._damage_dice = [int(die) for die in row['damage_dice'].strip('[]').split(',')]
                    self._num_attacks = int(row['num_attacks'])
                    assert self._num_attacks == len(self._damage_dice), "Number of attacks must match length of damage dice list."
                    return
        raise ValueError(f"Monster {name} not found in stats file.")
    
    def attempt_hit(self, attack_roll: int, damage_roll: int) -> bool:
        """
        Determine if an incoming attack hits the monster, and if so, apply damage.
        Args:
            attack_roll (int): The attack roll of the incoming attack.
            damage_roll (int): The damage roll of the incoming attack.
        Returns:
            bool: True if the attack hits, False otherwise.
        """
        if attack_roll >= self.ac:
            self.damage(damage_roll)
            return True
        return False  
    
    def damage(self, damage_amount: int) -> int:
        """
        Apply damage to the monster.
        Returns the updated life points.

        Args:
            damage_amount (int): Amount of damage to apply.

        Returns:
            int: Updated life points after damage.
        """
        self.life_points -= damage_amount
        if self.life_points <= 0:
            self.kill()
        return self.life_points
    
    def kill(self):
        self.life_points = 0
        self.is_alive = False

    def attack(self, target: Entity) -> int:
        """
        Attempt to attack an enemy.

        Args:
            target (Entity): The target entity to attack.
        Returns:
            tot_damage (int): The amount of damage dealt to the enemy.
        """
        tot_damage = 0
        for i in range(self._num_attacks):
            attack_roll = DiceRoller(sides=20).roll() + self._attack_mod
            damage_roll = DiceRoller(sides=self._damage_dice[i]).roll()
            if target.attempt_hit(attack_roll, damage_roll): tot_damage += damage_roll

    # Utility methods

    def copy(self):
        """Return a copy of the object."""
        return copy.deepcopy(self)
    
    def __str__(self):
        return f"Monster: {self.name} ({"alive" if self.is_alive else "dead"})"

class Monster1(Monster):
    """
    Represents a specific type of monster: Monster1.
    Inherits from Monster.
    """

    def __init__(self, name: str):
        super().__init__(name, "data/monsters1.csv")

class Monster2(Monster):
    """
    Represents a specific type of monster: Monster2.
    Inherits from Monster.
    """

    def __init__(self, name: str):
        super().__init__(name, "data/monsters2.csv")

class Guardian(Monster):
    """
    Represents a specific type of monster: Guardian.
    Inherits from Monster.
    """

    def __init__(self, name: str):
        super().__init__(name, "data/guardians.csv")