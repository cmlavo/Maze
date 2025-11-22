# add parent folder to path so that src imports work
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.players import Player, Monster, Humanoid, Cyborg, Wartech
from src.items import Weapon, Item, WeaponAttachment
from src.inventory import Inventory


# initialise an inventory for testing
shotgun = Weapon("shotgun")
machine_gun = Weapon("machine gun")
two_hand_laser_gun = Weapon("2-hand laser gun")
starting_inventory = Inventory([shotgun, machine_gun, machine_gun])

# initialise four players
players = [None] * 4
players[0] = Humanoid("Test Humanoid", inventory=starting_inventory.copy())
players[1] = Cyborg("Test Cyborg", inventory=starting_inventory.copy())
players[2] = Wartech("Test Wartech", inventory=starting_inventory.copy())
players[3] = Monster("Test Monster", inventory=starting_inventory.copy())

for player in players:
    starting_inventory = Inventory([shotgun, machine_gun, machine_gun])
    print(f"\n--- Testing player: {player.name} ---")
    # equipping two same-order one-handed weapons
    print(f"Initial inventory: {player.inventory}")
    player.equip_weapon(shotgun)
    player.equip_weapon(machine_gun)
    print(f"One-handed equip inventory: {player.inventory}")
    print(f"One-handed equip hands: {player.hands}")

    # equipping a two-handed weapon    
    player.give_item(two_hand_laser_gun)
    print(f"Two-handed give inventory: {player.inventory}")
    player.equip_weapon(two_hand_laser_gun, 0)
    print(f"Two-handed equip inventory: {player.inventory}")
    print(f"Two-handed equip hands: {player.hands}")

    # back to the one-handed weapon
    player.equip_weapon(shotgun, 0)
    print(f"Back to one-handed equip inventory: {player.inventory}")
    print(f"Back to one-handed equip hands: {player.hands}")