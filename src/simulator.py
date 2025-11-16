"""
Simulator module for Monte Carlo simulations of the board game.
Used to test game balance and analyze game dynamics.
"""
from typing import List, Dict, Optional, Tuple
import random
import statistics
from src.players import Player
from src.monsters import Monster, MonsterType
from src.board import Board
from src.dice_roller import DiceRoller
from src.events import Event, EventManager, EventTemplates
from src.state_machines import (
    PlayerStateMachine, MonsterStateMachine,
    PlayerBehaviorSettings, MonsterBehaviorSettings
)


class GameResult:
    """
    Represents the result of a single game simulation.
    
    Attributes:
        player_won (bool): Whether the player won
        turns_taken (int): Number of turns
        final_health (int): Player's final health
        damage_dealt (int): Total damage dealt by player
        damage_taken (int): Total damage taken by player
        items_collected (int): Number of items collected
        monsters_defeated (int): Number of monsters defeated
        events_triggered (int): Number of events triggered
    """
    
    def __init__(self):
        """Initialize a GameResult."""
        self.player_won = False
        self.turns_taken = 0
        self.final_health = 0
        self.damage_dealt = 0
        self.damage_taken = 0
        self.items_collected = 0
        self.monsters_defeated = 0
        self.events_triggered = 0
        self.player_state_history = []
        self.monster_state_history = []


