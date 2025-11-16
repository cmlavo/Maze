"""
Inventory module for the board game simulator.
Represents a list of Item objects with unique interaction functionalities.
"""

from src.items import Item, Weapon
import copy

class Inventory:
    """
    Represents an inventory holding multiple items.
    
    Attributes:
        items (list): List of Item objects in the inventory
    """
    
    def __init__(self, items = []):
        """
        Initialize an inventory.
        Args:
            items (list(Item)): List of Item objects to initialize the inventory with. Defaults to an empty list.
        """
        assert all(isinstance(item, Item) for item in items), "All elements in items must be of type Item"
        self.items = items

    def add_item(self, item):
        """Add an item to the inventory."""
        if item is not None:
            self.items.append(item)

    def remove_item(self, item):
        """Remove an item from the inventory if it exists."""
        if item in self.items:
            self.items.remove(item)

    def empty_inventory(self):
        """Remove all items from the inventory."""
        self.items.clear()

    def get_first_weapon(self):
        """Return the first weapon found in the inventory, or None if no weapon exists."""
        for item in self.items:
            if isinstance(item, Weapon):
                return item
        return None
    
    def copy(self):
        """Return a copy of the inventory."""
        return copy.deepcopy(self)
    
    def __str__(self):
        """String representation of the inventory."""
        item_names = [item.name for item in self.items]
        return f"Inventory({item_names})"