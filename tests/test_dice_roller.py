"""
Unit tests for the Dice Roller module.
"""
import unittest
from src.dice_roller import DiceRoller


class TestDiceRoller(unittest.TestCase):
    """Test cases for DiceRoller class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.dice = DiceRoller()
    
    def test_initialization(self):
        """Test dice roller initialization."""
        self.assertIsNotNone(self.dice.dice_types)
        self.assertIn('d6', self.dice.dice_types)
        self.assertIn('d20', self.dice.dice_types)
    
    def test_roll_single_die(self):
        """Test rolling a single die."""
        total, rolls = self.dice.roll('d6')
        self.assertEqual(len(rolls), 1)
        self.assertEqual(total, rolls[0])
        self.assertGreaterEqual(total, 1)
        self.assertLessEqual(total, 6)
    
    def test_roll_multiple_dice(self):
        """Test rolling multiple dice."""
        total, rolls = self.dice.roll('d6', num_dice=3)
        self.assertEqual(len(rolls), 3)
        self.assertEqual(total, sum(rolls))
        for roll in rolls:
            self.assertGreaterEqual(roll, 1)
            self.assertLessEqual(roll, 6)
    
    def test_roll_different_dice_types(self):
        """Test rolling different dice types."""
        for dice_type, sides in [('d4', 4), ('d8', 8), ('d20', 20)]:
            total, rolls = self.dice.roll(dice_type)
            self.assertGreaterEqual(total, 1)
            self.assertLessEqual(total, sides)
    
    def test_invalid_dice_type(self):
        """Test rolling invalid dice type raises error."""
        with self.assertRaises(ValueError):
            self.dice.roll('d999')
    
    def test_invalid_num_dice(self):
        """Test rolling invalid number of dice raises error."""
        with self.assertRaises(ValueError):
            self.dice.roll('d6', num_dice=0)
    
    def test_roll_with_advantage(self):
        """Test rolling with advantage."""
        result, rolls = self.dice.roll_with_advantage('d20')
        self.assertEqual(len(rolls), 2)
        self.assertEqual(result, max(rolls))
    
    def test_roll_with_disadvantage(self):
        """Test rolling with disadvantage."""
        result, rolls = self.dice.roll_with_disadvantage('d20')
        self.assertEqual(len(rolls), 2)
        self.assertEqual(result, min(rolls))
    
    def test_add_custom_dice(self):
        """Test adding custom dice type."""
        self.dice.add_dice_type('d7', 7)
        self.assertIn('d7', self.dice.dice_types)
        
        total, rolls = self.dice.roll('d7')
        self.assertGreaterEqual(total, 1)
        self.assertLessEqual(total, 7)
    
    def test_add_invalid_dice(self):
        """Test adding invalid dice raises error."""
        with self.assertRaises(ValueError):
            self.dice.add_dice_type('d1', 1)
    
    def test_get_available_dice(self):
        """Test getting available dice types."""
        available = self.dice.get_available_dice()
        self.assertIsInstance(available, list)
        self.assertIn('d6', available)
        self.assertIn('d20', available)


if __name__ == '__main__':
    unittest.main()
