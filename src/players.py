"""
Players module for the board game simulator.
Represents player characters with various attributes and abilities.
"""
import csv
import os
from typing import Tuple
import copy
from abc import ABC, abstractmethod

from src.inventory import Inventory
from src.items import Item, Weapon, HealingItem, Vitamins, ElectronicPowerSupport, EmptyWeapon, Armour
from src.dice_roller import DiceRoller

class Entity(ABC):
    """
    Abstract class for all entities in the game.
    """

    @abstractmethod
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def attempt_hit(self, attack_roll: int, damage_roll: int) -> bool:
        pass

    @abstractmethod
    def damage(self, damage: int) -> bool:
        pass  

    @abstractmethod
    def copy(self):
        pass

    def copy(self):
        """Return a copy of the object."""
        return copy.deepcopy(self)

class Player(Entity):
    """
    Represents a player character in the board game.
    Inherits from PlayerState for state management, and Entity for shared attributes.
    
    Attributes:
        level (int): Current level of the player        
        _stats__file (str): Path to the CSV file containing player stats
        
        _max_life_points (int): Maximum life_points points        
        _base_ac (int): Base armour class stat without modifiers
        _ac_mod (int): Armour class modifier
        _attack_mod (int): Attack modifier
        _damage_mod (int): Damage modifier
        _detection_rate (int): Detection rate stat
        _unarmed_damage (int): Damage when unarmed

        life_points (int): Current life_points points
        ac (int): Current armour class stat
        time_bombs (int): Number of bombs the player has
        position (int): Current position on the board
        on_guard (bool): Whether the player is on guard

        inventory (Inventory): Inventory of items the player carries
        hands (list(Weapon)): List of weapons equipped in hands
        armour (Armour): Armour equipped by the player
    """
    
    def __init__(self, name: str, stats_file: str, level: int = 1, inventory: Inventory = None):
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
        self._stats_file = stats_file
        
        self.inventory = inventory if inventory is not None else Inventory()        
        self.hands = [None, None]
        self.armour = None        

        self._load_stats()
        self.update_ac()
        self.life_points = self._max_life_points
        self.position = 0
        self.time_bombs = 0
        self.on_guard = False

    def _load_stats(self):
        """
        Load player stats from a CSV file based on level.
        
        Args:
            level (int): Player level to load stats for.
            _stats_file (str): Path to the CSV file containing stats.
        """
        if not os.path.exists(self._stats_file):
            raise FileNotFoundError(f"Stats file {self._stats_file} not found.")
        
        with open(self._stats_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if int(row['level']) == self.level:
                    self._max_life_points = int(row['max_life_points'])
                    self._base_ac = int(row['base_ac'])
                    self.ac_mod = int(row['ac_mod'])
                    self._attack_mod = int(row['attack_mod'])
                    self._damage_mod = int(row['damage_mod'])
                    self._detection_rate = int(row['detection_rate'])
                    self._unarmed_damage = int(row['unarmed_damage'])
                    break
            else:
                raise ValueError(f"No stats found for level {self.level} in {self.stats_file}.")

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
            if weapon._hands == 2:  # if two-handed weapon, unequip both hands
                other_hand = (hand_slot + 1) % 2
                self.hands[other_hand] = None
            self.hands[hand_slot] = None
            self.inventory.add_item(weapon)
        return weapon

    def equip_armour(self, armour: Armour = None) -> bool:
        """
        Equip armour from inventory. If no armour is specified, equip the first available armour from inventory.
        Args:
            armour (Armour): Armour to equip (default None)
        Returns:
            bool: True if armour was equipped, False otherwise.
        """
        if armour is not None:
            if armour not in self.inventory.items:
                return False
            else:
                self.unequip_armour()
                self.armour = armour
                self.inventory.remove_item(armour)
                self.update_ac()
                return True
            
        else: # no armour specified - equip first available armour from inventory
            for item in self.inventory.items:
                if isinstance(item, Armour):
                    self.unequip_armour()
                    self.armour = item
                    self.inventory.remove_item(item)
                    self.update_ac()
                    return True
                    break
            return False
    
    def unequip_armour(self) -> Armour:
        """
        Unequip currently equipped armour and return it to inventory.

        Returns:
            Armour: The unequipped armour, or None if no armour was equipped.
        """
        if self.armour is None:
            return None
        else:
            unequipped_armour = self.armour
            self.armour = None
            self.inventory.add_item(unequipped_armour)
            self.update_ac()
            return unequipped_armour

    def update_ac(self) -> int:
        """
        Update the player's armour class based on equipped armour and modifiers.
        Returns:
            int: The updated armour class.
        """        
        if self.armour is not None:
            self.ac = self.armour.ac + self.armour.ac_mod + self.ac_mod
        else:
            self.ac = self._base_ac + self.ac_mod

        return self.ac

    def attack(self, target: Entity) -> Tuple[int, bool]:
        """
        Attempt to attack an enemy.

        Args:
            target (Entity): The target entity to attack.
        Returns:
            tot_damage (int): The amount of damage dealt to the enemy.
            killed (bool): True if the target was killed, False otherwise.
        """
        tot_damage = 0
        if all(hand is None for hand in self.hands): # unarmed attack
            attack_roll = DiceRoller(sides=20, modifier=self._attack_mod).roll()
            damage_roll = self._unarmed_damage
            hit, kill = target.attempt_hit(attack_roll, damage_roll)
            if hit: tot_damage += damage_roll
            return tot_damage, kill
        
        else: # armed attack
            for weapon in self.hands: # attack with each weapon available
                if weapon is not None and not isinstance(weapon, EmptyWeapon): # all bonuses applied from weapons first, then from player
                    attack_roll, damage_roll = weapon.get_attack()
                    attack_roll += self._attack_mod
                    damage_roll += self._damage_mod
                    hit, kill = target.attempt_hit(attack_roll, damage_roll)
                    if hit: tot_damage += damage_roll
                    if kill: 
                        return tot_damage, kill
            return tot_damage, kill

    def attempt_hit(self, attack_roll: int, damage_roll: int) -> bool:
        """
        Determine if an incoming attack hits the player, and if so, apply damage.
        Args:
            attack_roll (int): The attack roll of the incoming attack.
            damage_roll (int): The damage roll of the incoming attack.
        Returns:
            hit (bool): True if the attack hits, False otherwise.
            kill (bool): True if the player was killed, False otherwise.
        """
        hit, kill = False, False
        if attack_roll >= self.ac:
            hit = True
            if self.damage(damage_roll): kill = True
        return hit, kill

    def give_item(self, item: Item) -> bool:
        """
        Give an item to another player.

        Args:
            item (Item): The item to give.
        Returns:
            bool: True if the item was given, False otherwise.
        """
        self.inventory.add_item(item)
        return True

    def set_inventory(self, inventory: Inventory):
        """
        Set the player's inventory.

        Args:
            inventory (Inventory): The new inventory to set.
        """
        self.inventory = inventory

    def heal(self, amount: int):
        """
        Heal the player by a specified amount, not exceeding max life points.R
        Returns the new life points.

        Args:
            amount (int): Amount to heal.
        """
        self.life_points = min(self.max_life_points, self.life_points + amount)
        return self.life_points
    
    def damage(self, amount: int) -> int:
        """
        Damage the player by a specified amount, not going below zero life points.
        Returns the new life points.

        Args:
            amount (int): Amount of damage to apply.
        Returns:
            bool: True if the player was killed, False otherwise.
        """
        self.life_points = self.life_points - amount
        if self.life_points <= 0:
            self.life_points = 0
            self.kill()
            return True
        return False

    def kill(self):
        """
        When a player dies, they lose all items in inventory and unequips all weapons. 
        They lose 1d4 levels, return to max hit points, and go back to start position.
        """        
        self.reset_equipment()
        self.level = max(1, self.level - DiceRoller(sides=4).roll())
        self._load_stats()
        self.position = 0
        self.life_points = self._max_life_points

    def reset_equipment(self):
        """
        Clears the player's inventory, gives them the starting weapon and armour, and equips them.
        """
        for idx, hand in enumerate(self.hands): self.unequip_weapon(idx)
        starting_inventory = Inventory([Weapon('shotgun'), Armour('metal jacket')])
        self.set_inventory(starting_inventory)        
        self.equip_weapon()
        self.equip_armour()

    def roll_detection(self) -> bool:
        """
        Roll a detection check against the player's detection rate.
        Returns:
            bool: True if detection is successful, False otherwise.
        """
        roll = DiceRoller(sides=20).roll()
        return roll <= self._detection_rate

    def time_bomb_check(self) -> bool:
        """
        Roll a check to see if the time bomb hurts the player, take damage if so.
        Returns:
            bool: True if the player is hurt by the time bomb, False otherwise.
        """

        if not self.roll_detection():
            self.damage(DiceRoller(sides=6, number=2).roll())
            return True
        return False

    # Utility methods
    def __str__(self) -> str:
        """String representation of the player."""
        return f"Player: {self.name} (lvl. {self.level})"

    def copy(self):
        """Return a copy of the object."""
        return copy.deepcopy(self)

    # Abstract methods
    @abstractmethod
    def equip_weapon(self, weapon: Weapon = None, override: int = None) -> bool:
        pass

    @abstractmethod
    def consume_healing_item(self, healing_item: HealingItem) -> bool:
        pass    

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

    def __str__(self) -> str:
        """String representation of the monster."""
        return f"Player: {self.name} (Lvl. {self.level} Monster)"

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
                            
        if weapon._hands == 2: # if a weapon is two-handed, both hands must be free or overridden
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

        elif weapon._hands == 1: # if a weapon is one-handed
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

    def __str__(self) -> str:
        """String representation of the humanoid."""
        return f"Player: {self.name} (Lvl. {self.level} Humanoid)"

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
                            
        if weapon._hands == 2: # if a weapon is two-handed, both hands must be free or overridden
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

        elif weapon._hands == 1: # if a weapon is one-handed
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

    def __str__(self) -> str:
        """String representation of the cyborg."""
        return f"Player: {self.name} (Lvl. {self.level} Cyborg)"

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
                            
        if weapon._hands == 2: # if a weapon is two-handed, both hands must be free or overridden
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

        elif weapon._hands == 1: # if a weapon is one-handed
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

    def __str__(self) -> str:
        """String representation of the wartech."""
        return f"Player: {self.name} (Lvl. {self.level} Wartech)"