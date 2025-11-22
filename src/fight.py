"""
Module for fight mechanics between players and players, and players and monsters.
"""
from src.players import Entity
from src.monsters import Monster, Monster1, Monster2, Guardian
from src.dice_roller import DiceRoller
from src.events import Event
from src.state_machines import StateMachine, MonsterStateMachine, PlayerStateMachine, GuardianStateMachine

class Fight(Event):
    """
    Represents a fight event between two entities (players or monsters).

    Attributes:
        combattants (list[Entity]): List of entities involved in the fight, in turn order.
        is_active (bool): Status indicating if the fight is ongoing.
        turn_counter (int): Counter to track the current turn in the fight.
    """

    def __init__(self, combattants):
        """
        Initializes a Fight event with the given combattants.

        Args:
            combattants (list[Entity]): List of entities involved in the fight.
        """
        super().__init__()
        self.combattants = combattants
        self.is_active = True
        self.turn_counter = 0

    def _load_state_machines(self):
        """
        Load state machines for each combattant.
        Returns:
            list: List of state machines corresponding to each combattant.
        """
        state_machines = []
        for entity in self.combattants:
            if isinstance(entity, Guardian):
                state_machines.append(GuardianStateMachine(entity))
            elif isinstance(entity, Monster1) or isinstance(entity, Monster2):
                state_machines.append(MonsterStateMachine(entity))
            else:
                state_machines.append(PlayerStateMachine(entity))
        return state_machines

    def run(self):
        """
        Runs the fight until it ends.
        Returns:
            alive (list[Entity]): List of entities that are still alive after the fight.
        """
        while self.is_active:
            for entity, state_machine in zip(self.combattants, self.state_machines):
                if not entity.is_alive:
                    continue  # Skip dead entities
                self.act(entity, state_machine)