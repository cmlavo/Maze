# add parent folder to path so that src imports work
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.players import Player, Monster, Humanoid, Cyborg, Wartech
from src.items import Weapon, Item, WeaponUpgrades, Armour
from src.inventory import Inventory

# initialise two players
Player1 = Humanoid("Humanoid")
Player2 = Cyborg("Cyborg")
Player3 = Wartech("Wartech")
Player4 = Monster("Monster")

print(f"\n--- Testing unarmed attacks ---")

# humanoid attacks monster unarmed
print(f"\n{Player1.name} attacks {Player4.name} unarmed:")
print(f"Hit: {Player1.attack(Player4)}")
print(f"{Player4.name} health: {Player4.life_points}/{Player4._max_life_points}")

# monster attacks humanoid unarmed
print(f"\n{Player4.name} attacks {Player1.name} unarmed:")
print(f"Hit: {Player4.attack(Player1)}")
print(f"{Player1.name} health: {Player1.life_points}/{Player1._max_life_points}")

# wartech attacks cyborg unarmed
print(f"\n{Player3.name} attacks {Player2.name} unarmed:")
print(f"Hit: {Player3.attack(Player2)}")
print(f"{Player2.name} health: {Player2.life_points}/{Player2._max_life_points}")

# cyborg attacks wartech unarmed
print(f"\n{Player2.name} attacks {Player3.name} unarmed:")
print(f"Hit: {Player2.attack(Player3)}")
print(f"{Player3.name} health: {Player3.life_points}/{Player3._max_life_points}")

# now equip weapons to players
Player1.reset_equipment()
Player2.reset_equipment()
Player3.reset_equipment()
Player4.reset_equipment()

print(f"\n--- Testing armed attacks ---")

# humanoid shoots monster 
print(f"\n{Player1.name} shoots {Player4.name}:")
print(f"Hit: {Player1.attack(Player4)}")
print(f"{Player4.name} health: {Player4.life_points}/{Player4._max_life_points}")

# monster shoots humanoid 
print(f"\n{Player4.name} shoots {Player1.name}:")
print(f"Hit: {Player4.attack(Player1)}")
print(f"{Player1.name} health: {Player1.life_points}/{Player1._max_life_points}")

# wartech shoots cyborg
print(f"\n{Player3.name} shoots {Player2.name}:")
print(f"Hit: {Player3.attack(Player2)}")
print(f"{Player2.name} health: {Player2.life_points}/{Player2._max_life_points}")

# cyborg shoots wartech 
print(f"\n{Player2.name} shoots {Player3.name}:")
print(f"Hit: {Player2.attack(Player3)}")
print(f"{Player3.name} health: {Player3.life_points}/{Player3._max_life_points}")
