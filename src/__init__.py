"""
Board Game Simulator Package

An object-oriented simulator for a board game featuring:
- Players (human, monster, cyborg, wartech)
- Monsters with various types and behaviors
- Items and equipment system
- Dynamic events
- Game board with pathfinding
- State machines for AI behavior
- Monte Carlo simulation for game balance testing
"""

from src.players import Player
from src.monsters import Monster, MonsterType
from src.items import Item, ItemType, ItemRarity, ItemTemplates
from src.events import Event, EventType, EventManager, EventTemplates
from src.board import Board, Tile, TileType
from src.dice_roller import DiceRoller
from src.state_machines import (
    PlayerStateMachine, MonsterStateMachine,
    PlayerBehaviorSettings, MonsterBehaviorSettings,
    PlayerState, MonsterState
)
from src.simulator import Simulator, GameResult

__version__ = '1.0.0'
__all__ = [
    'Player',
    'Monster', 'MonsterType',
    'Item', 'ItemType', 'ItemRarity', 'ItemTemplates',
    'Event', 'EventType', 'EventManager', 'EventTemplates',
    'Board', 'Tile', 'TileType',
    'DiceRoller',
    'PlayerStateMachine', 'MonsterStateMachine',
    'PlayerBehaviorSettings', 'MonsterBehaviorSettings',
    'PlayerState', 'MonsterState',
    'Simulator', 'GameResult'
]
