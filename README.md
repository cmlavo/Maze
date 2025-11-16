# Maze
Numerical simulator of the in-development board game

## Overview

An object-oriented simulator for a board game featuring players, monsters, items, events, and Monte Carlo simulations for game balance testing.

## Features

- **Multiple Player Types**: Human, Monster, Cyborg, and Wartech classes with unique stats and abilities
- **Monster System**: Various monster types (Goblin, Orc, Troll, Dragon, Undead, Demon) with distinct behaviors
- **Items & Equipment**: Weapons, armor, potions, and consumables with rarity levels
- **Dynamic Events**: Treasure chests, traps, merchants, boss battles, and more
- **Game Board**: Grid-based board with pathfinding and spatial logic
- **Dice Roller**: Flexible dice rolling system supporting various dice types (d4, d6, d8, d10, d12, d20, d100)
- **AI State Machines**: Configurable behavior patterns for both players and monsters
- **Monte Carlo Simulator**: Run thousands of simulations to test game balance

## Installation

```bash
# Clone the repository
git clone https://github.com/cmlavo/Maze.git
cd Maze

# No external dependencies required - uses only Python standard library
python3 examples.py
```

## Quick Start

### Creating Players

```python
from src.players import Player

# Create players with different types
human = Player("Alice", "human", level=1)
cyborg = Player("Bob", "cyborg", level=2)
wartech = Player("Charlie", "wartech", level=3)

print(human)  # Alice (Human Lv.1): HP 100/100, ATK 10, DEF 8, SPD 6
```

### Rolling Dice

```python
from src.dice_roller import DiceRoller

dice = DiceRoller()
total, rolls = dice.roll('d20')
print(f"Rolled: {total}")

# Roll with advantage
result, rolls = dice.roll_with_advantage('d20')
```

### Creating Monsters

```python
from src.monsters import Monster, MonsterType

goblin = Monster("Sneaky", MonsterType.GOBLIN, level=1)
dragon = Monster("Smaug", MonsterType.DRAGON, level=5)
dragon.set_as_boss(True)  # Make it a boss
```

### Setting Up the Board

```python
from src.board import Board

board = Board(width=10, height=10)
board.generate_random_layout(wall_probability=0.15)
board.place_entity(player, (0, 0))
print(board.display())
```

### Running Simulations

```python
from src.simulator import Simulator
from src.state_machines import PlayerBehaviorSettings

simulator = Simulator(board_size=(10, 10))
results = simulator.run_monte_carlo(
    player_type='human',
    player_level=2,
    num_simulations=1000,
    player_behavior=PlayerBehaviorSettings.balanced(),
    num_monsters=3
)

print(f"Win Rate: {results['win_rate']:.2%}")
print(simulator.get_balance_report())
```

## Project Structure

```
Maze/
├── data/
│   └── player_stats.csv         # Player statistics by type and level
├── src/
│   ├── __init__.py              # Package initialization
│   ├── players.py               # Player class implementation
│   ├── monsters.py              # Monster class implementation
│   ├── items.py                 # Items and equipment system
│   ├── events.py                # Game events system
│   ├── board.py                 # Game board implementation
│   ├── dice_roller.py           # Dice rolling mechanics
│   ├── state_machines.py        # AI behavior state machines
│   └── simulator.py             # Monte Carlo simulation engine
├── tests/                       # Unit tests
├── examples.py                  # Example usage
└── README.md                    # This file
```

## Player Types

| Type    | Health | Attack | Defense | Speed | Special Ability      |
|---------|--------|--------|---------|-------|---------------------|
| Human   | 100    | 10     | 8       | 6     | Tactical Insight    |
| Monster | 150    | 15     | 5       | 8     | Berserker Rage      |
| Cyborg  | 110    | 12     | 10      | 7     | Tech Enhancement    |
| Wartech | 120    | 13     | 12      | 5     | Heavy Artillery     |

*Stats shown are for Level 1. Stats increase with level.*

## State Machine Behaviors

### Player Behaviors
- **Aggressive**: High aggression, low caution
- **Cautious**: Low aggression, high caution, higher health threshold for retreat
- **Greedy**: High greed, treasure-focused
- **Explorer**: High exploration tendency
- **Balanced**: Well-rounded behavior

### Monster Behaviors
- **Aggressive**: Wide chase range, relentless pursuit
- **Defensive**: Small patrol area, cautious
- **Balanced**: Standard behavior

## Running Tests

```bash
python3 -m pytest tests/
```

## Examples

Run the examples script to see all features in action:

```bash
python3 examples.py
```

This demonstrates:
- Player creation and abilities
- Dice rolling mechanics
- Monster types and special attacks
- Item system usage
- Board setup and pathfinding
- Event system
- State machines
- Monte Carlo simulations

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

