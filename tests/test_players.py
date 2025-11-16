"""
Unit tests for the Players module.
"""
import unittest
from src.players import Player


class TestPlayer(unittest.TestCase):
    """Test cases for Player class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.human = Player("TestHuman", "human", level=1)
        self.cyborg = Player("TestCyborg", "cyborg", level=2)
    
    def test_initialization(self):
        """Test player initialization."""
        self.assertEqual(self.human.name, "TestHuman")
        self.assertEqual(self.human.player_type, "human")
        self.assertEqual(self.human.level, 1)
        self.assertGreater(self.human.health, 0)
        self.assertGreater(self.human.max_health, 0)
    
    def test_different_player_types(self):
        """Test different player types have different stats."""
        monster = Player("TestMonster", "monster", level=1)
        wartech = Player("TestWartech", "wartech", level=1)
        
        # Monsters should have higher health
        self.assertGreater(monster.max_health, self.human.max_health)
        
        # Wartech should have higher defense
        self.assertGreater(wartech.defense, self.human.defense)
    
    def test_take_damage(self):
        """Test taking damage reduces health."""
        initial_health = self.human.health
        damage = self.human.take_damage(20)
        
        self.assertLess(self.human.health, initial_health)
        self.assertGreater(damage, 0)
    
    def test_take_damage_cannot_go_negative(self):
        """Test health cannot go below zero."""
        self.human.take_damage(1000)
        self.assertEqual(self.human.health, 0)
    
    def test_heal(self):
        """Test healing increases health."""
        self.human.take_damage(50)
        damaged_health = self.human.health
        self.human.heal(20)
        
        self.assertGreater(self.human.health, damaged_health)
    
    def test_heal_cannot_exceed_max(self):
        """Test healing cannot exceed max health."""
        self.human.heal(1000)
        self.assertEqual(self.human.health, self.human.max_health)
    
    def test_is_alive(self):
        """Test is_alive method."""
        self.assertTrue(self.human.is_alive())
        
        self.human.take_damage(1000)
        self.assertFalse(self.human.is_alive())
    
    def test_move(self):
        """Test moving player."""
        new_pos = (5, 5)
        self.human.move(new_pos)
        self.assertEqual(self.human.position, new_pos)
    
    def test_inventory_management(self):
        """Test adding and removing items."""
        item = "test_item"
        
        self.human.add_item(item)
        self.assertIn(item, self.human.inventory)
        
        self.human.remove_item(item)
        self.assertNotIn(item, self.human.inventory)
    
    def test_use_special_ability(self):
        """Test using special ability."""
        result = self.human.use_special_ability()
        
        self.assertIn('ability', result)
        self.assertIn('success', result)
        self.assertIn('effect', result)
        self.assertTrue(result['success'])
    
    def test_level_up(self):
        """Test leveling up increases stats."""
        initial_level = self.human.level
        initial_health = self.human.max_health
        initial_attack = self.human.attack
        
        self.human.level_up()
        
        self.assertEqual(self.human.level, initial_level + 1)
        self.assertGreater(self.human.max_health, initial_health)
        self.assertGreater(self.human.attack, initial_attack)
        self.assertEqual(self.human.health, self.human.max_health)
    
    def test_string_representation(self):
        """Test string representation."""
        player_str = str(self.human)
        self.assertIn("TestHuman", player_str)
        self.assertIn("Human", player_str)
        self.assertIn("Lv.1", player_str)


if __name__ == '__main__':
    unittest.main()
