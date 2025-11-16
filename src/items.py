"""
Items module for the board game simulator.
Represents various items that players can collect and use.
"""
import csv
import os

from src.dice_roller import DiceRoller
from typing import Tuple


class Item:
    """
    Base class for all items in the game.
    Attributes:
        name (str): Name of the item.
    """
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

class Weapon(Item):
    """
    Represents a weapon item.
    Inherits from Item.

    Attributes:
        hands (int): Number of hands required to wield the weapon (1 or 2).
        order (int): Weapon order identifier.
        charges (int, optional): Maximum number of charges.
        
        dice (int): Dice lever rolled for damage calculation.
        number (int): Number of dice rolled for damage calculation.
        dmg_mod (int): Damage modifier added to the dice roll.
        atk_mod (int): Attack modifier added to attack rolls.

        weapon_attachment (WeaponAttachment): An instance of WeaponAttachment to apply bonuses to rolls.
    """
    def __init__(self, name: str):
        super().__init__(name)
        self._load_stats(name)
        weapon_modifier = None

    def _load_stats(self, name: str, stats_file: str = 'data/weapons.csv'):
        """
        Load weapon stats from a CSV file based on level.
        
        Args:
            level (int): Player level to load stats for.
            stats_file (str): Path to the CSV file containing stats. Defaults to 'data/weapons.csv'.
        """
        if not os.path.exists(stats_file):
            raise FileNotFoundError(f"Stats file {stats_file} not found.")
        
        with open(stats_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['name'] == name:
                    self.hands = int(row['hands'])
                    self.order = int(row['order'])
                    self.charges = int(row['charges']) if row['charges'] else None
                    self.dice = int(row['dice'])
                    self.number = int(row['number'])
                    self.dmg_mod = int(row['dmg_mod'])
                    self.atk_mod = int(row['atk_mod'])
                    break
            else:
                raise ValueError(f"No stats found for weapon {name} in {stats_file}.")
            
    def get_attack(self) -> Tuple[int, int]:
        """
        Calculate the attack roll and damage roll of the weapon.
        
        Returns:
            attack: Attack roll, including modifiers.
            damage: Damage roll, including modifiers.
        """
        attack = DiceRoller(sides=20, modifier=self.atk_mod).roll()
        damage = DiceRoller(sides=self.dice, number=self.number, modifier=self.dmg_mod).roll()

        if self.weapon_modifier is not None:
            attack, damage = self.weapon_modifier(attack, damage)

        return attack, damage
    
class EmptyWeapon(Weapon):
    """
    Represents an empty weapon slot (no weapon equipped).
    Inherits from Weapon.
    """
    def __init__(self):
        super().__init__(name="empty weapon")

class WeaponAttachment(Item):
    """
    Class to handle weapon attachments that can affect attack and damage rolls.
    """
    def __init__(self, name: str):
        super().__init__(name)
        self._load_stats(name)

    def _load_stats(self, name: str, stats_file: str = 'data/weapon_attachments.csv'):
        """
        Load weapon attachment stats from a CSV file.
        
        Args:
            name (str): Name of the weapon attachment.
            stats_file (str): Path to the CSV file containing stats. Defaults to 'data/weapon_attachments.csv'.
        """
        if not os.path.exists(stats_file):
            raise FileNotFoundError(f"Stats file {stats_file} not found.")
        
        with open(stats_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['name'] == name:
                    self.atk_bonus = int(row['atk_bonus'])
                    self.dmg_bonus = int(row['dmg_bonus'])
                    self.dmg_mult = int(row['dmg_mult'])
                    break
            else:
                raise ValueError(f"No stats found for weapon attachment {name} in {stats_file}.")

    def __call__(self, attack: int, damage: int) -> Tuple[int, int]:
        """
        Apply the weapon attachment's bonuses to the attack and damage rolls.
        
        Args:
            attack (int): The original attack roll.
            damage (int): The original damage roll.
        Returns:
            attack (int): Modified attack roll.
            damage (int): Modified damage roll.
        """
        modified_attack = attack + self.atk_bonus
        modified_damage = (damage + self.dmg_bonus) * self.dmg_mult
        return modified_attack, modified_damage
    
class HealingItem(Item):
    """
    Base class for healing items.
    """
    def __init__(self, name: str, healing):
        super().__init__(name)
        self.healing = healing

class Vitamins(HealingItem):
    ...

class ElectronicPowerSupport(HealingItem):
    ...