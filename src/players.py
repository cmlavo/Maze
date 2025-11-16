"""
Players module for the board game simulator.
Represents player characters with various attributes and abilities.
"""
import csv
import os
from typing import Tuple
import copy

from src.inventory import Inventory
from src.items import Item, Weapon, HealingItem, Vitamins, ElectronicPowerSupport, EmptyWeapon
from src.dice_roller import DiceRoller

class Entity:
    """
    Base class for all entities in the game.
    Attributes:
        name (str): Name of the entity.
    """
    def __init__(self, name: str):
        self.name = name    

class Player(Entity):
    """
    Represents a player character in the board game.
    Inherits from PlayerState for state management, and Entity for shared attributes.
    
    Attributes:
        level (int): Current level of the player
        inventory (Inventory): Inventory of items the player carries
        position (int): Current position on the board

        life_points (int): Current life_points points
        max_life_points (int): Maximum life_points points
        ac (int): Armour class stat
        damage (int): Damage stat
        attack (int): Attack stat
        detection_rate (int): Detection rate stat
        time_bombs (int): Number of bombs the player has
        unarmed_damage (int): Damage when unarmed

        hands (list(Weapon)): List of weapons equipped in hands
    """
    
    def __init__(self, name: str, stat_file: str, level: int = 1, inventory: Inventory = None):
        """
        Initialize a Player with stats from CSV file.
        
        Args:
            name (str): Player's name
            stats_file (str): Path to CSV file with player stats
            level (int): Starting level (default 1)
            inventory (Inventory): Inventory of items the player starts with
        """
        super().__init__(name)
        self.level = level
        self.position = 0
        self.inventory = inventory if inventory is not None else Inventory()
        self.time_bombs = 0
        self.hands = [None, None]
        self._load_stats(level, stat_file)

    def _load_stats(self, level: int, stats_file: str):
        """
        Load player stats from a CSV file based on level.
        
        Args:
            level (int): Player level to load stats for.
            stats_file (str): Path to the CSV file containing stats.
        """
        if not os.path.exists(stats_file):
            raise FileNotFoundError(f"Stats file {stats_file} not found.")
        
        with open(stats_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if int(row['level']) == level:
                    self.max_life_points = int(row['life_points'])
                    self.life_points = self.max_life_points
                    self.ac = int(row['ac'])
                    self.attack = int(row['attack'])
                    self.damage = int(row['damage'])
                    self.detection_rate = int(row['detection_rate'])
                    self.unarmed_damage = int(row['unarmed_damage'])
                    break
            else:
                raise ValueError(f"No stats found for level {level} in {stats_file}.")

    def copy(self):
        """Return a copy of the player."""
        return copy.deepcopy(self)

    def unequip_weapon(self, hand_slot: int) -> Weapon:
        """
        Unequip weapon from specified hand and return it to inventory.

        Args:
            hand_slot (int): Weapon slot to unequip from.
        Returns:
            Weapon: The unequipped weapon, or None if no weapon was equipped.
        """
        assert hand_slot in [0, 1], "Weapon slot must be 0 or 1"
        weapon = self.hands[hand_slot]
        if weapon is None:
            return None
        else:
            if weapon.hands == 2:  # if two-handed weapon, unequip both hands
                other_hand = (hand_slot + 1) % 2
                self.hands[other_hand] = None
            self.hands[hand_slot] = None
            self.inventory.add_item(weapon)
        return weapon

    def attack(self, target: Entity) -> bool:
        """
        Attempt to attack an enemy.

        Args:
            target (Entity): The target entity to attack.
        Returns:
            bool: True if attack hits, False otherwise.
        """
        ...

    def give(self, item: Item) -> bool:
        """
        Give an item to another player.

        Args:
            item (Item): The item to give.
        Returns:
            bool: True if the item was given, False otherwise.
        """
        self.inventory.add_item(item)
        return True

class Monster(Player):
    """
    Represents a monster character in the board game.
    Inherits from Player for shared attributes and methods.
    """
    
    def __init__(self, name: str, level: int = 1, inventory: Inventory = None, stats_override: str = "data/monster.csv"):
        """
        Initialize a Monster with stats from CSV file.
        
        Args:
            name (str): Monster's name
            level (int): Starting level (default 1)
            inventory (Inventory): Inventory of items the monster carries
            stats_override (str): Path to CSV file with monster stats (default "data/monster.csv")
        """

        super().__init__(name, stats_override, level, inventory)

    def equip_weapon(self, weapon: Weapon = None, override: int = None) -> bool:
        """
        Monsters can equip any weapon in any hand.
        If no weapon is specified, equip the first available weapon from inventory.
        If no override is specified, equip in the first free hand, or do not equip if both hands are full.
        Args:
            weapon (Weapon): Weapon to equip (default None)
            override (str): 0 or 1 to override existing weapon slot (default None)
        Returns:
            bool: True if a weapon was equipped, False otherwise.
        """
        hand_attr = None
        if override is not None: # get hand_attr, the index of the hand to override
            assert override in [0, 1], "Override must be 0 or 1"
            hand_attr = override
            
        else: # get hand_attr, the index of the free hand, if none is overriden
            for hand in self.hands:
                if hand is None:
                    hand_attr = self.hands.index(hand)
                    break
            if hand_attr is None: # no free hand
                return False
        
        if weapon is None: # no weapon specified - equip first available weapon from inventory
            weapon = self.inventory.get_first_weapon()
            if weapon is None: # no weapon found in inventory
                return False
            
        if weapon is not None and weapon not in self.inventory.items: # specified weapon but not in inventory
            return False
            
        # if all checks pass, equip the weapon in the specified hand
        self.hands[hand_attr] = weapon
        self.inventory.remove_item(weapon)

        return True

    def consume_healing_item(self, healing_item: HealingItem) -> bool:
        """
        Monsters can consume any healing item from their inventory.        
        Args:
            healing_item (HealingItem): Healing item to consume.
        Returns:
            bool: True if the item was consumed, False otherwise.
        """
        if healing_item not in self.inventory.items:
            return False
        
        self.heal(healing_item.get_healing())
        self.inventory.remove_item(healing_item)
        return True

class Humanoid(Player):
    """
    Represents a humanoid character in the board game.
    Inherits from Player for shared attributes and methods.
    """
    
    def __init__(self, name: str, level: int = 1, inventory: Inventory = None, stats_override: str = "data/humanoid.csv"):
        """
        Initialize a Humanoid with stats from CSV file.
        
        Args:
            name (str): Human's name
            level (int): Starting level (default 1)
            inventory (Inventory): Inventory of items the humanoid carries
            stats_override (str): Path to CSV file with humanoid stats (default "data/humanoid.csv")
        """

        super().__init__(name, stats_override, level, inventory)

    def equip_weapon(self, weapon: Weapon = None, override: int = None) -> bool:
        """
        Humanoids can equip one one-handed weapon per hand if one has lower class than the other, or one two-handed weapon.
        If no weapon is specified, equip the first available weapon from inventory.
        If no override is specified, equip in the first free hand, or do not equip if both hands are full.
        Args:
            weapon (Weapon): Weapon to equip (default None)
            override (str): 0 or 1 to override existing weapon slot (default None)
        Returns:
            bool: True if a weapon was equipped, False otherwise.
        """
        hand_attr = None
        if override is not None: # get hand_attr, the index of the hand to override
            assert override in [0, 1], "Override must be 0 or 1"
            hand_attr = override

        # get weapon to be equipped
        if weapon is None: # no weapon specified - equip first available weapon from inventory
            weapon = self.inventory.get_first_weapon()
            if weapon is None: # no weapon found in inventory
                return False
            
        if weapon is not None and weapon not in self.inventory.items: # specified weapon but not in inventory
            return False
                            
        if weapon.hands == 2: # if a weapon is two-handed, both hands must be free or overridden
            if hand_attr is not None: # overriding a hand; both hands must be overridden
                # unequip both hands
                self.unequip_weapon(hand_attr)
                other_hand = (hand_attr + 1) % 2
                if self.hands[other_hand] is not None:
                    self.unequip_weapon(other_hand)

                # equip two-handed weapon: first hand is the weapon, second hand is EmptyWeapon
                self.hands[hand_attr] = weapon
                self.hands[other_hand] = EmptyWeapon()
                self.inventory.remove_item(weapon)

            else: # no override; both hands must be free
                if not all(hand is None for hand in self.hands):
                    return False
                
                # equip two-handed weapon: first hand is the weapon, second hand is EmptyWeapon
                self.hands[0] = weapon
                self.hands[1] = EmptyWeapon()
                self.inventory.remove_item(weapon)

        elif weapon.hands == 1: # if a weapon is one-handed
            if hand_attr is not None: # overriding a hand
                # check if weapon orders are equal between hands
                other_hand = (hand_attr + 1) % 2
                if self.hands[other_hand] is not None:
                    if weapon.order == self.hands[other_hand].order:
                        return False
                
                # unequip the specified hand
                self.unequip_weapon(hand_attr)
                
                # equip the one-handed weapon
                self.hands[hand_attr] = weapon
                self.inventory.remove_item(weapon)
                
            else: # no override; equip in first free hand                
                for hand in self.hands:
                    if hand is None:
                        hand_attr = self.hands.index(hand)
                        break
                if hand_attr is None: # no free hand
                    return False
                # check if weapon orders are equal between hands
                other_hand = (hand_attr + 1) % 2
                if self.hands[other_hand] is not None:
                    if weapon.order == self.hands[other_hand].order:
                        return False
                # equip the one-handed weapon
                self.hands[hand_attr] = weapon
                self.inventory.remove_item(weapon)

        return True

    def consume_healing_item(self, healing_item: HealingItem) -> bool:
        """
        Humanoids can only consume vitamins.
        Args:
            healing_item (HealingItem): Healing item to consume.
        Returns:
            bool: True if the item was consumed, False otherwise.
        """
        if healing_item not in self.inventory.items:
            return False
        
        if not isinstance(healing_item, Vitamins):
            return False
        
        self.heal(healing_item.get_healing())
        self.inventory.remove_item(healing_item)
        return True

class Cyborg(Player):
    """
    Represents a cyborg character in the board game.
    Inherits from Player for shared attributes and methods.
    """
    
    def __init__(self, name: str, level: int = 1, inventory: Inventory = None, stats_override: str = "data/cyborg.csv"):
        """
        Initialize a Cyborg with stats from CSV file.
        
        Args:
            name (str): Cyborg's name
            level (int): Starting level (default 1)
            inventory (Inventory): Inventory of items the humanoid carries
            stats_override (str): Path to CSV file with cyborg stats (default "data/cyborg.csv")
        """

        super().__init__(name, stats_override, level, inventory)

    def equip_weapon(self, weapon: Weapon = None, override: int = None) -> bool:
        """
        Cyborgs can equip one one-handed weapon per hand if one has lower class than the other, or one two-handed weapon.
        If no weapon is specified, equip the first available weapon from inventory.
        If no override is specified, equip in the first free hand, or do not equip if both hands are full.
        Args:
            weapon (Weapon): Weapon to equip (default None)
            override (str): 0 or 1 to override existing weapon slot (default None)
        Returns:
            bool: True if a weapon was equipped, False otherwise.
        """
        hand_attr = None
        if override is not None: # get hand_attr, the index of the hand to override
            assert override in [0, 1], "Override must be 0 or 1"
            hand_attr = override

        # get weapon to be equipped
        if weapon is None: # no weapon specified - equip first available weapon from inventory
            weapon = self.inventory.get_first_weapon()
            if weapon is None: # no weapon found in inventory
                return False
            
        if weapon is not None and weapon not in self.inventory.items: # specified weapon but not in inventory
            return False
                            
        if weapon.hands == 2: # if a weapon is two-handed, both hands must be free or overridden
            if hand_attr is not None: # overriding a hand; both hands must be overridden
                # unequip both hands
                self.unequip_weapon(hand_attr)
                other_hand = (hand_attr + 1) % 2
                if self.hands[other_hand] is not None:
                    self.unequip_weapon(other_hand)

                # equip two-handed weapon: first hand is the weapon, second hand is EmptyWeapon
                self.hands[hand_attr] = weapon
                self.hands[other_hand] = EmptyWeapon()
                self.inventory.remove_item(weapon)

            else: # no override; both hands must be free
                if not all(hand is None for hand in self.hands):
                    return False
                
                # equip two-handed weapon: first hand is the weapon, second hand is EmptyWeapon
                self.hands[0] = weapon
                self.hands[1] = EmptyWeapon()
                self.inventory.remove_item(weapon)

        elif weapon.hands == 1: # if a weapon is one-handed
            if hand_attr is not None: # overriding a hand
                # check if weapon orders are equal between hands
                other_hand = (hand_attr + 1) % 2
                if self.hands[other_hand] is not None:
                    if weapon.order == self.hands[other_hand].order:
                        return False
                
                # unequip the specified hand
                self.unequip_weapon(hand_attr)
                
                # equip the one-handed weapon
                self.hands[hand_attr] = weapon
                self.inventory.remove_item(weapon)
                
            else: # no override; equip in first free hand                
                for hand in self.hands:
                    if hand is None:
                        hand_attr = self.hands.index(hand)
                        break
                if hand_attr is None: # no free hand
                    return False
                # check if weapon orders are equal between hands
                other_hand = (hand_attr + 1) % 2
                if self.hands[other_hand] is not None:
                    if weapon.order == self.hands[other_hand].order:
                        return False
                # equip the one-handed weapon
                self.hands[hand_attr] = weapon
                self.inventory.remove_item(weapon)

        return True

    def consume_healing_item(self, healing_item: HealingItem) -> bool:
        """
        Cyborgs can consume any healing item from their inventory.        
        Args:
            healing_item (HealingItem): Healing item to consume.
        Returns:
            bool: True if the item was consumed, False otherwise.
        """
        if healing_item not in self.inventory.items:
            return False
        
        self.heal(healing_item.get_healing())
        self.inventory.remove_item(healing_item)
        return True

class Wartech(Player):
    """
    Represents a wartech character in the board game.
    Inherits from Player for shared attributes and methods.
    """
    
    def __init__(self, name: str, level: int = 1, inventory: Inventory = None, stats_override: str = "data/wartech.csv"):
        """
        Initialize a Wartech with stats from CSV file.
        
        Args:
            name (str): Wartech's name
            level (int): Starting level (default 1)
            inventory (Inventory): Inventory of items the humanoid carries
            stats_override (str): Path to CSV file with wartech stats (default "data/wartech.csv")
        """

        super().__init__(name, stats_override, level, inventory)

    def equip_weapon(self, weapon: Weapon = None, override: int = None) -> bool:
        """
        Wartechs can equip one one-handed weapon per hand even if they have the same class, or one two-handed weapon.
        If no weapon is specified, equip the first available weapon from inventory.
        If no override is specified, equip in the first free hand, or do not equip if both hands are full.
        Args:
            weapon (Weapon): Weapon to equip (default None)
            override (str): 0 or 1 to override existing weapon slot (default None)
        Returns:
            bool: True if a weapon was equipped, False otherwise.
        """
        hand_attr = None
        if override is not None: # get hand_attr, the index of the hand to override
            assert override in [0, 1], "Override must be 0 or 1"
            hand_attr = override

        # get weapon to be equipped
        if weapon is None: # no weapon specified - equip first available weapon from inventory
            weapon = self.inventory.get_first_weapon()
            if weapon is None: # no weapon found in inventory
                return False
            
        if weapon is not None and weapon not in self.inventory.items: # specified weapon but not in inventory
            return False
                            
        if weapon.hands == 2: # if a weapon is two-handed, both hands must be free or overridden
            if hand_attr is not None: # overriding a hand; both hands must be overridden
                # unequip both hands
                self.unequip_weapon(hand_attr)
                other_hand = (hand_attr + 1) % 2
                if self.hands[other_hand] is not None:
                    self.unequip_weapon(other_hand)

                # equip two-handed weapon: first hand is the weapon, second hand is EmptyWeapon
                self.hands[hand_attr] = weapon
                self.hands[other_hand] = EmptyWeapon()
                self.inventory.remove_item(weapon)

            else: # no override; both hands must be free
                if not all(hand is None for hand in self.hands):
                    return False
                
                # equip two-handed weapon: first hand is the weapon, second hand is EmptyWeapon
                self.hands[0] = weapon
                self.hands[1] = EmptyWeapon()
                self.inventory.remove_item(weapon)

        elif weapon.hands == 1: # if a weapon is one-handed
            if hand_attr is not None: # overriding a hand
                
                # unequip the specified hand
                self.unequip_weapon(hand_attr)
                
                # equip the one-handed weapon
                self.hands[hand_attr] = weapon
                self.inventory.remove_item(weapon)
                
            else: # no override; equip in first free hand                
                for hand in self.hands:
                    if hand is None:
                        hand_attr = self.hands.index(hand)
                        break
                if hand_attr is None: # no free hand
                    return False
                
                # equip the one-handed weapon
                self.hands[hand_attr] = weapon
                self.inventory.remove_item(weapon)

        return True

    def consume_healing_item(self, healing_item: HealingItem) -> bool:
        """
        Wartechs can only consume Electronic Power Supports.
        Args:
            healing_item (HealingItem): Healing item to consume.
        Returns:
            bool: True if the item was consumed, False otherwise.
        """
        if healing_item not in self.inventory.items:
            return False
        
        if not isinstance(healing_item, ElectronicPowerSupport):
            return False
        
        self.heal(healing_item.get_healing())
        self.inventory.remove_item(healing_item)
        return True
