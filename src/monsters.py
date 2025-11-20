"""
Monsters module for the board game simulator.
Represents non-player monsters with various attributes and abilities.
"""
import csv
import os
from typing import Tuple
import copy
from abc import ABC, abstractmethod
from src.dice_roller import DiceRoller
from players import Entity

class Monster(Entity):
    