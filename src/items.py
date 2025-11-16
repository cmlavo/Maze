"""
Items module for the board game simulator.
Represents various items that players can collect and use.
"""
from enum import Enum
from typing import Optional, Dict


class ItemType(Enum):
    """Enumeration of item types."""
    WEAPON = "weapon"
    ARMOR = "armor"
    POTION = "potion"
    CONSUMABLE = "consumable"
    TREASURE = "treasure"
    KEY = "key"
    ARTIFACT = "artifact"


class ItemRarity(Enum):
    """Enumeration of item rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class Item:
    """
    Represents an item in the board game.
    
    Attributes:
        name (str): Item's name
        item_type (ItemType): Type of item
        rarity (ItemRarity): Rarity level
        value (int): Gold value of the item
        weight (float): Weight of the item
        durability (int): Current durability (if applicable)
        max_durability (int): Maximum durability
        effects (dict): Dictionary of stat effects
        description (str): Item description
        stackable (bool): Whether item can be stacked
        quantity (int): Number of items in stack
    """
    
    def __init__(self, 
                 name: str, 
                 item_type: ItemType, 
                 rarity: ItemRarity = ItemRarity.COMMON,
                 value: int = 10,
                 effects: dict = None,
                 description: str = "",
                 stackable: bool = False,
                 durability: Optional[int] = None):
        """
        Initialize an Item.
        
        Args:
            name (str): Item's name
            item_type (ItemType): Type of item
            rarity (ItemRarity): Rarity level
            value (int): Gold value
            effects (dict): Dictionary of stat effects
            description (str): Item description
            stackable (bool): Whether item can be stacked
            durability (int, optional): Item durability (for weapons/armor)
        """
        self.name = name
        self.item_type = item_type
        self.rarity = rarity
        self.value = value
        self.weight = self._calculate_weight()
        self.effects = effects or {}
        self.description = description
        self.stackable = stackable
        self.quantity = 1
        
        # Durability for weapons and armor
        if durability is not None:
            self.max_durability = durability
            self.durability = durability
        else:
            self.max_durability = None
            self.durability = None
    
    def _calculate_weight(self) -> float:
        """Calculate item weight based on type and rarity."""
        base_weights = {
            ItemType.WEAPON: 5.0,
            ItemType.ARMOR: 10.0,
            ItemType.POTION: 0.5,
            ItemType.CONSUMABLE: 0.5,
            ItemType.TREASURE: 1.0,
            ItemType.KEY: 0.2,
            ItemType.ARTIFACT: 2.0
        }
        
        rarity_multipliers = {
            ItemRarity.COMMON: 1.0,
            ItemRarity.UNCOMMON: 1.1,
            ItemRarity.RARE: 1.2,
            ItemRarity.EPIC: 1.3,
            ItemRarity.LEGENDARY: 1.5
        }
        
        return base_weights[self.item_type] * rarity_multipliers[self.rarity]
    
    def use(self, target=None) -> Dict:
        """
        Use the item on a target.
        
        Args:
            target: Target entity (player or monster)
            
        Returns:
            Dict: Result of item use
        """
        result = {
            'success': False,
            'message': '',
            'effects_applied': {}
        }
        
        if self.item_type == ItemType.POTION:
            if target and hasattr(target, 'heal'):
                heal_amount = self.effects.get('heal', 0)
                target.heal(heal_amount)
                result['success'] = True
                result['message'] = f"Healed {heal_amount} HP"
                result['effects_applied'] = {'heal': heal_amount}
                if self.stackable and self.quantity > 1:
                    self.quantity -= 1
                    
        elif self.item_type == ItemType.CONSUMABLE:
            if target:
                result['success'] = True
                result['message'] = f"Applied effects: {self.effects}"
                result['effects_applied'] = self.effects.copy()
                if self.stackable and self.quantity > 1:
                    self.quantity -= 1
                    
        elif self.item_type in [ItemType.WEAPON, ItemType.ARMOR]:
            result['success'] = True
            result['message'] = f"Equipped {self.name}"
            result['effects_applied'] = self.effects.copy()
            
        else:
            result['message'] = f"{self.name} cannot be used directly"
        
        return result
    
    def repair(self, amount: int):
        """
        Repair the item's durability.
        
        Args:
            amount (int): Amount to repair
        """
        if self.durability is not None:
            self.durability = min(self.max_durability, self.durability + amount)
    
    def take_damage(self, amount: int = 1) -> bool:
        """
        Reduce item durability.
        
        Args:
            amount (int): Amount of durability to lose
            
        Returns:
            bool: True if item is still usable, False if broken
        """
        if self.durability is not None:
            self.durability = max(0, self.durability - amount)
            return self.durability > 0
        return True
    
    def is_broken(self) -> bool:
        """
        Check if item is broken.
        
        Returns:
            bool: True if item has 0 durability
        """
        if self.durability is not None:
            return self.durability <= 0
        return False
    
    def stack(self, quantity: int = 1):
        """
        Add to item stack.
        
        Args:
            quantity (int): Number of items to add
        """
        if self.stackable:
            self.quantity += quantity
    
    def unstack(self, quantity: int = 1) -> bool:
        """
        Remove from item stack.
        
        Args:
            quantity (int): Number of items to remove
            
        Returns:
            bool: True if successful, False if not enough items
        """
        if self.stackable and self.quantity >= quantity:
            self.quantity -= quantity
            return True
        return False
    
    def get_stat_bonuses(self) -> Dict:
        """
        Get stat bonuses provided by this item.
        
        Returns:
            Dict: Dictionary of stat bonuses
        """
        return self.effects.copy()
    
    def __str__(self) -> str:
        """String representation of the item."""
        qty_str = f" x{self.quantity}" if self.stackable and self.quantity > 1 else ""
        durability_str = f" [{self.durability}/{self.max_durability}]" if self.durability is not None else ""
        return f"{self.name} ({self.item_type.value}, {self.rarity.value}){qty_str}{durability_str}"
    
    def __repr__(self) -> str:
        """Detailed representation of the item."""
        return (f"Item(name='{self.name}', type={self.item_type}, rarity={self.rarity}, "
                f"value={self.value}, effects={self.effects})")


# Predefined item templates
class ItemTemplates:
    """Common item templates for quick item creation."""
    
    @staticmethod
    def health_potion(size: str = "small") -> Item:
        """Create a health potion."""
        sizes = {
            'small': (25, 10, ItemRarity.COMMON),
            'medium': (50, 25, ItemRarity.UNCOMMON),
            'large': (100, 50, ItemRarity.RARE)
        }
        heal, value, rarity = sizes.get(size, sizes['small'])
        return Item(
            name=f"{size.capitalize()} Health Potion",
            item_type=ItemType.POTION,
            rarity=rarity,
            value=value,
            effects={'heal': heal},
            description=f"Restores {heal} HP",
            stackable=True
        )
    
    @staticmethod
    def sword(quality: str = "common") -> Item:
        """Create a sword."""
        qualities = {
            'common': (5, 50, ItemRarity.COMMON, 50),
            'uncommon': (8, 100, ItemRarity.UNCOMMON, 75),
            'rare': (12, 250, ItemRarity.RARE, 100),
            'epic': (18, 500, ItemRarity.EPIC, 150),
            'legendary': (25, 1000, ItemRarity.LEGENDARY, 200)
        }
        attack, value, rarity, durability = qualities.get(quality, qualities['common'])
        return Item(
            name=f"{quality.capitalize()} Sword",
            item_type=ItemType.WEAPON,
            rarity=rarity,
            value=value,
            effects={'attack': attack},
            description=f"A {quality} sword that increases attack by {attack}",
            durability=durability
        )
    
    @staticmethod
    def shield(quality: str = "common") -> Item:
        """Create a shield."""
        qualities = {
            'common': (5, 50, ItemRarity.COMMON, 50),
            'uncommon': (8, 100, ItemRarity.UNCOMMON, 75),
            'rare': (12, 250, ItemRarity.RARE, 100),
            'epic': (18, 500, ItemRarity.EPIC, 150),
            'legendary': (25, 1000, ItemRarity.LEGENDARY, 200)
        }
        defense, value, rarity, durability = qualities.get(quality, qualities['common'])
        return Item(
            name=f"{quality.capitalize()} Shield",
            item_type=ItemType.ARMOR,
            rarity=rarity,
            value=value,
            effects={'defense': defense},
            description=f"A {quality} shield that increases defense by {defense}",
            durability=durability
        )
