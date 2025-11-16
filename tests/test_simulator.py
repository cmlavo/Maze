"""
Unit tests for the Simulator module.
"""
import unittest
from src.simulator import Simulator, GameResult
from src.state_machines import PlayerBehaviorSettings


class TestGameResult(unittest.TestCase):
    """Test cases for GameResult class."""
    
    def test_initialization(self):
        """Test game result initialization."""
        result = GameResult()
        self.assertFalse(result.player_won)
        self.assertEqual(result.turns_taken, 0)
        self.assertEqual(result.final_health, 0)
        self.assertEqual(result.damage_dealt, 0)


class TestSimulator(unittest.TestCase):
    """Test cases for Simulator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.simulator = Simulator(board_size=(8, 8))
    
    def test_initialization(self):
        """Test simulator initialization."""
        self.assertEqual(self.simulator.board_size, (8, 8))
        self.assertIsNotNone(self.simulator.dice_roller)
        self.assertEqual(len(self.simulator.results), 0)
    
    def test_run_single_simulation(self):
        """Test running a single simulation."""
        result = self.simulator.run_simulation(
            player_type='human',
            player_level=1,
            num_monsters=2,
            max_turns=30
        )
        
        self.assertIsInstance(result, GameResult)
        self.assertGreaterEqual(result.turns_taken, 1)
        self.assertLessEqual(result.turns_taken, 30)
    
    def test_simulation_with_different_player_types(self):
        """Test simulations with different player types."""
        for player_type in ['human', 'cyborg', 'monster', 'wartech']:
            result = self.simulator.run_simulation(
                player_type=player_type,
                player_level=1,
                num_monsters=1,
                max_turns=20
            )
            self.assertIsInstance(result, GameResult)
    
    def test_simulation_with_behavior_settings(self):
        """Test simulation with different behavior settings."""
        behaviors = [
            PlayerBehaviorSettings.aggressive(),
            PlayerBehaviorSettings.cautious(),
            PlayerBehaviorSettings.balanced()
        ]
        
        for behavior in behaviors:
            result = self.simulator.run_simulation(
                player_type='human',
                player_level=1,
                player_behavior=behavior,
                num_monsters=1,
                max_turns=20
            )
            self.assertIsInstance(result, GameResult)
    
    def test_run_monte_carlo(self):
        """Test running Monte Carlo simulations."""
        results = self.simulator.run_monte_carlo(
            player_type='human',
            player_level=1,
            num_simulations=10,
            num_monsters=1,
            max_turns=20
        )
        
        self.assertIn('total_simulations', results)
        self.assertEqual(results['total_simulations'], 10)
        self.assertIn('win_rate', results)
        self.assertIn('avg_turns', results)
    
    def test_analyze_results(self):
        """Test analyzing simulation results."""
        # Run some simulations first
        for _ in range(5):
            result = self.simulator.run_simulation(
                player_type='human',
                player_level=1,
                num_monsters=1,
                max_turns=20
            )
            self.simulator.results.append(result)
        
        analysis = self.simulator.analyze_results()
        
        self.assertEqual(analysis['total_simulations'], 5)
        self.assertIn('win_rate', analysis)
        self.assertIn('avg_turns', analysis)
        self.assertGreaterEqual(analysis['win_rate'], 0.0)
        self.assertLessEqual(analysis['win_rate'], 1.0)
    
    def test_get_balance_report(self):
        """Test generating balance report."""
        # Run a few simulations
        self.simulator.run_monte_carlo(
            player_type='human',
            player_level=1,
            num_simulations=5,
            num_monsters=1,
            max_turns=20
        )
        
        report = self.simulator.get_balance_report()
        self.assertIsInstance(report, str)
        self.assertIn('Game Balance Report', report)
        self.assertIn('Win Rate', report)


if __name__ == '__main__':
    unittest.main()