class Simulator:
    """
    Simulator for running Monte Carlo simulations of the board game.
    
    Attributes:
        board_size (tuple): Size of the game board (width, height)
        dice_roller (DiceRoller): Dice roller for the simulation
        results (list): List of GameResult objects from simulations
    """
    
    def __init__(self, board_size: Tuple[int, int] = (10, 10)):
        """
        Initialize the Simulator.
        
        Args:
            board_size (tuple): Size of the game board (width, height)
        """
        self.board_size = board_size
        self.dice_roller = DiceRoller()
        self.results = []
    
    def run_simulation(self,
                      player_type: str,
                      player_level: int,
                      player_behavior: Optional[PlayerBehaviorSettings] = None,
                      num_monsters: int = 5,
                      max_turns: int = 100) -> GameResult:
        """
        Run a single game simulation.
        
        Args:
            player_type (str): Type of player (human, monster, cyborg, wartech)
            player_level (int): Player level
            player_behavior (PlayerBehaviorSettings): Player behavior settings
            num_monsters (int): Number of monsters to spawn
            max_turns (int): Maximum number of turns
            
        Returns:
            GameResult: Result of the simulation
        """
        # Initialize game components
        result = GameResult()
        board = Board(*self.board_size)
        board.generate_random_layout(wall_probability=0.15)
        
        # Create player
        player = Player(name="TestPlayer", player_type=player_type, level=player_level)
        player_sm = PlayerStateMachine(player, player_behavior or PlayerBehaviorSettings.balanced())
        board.place_entity(player, board.start_position)
        
        # Create monsters
        monsters = []
        monster_sms = []
        monster_types = list(MonsterType)
        
        for i in range(num_monsters):
            monster_type = random.choice(monster_types)
            monster = Monster(f"Monster{i}", monster_type, level=player_level)
            monster_sm = MonsterStateMachine(monster, MonsterBehaviorSettings.balanced())
            
            # Place monster at random valid position
            placed = False
            for _ in range(50):  # Try up to 50 times
                x = random.randint(2, board.width - 3)
                y = random.randint(2, board.height - 3)
                if board.place_entity(monster, (x, y)):
                    monster_sm.home_position = (x, y)
                    placed = True
                    break
            
            if placed:
                monsters.append(monster)
                monster_sms.append(monster_sm)
        
        # Create event manager
        event_manager = EventManager()
        event_manager.add_event(EventTemplates.treasure_chest())
        event_manager.add_event(EventTemplates.poison_trap())
        event_manager.add_event(EventTemplates.healing_fountain())
        event_manager.add_event(EventTemplates.merchant_encounter())
        
        # Run simulation
        for turn in range(max_turns):
            result.turns_taken = turn + 1
            
            # Check win condition
            if player.position == board.exit_position:
                result.player_won = True
                break
            
            # Check lose condition
            if not player.is_alive():
                result.player_won = False
                break
            
            # Update player state machine
            context = self._build_context(player, monsters, board)
            player_sm.update(context)
            action = player_sm.get_action()
            
            # Execute player action
            if action == "explore":
                self._execute_explore(player, board, event_manager, result)
            elif action == "attack":
                self._execute_combat(player, monsters, board, result)
            elif action == "rest":
                heal_amount = max(5, player.max_health // 10)
                player.heal(heal_amount)
            elif action == "flee":
                self._execute_flee(player, monsters, board)
            
            # Update monsters
            for monster, monster_sm in zip(monsters, monster_sms):
                if monster.is_alive():
                    monster_context = self._build_monster_context(monster, player, board, monster_sm.home_position)
                    monster_sm.update(monster_context)
                    monster_action = monster_sm.get_action()
                    
                    if monster_action == "chase":
                        self._execute_chase(monster, player, board)
                    elif monster_action == "attack":
                        self._execute_monster_attack(monster, player, result)
                    elif monster_action == "patrol":
                        self._execute_patrol(monster, board, monster_sm.home_position)
        
        # Record final statistics
        result.final_health = player.health
        result.player_state_history = player_sm.state_history.copy()
        
        return result
    
    def run_monte_carlo(self,
                       player_type: str,
                       player_level: int,
                       num_simulations: int = 1000,
                       player_behavior: Optional[PlayerBehaviorSettings] = None,
                       num_monsters: int = 5,
                       max_turns: int = 100) -> Dict:
        """
        Run multiple Monte Carlo simulations.
        
        Args:
            player_type (str): Type of player
            player_level (int): Player level
            num_simulations (int): Number of simulations to run
            player_behavior (PlayerBehaviorSettings): Player behavior settings
            num_monsters (int): Number of monsters per game
            max_turns (int): Maximum turns per game
            
        Returns:
            Dict: Statistical summary of results
        """
        self.results = []
        
        for i in range(num_simulations):
            result = self.run_simulation(
                player_type=player_type,
                player_level=player_level,
                player_behavior=player_behavior,
                num_monsters=num_monsters,
                max_turns=max_turns
            )
            self.results.append(result)
        
        return self.analyze_results()
    
    def analyze_results(self) -> Dict:
        """
        Analyze simulation results and generate statistics.
        
        Returns:
            Dict: Statistical analysis of results
        """
        if not self.results:
            return {}
        
        wins = sum(1 for r in self.results if r.player_won)
        win_rate = wins / len(self.results)
        
        turns = [r.turns_taken for r in self.results]
        final_healths = [r.final_health for r in self.results]
        damage_dealt = [r.damage_dealt for r in self.results]
        damage_taken = [r.damage_taken for r in self.results]
        monsters_defeated = [r.monsters_defeated for r in self.results]
        
        analysis = {
            'total_simulations': len(self.results),
            'wins': wins,
            'losses': len(self.results) - wins,
            'win_rate': win_rate,
            'avg_turns': statistics.mean(turns),
            'median_turns': statistics.median(turns),
            'std_turns': statistics.stdev(turns) if len(turns) > 1 else 0,
            'avg_final_health': statistics.mean(final_healths),
            'avg_damage_dealt': statistics.mean(damage_dealt),
            'avg_damage_taken': statistics.mean(damage_taken),
            'avg_monsters_defeated': statistics.mean(monsters_defeated)
        }
        
        return analysis
    
    def _build_context(self, player: Player, monsters: List[Monster], board: Board) -> Dict:
        """Build context dictionary for player state machine."""
        alive_monsters = [m for m in monsters if m.is_alive()]
        
        # Find nearest monster
        min_distance = float('inf')
        for monster in alive_monsters:
            distance = board.get_distance(player.position, monster.position)
            if distance < min_distance:
                min_distance = distance
        
        return {
            'enemies_nearby': len([m for m in alive_monsters if board.get_distance(player.position, m.position) <= 3]),
            'treasure_nearby': False,  # Simplified
            'merchant_nearby': False,  # Simplified
            'nearest_enemy_distance': min_distance if alive_monsters else float('inf')
        }
    
    def _build_monster_context(self, monster: Monster, player: Player, board: Board, home_position: Tuple[int, int]) -> Dict:
        """Build context dictionary for monster state machine."""
        return {
            'nearest_player_distance': board.get_distance(monster.position, player.position),
            'distance_from_home': board.get_distance(monster.position, home_position)
        }
    
    def _execute_explore(self, player: Player, board: Board, event_manager: EventManager, result: GameResult):
        """Execute explore action."""
        # Try to move towards exit
        current_pos = player.position
        adjacent = board.get_adjacent_positions(current_pos)
        
        if adjacent:
            # Move towards exit
            exit_pos = board.exit_position
            best_pos = min(adjacent, key=lambda pos: board.get_distance(pos, exit_pos) if board.is_passable(pos) else float('inf'))
            
            if board.is_passable(best_pos):
                board.move_entity(player, current_pos, best_pos)
    
    def _execute_combat(self, player: Player, monsters: List[Monster], board: Board, result: GameResult):
        """Execute combat action."""
        # Find nearest alive monster
        nearest_monster = None
        min_distance = float('inf')
        
        for monster in monsters:
            if monster.is_alive():
                distance = board.get_distance(player.position, monster.position)
                if distance < min_distance:
                    min_distance = distance
                    nearest_monster = monster
        
        # Attack if in range
        if nearest_monster and min_distance <= 1:
            # Roll for attack
            attack_roll, _ = self.dice_roller.roll('d20')
            if attack_roll + player.attack > 10 + nearest_monster.defense:
                damage_roll, _ = self.dice_roller.roll('d6', num_dice=2)
                damage = damage_roll + player.attack // 2
                actual_damage = nearest_monster.take_damage(damage)
                result.damage_dealt += actual_damage
                
                if not nearest_monster.is_alive():
                    result.monsters_defeated += 1
    
    def _execute_flee(self, player: Player, monsters: List[Monster], board: Board):
        """Execute flee action."""
        # Try to move away from nearest monster
        current_pos = player.position
        adjacent = board.get_adjacent_positions(current_pos)
        
        if adjacent and monsters:
            nearest_monster = min((m for m in monsters if m.is_alive()), 
                                key=lambda m: board.get_distance(player.position, m.position),
                                default=None)
            
            if nearest_monster:
                # Move away from monster
                best_pos = max(adjacent, 
                             key=lambda pos: board.get_distance(pos, nearest_monster.position) if board.is_passable(pos) else 0)
                
                if board.is_passable(best_pos):
                    board.move_entity(player, current_pos, best_pos)
    
    def _execute_chase(self, monster: Monster, player: Player, board: Board):
        """Execute monster chase action."""
        current_pos = monster.position
        adjacent = board.get_adjacent_positions(current_pos)
        
        if adjacent:
            # Move towards player
            best_pos = min(adjacent, 
                         key=lambda pos: board.get_distance(pos, player.position) if board.is_passable(pos) else float('inf'))
            
            if board.is_passable(best_pos):
                board.move_entity(monster, current_pos, best_pos)
    
    def _execute_patrol(self, monster: Monster, board: Board, home_position: Tuple[int, int]):
        """Execute monster patrol action."""
        current_pos = monster.position
        adjacent = board.get_adjacent_positions(current_pos)
        
        if adjacent:
            # Random movement, prefer staying near home
            valid_moves = [pos for pos in adjacent if board.is_passable(pos)]
            if valid_moves:
                next_pos = random.choice(valid_moves)
                board.move_entity(monster, current_pos, next_pos)
    
    def _execute_monster_attack(self, monster: Monster, player: Player, result: GameResult):
        """Execute monster attack on player."""
        attack_roll, _ = self.dice_roller.roll('d20')
        if attack_roll + monster.attack > 10 + player.defense:
            damage_roll, _ = self.dice_roller.roll('d6', num_dice=2)
            damage = damage_roll + monster.attack // 2
            actual_damage = player.take_damage(damage)
            result.damage_taken += actual_damage
    
    def get_balance_report(self) -> str:
        """
        Generate a balance report based on simulation results.
        
        Returns:
            str: Formatted balance report
        """
        if not self.results:
            return "No simulations run yet."
        
        analysis = self.analyze_results()
        
        report = f"""
=== Game Balance Report ===
Total Simulations: {analysis['total_simulations']}
Win Rate: {analysis['win_rate']:.2%}
Wins: {analysis['wins']} | Losses: {analysis['losses']}

Turn Statistics:
  Average: {analysis['avg_turns']:.1f}
  Median: {analysis['median_turns']:.1f}
  Std Dev: {analysis['std_turns']:.1f}

Performance Metrics:
  Avg Final Health: {analysis['avg_final_health']:.1f}
  Avg Damage Dealt: {analysis['avg_damage_dealt']:.1f}
  Avg Damage Taken: {analysis['avg_damage_taken']:.1f}
  Avg Monsters Defeated: {analysis['avg_monsters_defeated']:.1f}

Balance Assessment:
"""
        
        # Add balance recommendations
        if analysis['win_rate'] < 0.3:
            report += "  ⚠️  Game may be too difficult. Consider reducing monster difficulty.\n"
        elif analysis['win_rate'] > 0.7:
            report += "  ⚠️  Game may be too easy. Consider increasing challenge.\n"
        else:
            report += "  ✓  Game balance appears reasonable.\n"
        
        if analysis['avg_turns'] < 20:
            report += "  ⚠️  Games are very short. Consider larger boards or more objectives.\n"
        elif analysis['avg_turns'] > 80:
            report += "  ⚠️  Games are very long. Consider reducing board size or complexity.\n"
        
        return report
