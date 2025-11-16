"""
Example usage of the Board Game Simulator.

This script demonstrates how to use various components of the simulator.
"""
from src.players import Player
from src.monsters import Monster, MonsterType
from src.items import ItemTemplates
from src.events import EventTemplates, EventManager
from src.board import Board
from src.dice_roller import DiceRoller
from src.state_machines import (
    PlayerStateMachine, MonsterStateMachine,
    PlayerBehaviorSettings, MonsterBehaviorSettings
)
from src.simulator import Simulator


def example_basic_player():
    """Example: Creating and using players."""
    print("=== Basic Player Example ===")
    
    # Create players of different types
    human = Player("Alice", "human", level=1)
    cyborg = Player("Bob", "cyborg", level=2)
    
    print(human)
    print(cyborg)
    
    # Use special abilities
    result = human.use_special_ability()
    print(f"Special ability: {result['ability']} - {result['effect']}")
    
    # Combat simulation
    cyborg.take_damage(30)
    print(f"After damage: {cyborg}")
    
    cyborg.heal(20)
    print(f"After healing: {cyborg}")
    print()


def example_dice_roller():
    """Example: Using the dice roller."""
    print("=== Dice Roller Example ===")
    
    dice = DiceRoller()
    
    # Roll different dice types
    d20_total, d20_rolls = dice.roll('d20')
    print(f"d20 roll: {d20_total} (rolls: {d20_rolls})")
    
    # Roll multiple dice
    total, rolls = dice.roll('d6', num_dice=3)
    print(f"3d6 roll: {total} (rolls: {rolls})")
    
    # Roll with advantage
    adv_result, adv_rolls = dice.roll_with_advantage('d20')
    print(f"d20 with advantage: {adv_result} (rolls: {adv_rolls})")
    
    # Add custom dice
    dice.add_dice_type('d7', 7)
    custom_total, custom_rolls = dice.roll('d7', num_dice=2)
    print(f"2d7 roll: {custom_total} (rolls: {custom_rolls})")
    print()


def example_monsters():
    """Example: Creating and using monsters."""
    print("=== Monsters Example ===")
    
    # Create different monster types
    goblin = Monster("Sneaky", MonsterType.GOBLIN, level=1)
    dragon = Monster("Smaug", MonsterType.DRAGON, level=5)
    
    print(goblin)
    print(dragon)
    
    # Make dragon a boss
    dragon.set_as_boss(True)
    print(f"Boss dragon: {dragon}")
    
    # Special attack
    special = goblin.special_attack()
    print(f"Goblin special: {special['name']} - {special['effect']}")
    print()


def example_items():
    """Example: Creating and using items."""
    print("=== Items Example ===")
    
    # Create items from templates
    health_potion = ItemTemplates.health_potion('medium')
    sword = ItemTemplates.sword('rare')
    shield = ItemTemplates.shield('uncommon')
    
    print(health_potion)
    print(sword)
    print(shield)
    
    # Use a potion
    player = Player("TestPlayer", "human")
    player.take_damage(50)
    print(f"Player before potion: {player}")
    
    result = health_potion.use(player)
    print(f"Potion use result: {result['message']}")
    print(f"Player after potion: {player}")
    print()


def example_board():
    """Example: Creating and using the board."""
    print("=== Board Example ===")
    
    # Create a board
    board = Board(width=8, height=8)
    board.generate_random_layout(wall_probability=0.15)
    
    # Place a player
    player = Player("Hero", "human")
    board.place_entity(player, (0, 0))
    
    # Place a monster
    monster = Monster("Enemy", MonsterType.ORC, level=1)
    board.place_entity(monster, (3, 3))
    
    print("Board layout:")
    print(board.display())
    print()
    
    # Find path
    path = board.find_path(player.position, monster.position)
    if path:
        print(f"Path from player to monster: {path}")
    print()


def example_events():
    """Example: Creating and using events."""
    print("=== Events Example ===")
    
    # Create event manager
    event_manager = EventManager()
    
    # Add events
    event_manager.add_event(EventTemplates.treasure_chest())
    event_manager.add_event(EventTemplates.healing_fountain())
    event_manager.add_event(EventTemplates.merchant_encounter())
    
    # Check which events can trigger
    context = {'gold': 50, 'level': 2}
    triggerable = event_manager.check_events(context)
    
    print(f"Found {len(triggerable)} triggerable events")
    
    # Trigger an event
    if triggerable:
        event = triggerable[0]
        player = Player("Hero", "human")
        result = event_manager.trigger_event(event, player)
        print(f"Triggered event: {result['event_name']}")
        print(f"Description: {result['description']}")
        
        if result['choices_available']:
            print(f"Choices: {result['choices']}")
    print()


def example_state_machines():
    """Example: Using state machines."""
    print("=== State Machines Example ===")
    
    # Create player with aggressive behavior
    player = Player("Warrior", "human", level=2)
    behavior = PlayerBehaviorSettings.aggressive()
    player_sm = PlayerStateMachine(player, behavior)
    
    print(f"Initial state: {player_sm.state}")
    
    # Simulate different contexts
    contexts = [
        {'enemies_nearby': 1, 'treasure_nearby': False},
        {'enemies_nearby': 0, 'treasure_nearby': True},
    ]
    
    for i, context in enumerate(contexts, 1):
        state = player_sm.update(context)
        action = player_sm.get_action()
        print(f"Context {i}: {context}")
        print(f"  New state: {state}, Action: {action}")
    print()


def example_simulation():
    """Example: Running a Monte Carlo simulation."""
    print("=== Simulation Example ===")
    
    # Create simulator
    simulator = Simulator(board_size=(10, 10))
    
    # Run small Monte Carlo simulation
    print("Running 100 simulations...")
    results = simulator.run_monte_carlo(
        player_type='human',
        player_level=2,
        num_simulations=100,
        player_behavior=PlayerBehaviorSettings.balanced(),
        num_monsters=3,
        max_turns=50
    )
    
    # Display results
    print("\nSimulation Results:")
    print(f"Win Rate: {results['win_rate']:.2%}")
    print(f"Average Turns: {results['avg_turns']:.1f}")
    print(f"Average Monsters Defeated: {results['avg_monsters_defeated']:.1f}")
    
    # Get balance report
    print(simulator.get_balance_report())


def main():
    """Run all examples."""
    print("Board Game Simulator - Example Usage\n")
    print("=" * 50)
    print()
    
    example_basic_player()
    example_dice_roller()
    example_monsters()
    example_items()
    example_board()
    example_events()
    example_state_machines()
    example_simulation()
    
    print("=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    main()
