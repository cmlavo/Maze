import random
import math
from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from dataclasses import dataclass

@dataclass
class Personality:
    """
    Represents personality traits for a player.
    Attributes:
        aggressiveness (float): Tendency to attack.
        greediness (float): Tendency to seek rewards.
        cautiousness (float): Tendency to avoid risks.
        strategicness (float): Tendency to plan actions.
        agreeableness (float): Tendency to cooperate.
        expendability (float): Tendency to sacrifice for others.
        unpredictability (float): Tendency to act randomly.
        influencability (float): Tendency to be influenced by others.
    """

    def __init__(self, personality: str = "default"):
        self._load_stats(personality)

    def _load_stats(self, personality: str):
        """
        Load personality stats from a CSV file.

        Args:
            personality (str): Name of the personality to load.
        """
        import csv
        import os

        stats_file = os.path.join("configs", "personalities.csv")
        if not os.path.exists(stats_file):
            raise FileNotFoundError(f"Personality stats file {stats_file} not found.")

        with open(stats_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['name'] == personality:
                    self.aggressiveness = float(row['aggressiveness'])
                    self.greediness = float(row['greediness'])
                    self.cautiousness = float(row['cautiousness'])
                    self.strategicness = float(row['strategicness'])
                    self.agreeableness = float(row['agreeableness'])
                    self.expendability = float(row['expendability'])
                    self.unpredictability = float(row['unpredictability'])
                    self.influencability = float(row['influencability'])
                    return
        raise ValueError(f"Personality {personality} not found in stats file.")

class DecisionContext:
    """
    Context for making decisions in the state machine.
    Attributes:
        in_combat (bool): Whether the entity is in combat.
        combatants (list[Entity]): List of entities in combat.
        self_entity (Entity): The entity making the decision.
        inventory (Inventory): The inventory of the entity.
        treasure (int): The level of treasure available to the creature.
        
    """