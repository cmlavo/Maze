"""
Dice Roller module for the board game simulator.
Handles different dice types and rolling mechanics.
"""
import random
from typing import List, Tuple


class DiceRoller:
    """
    A class to handle dice rolling with support for various dice types.
    
    Attributes:
        dice_types (dict): Available dice types with their number of sides
    """
    
    STANDARD_DICE = {
        'd4': 4,
        'd6': 6,
        'd8': 8,
        'd10': 10,
        'd12': 12,
        'd20': 20,
        'd100': 100
    }
    
    def __init__(self, custom_dice: dict = None):
        """
        Initialize the DiceRoller with standard or custom dice types.
        
        Args:
            custom_dice (dict, optional): Custom dice types to add/override
        """
        self.dice_types = self.STANDARD_DICE.copy()
        if custom_dice:
            self.dice_types.update(custom_dice)
    
    def roll(self, dice_type: str, num_dice: int = 1) -> Tuple[int, List[int]]:
        """
        Roll one or more dice of a specific type.
        
        Args:
            dice_type (str): The type of dice to roll (e.g., 'd6', 'd20')
            num_dice (int): Number of dice to roll
            
        Returns:
            Tuple[int, List[int]]: (total sum, list of individual rolls)
            
        Raises:
            ValueError: If dice_type is not recognized
        """
        if dice_type not in self.dice_types:
            raise ValueError(f"Unknown dice type: {dice_type}. Available: {list(self.dice_types.keys())}")
        
        if num_dice < 1:
            raise ValueError("Number of dice must be at least 1")
        
        sides = self.dice_types[dice_type]
        rolls = [random.randint(1, sides) for _ in range(num_dice)]
        return sum(rolls), rolls
    
    def roll_with_advantage(self, dice_type: str) -> Tuple[int, List[int]]:
        """
        Roll with advantage (roll twice, take higher value).
        
        Args:
            dice_type (str): The type of dice to roll
            
        Returns:
            Tuple[int, List[int]]: (highest roll, list of both rolls)
        """
        total, rolls = self.roll(dice_type, num_dice=2)
        return max(rolls), rolls
    
    def roll_with_disadvantage(self, dice_type: str) -> Tuple[int, List[int]]:
        """
        Roll with disadvantage (roll twice, take lower value).
        
        Args:
            dice_type (str): The type of dice to roll
            
        Returns:
            Tuple[int, List[int]]: (lowest roll, list of both rolls)
        """
        total, rolls = self.roll(dice_type, num_dice=2)
        return min(rolls), rolls
    
    def add_dice_type(self, name: str, sides: int):
        """
        Add a new dice type to the roller.
        
        Args:
            name (str): Name of the dice type (e.g., 'd7')
            sides (int): Number of sides on the dice
        """
        if sides < 2:
            raise ValueError("Dice must have at least 2 sides")
        self.dice_types[name] = sides
    
    def get_available_dice(self) -> List[str]:
        """
        Get list of available dice types.
        
        Returns:
            List[str]: List of dice type names
        """
        return list(self.dice_types.keys())
