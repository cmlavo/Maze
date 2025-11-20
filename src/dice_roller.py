"""
Dice Roller module for the board game simulator.
Handles different dice types and rolling mechanics.
"""
import random

class DiceRoller:
    """
    A class to handle dice rolling with support for various dice types.
    """
    
    def __init__(self, sides: int = 20, number: int = 1, modifier: int = 0, multiplier: int = 1):
        """
        Initialize the DiceRoller with standard or custom dice types.
        
        Args:
            sides (int): Number of sides on the dice. Defaults to 20.
            number (int): Number of dice to roll. Defaults to 1.
            modifier (int): Modifier to add to the roll. Defaults to 0.
            multiplier (int): Multiplier for the final roll result. Defaults to 1.
        """
        self.sides = sides
        self.number = number
        self.modifier = modifier
        self.multiplier = multiplier

    def roll(self) -> int:
        """
        Roll the dice.
        
        Returns:
            int: Total sum of dice roll(s).
        """
        total = 0
        for _ in range(self.number):
            roll = random.randint(1, self.sides)
            total += roll
        total = (total + self.modifier) * self.multiplier
        return total
        
