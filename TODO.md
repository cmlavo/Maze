board.move_player(player)
player.ditch_weapon(weapon)
GLOBAL_LOG_FILE
GLOBAL_VERBOSE

StateMachines:
    Three classes, each inherit from the class StateMachine:
    - PlayerStateMachine
    - MonsterStateMachine
    - GuardianStateMachine

    These are classes which decide what an entity does when faced with a decision. For monsters and guardians, there is only one decision: "On a given turn of combat, who do I attack?". Monsters have an equal chance of attacking any other combattant. Guardians will never attack another Guardian.

    For players, there are many decisions to make:
    - "Which gun do I equip?"
    - "Which guns should I keep, and which should I discard from my inventory?"
    - "Which armour do I equip?"
    - "Do I risk fighting a monster, or do I stay away?"
    - "Which monster do I attack this turn of combat?"
    - "Do I risk fighting a stronger enemy in exchange for a chance at more treasure?"
    - "Should I flee from the current fight?"
    - "Should I trigger a time bomb now?"
    - "Should I use a healing item?"
    - "On which weapon should I use this weapon upgrade?"
    - "Which Neural Implant should I choose?"
    - "Should I expend my exit map and go to the exit now?"
    - "Should I expend my magnetic card to open this secret door?"
    - "Should I attack this player?"
    - "Should I ask this player for a cease-fire?"
    - "Should I accept this player's cease-fire?"
    - "Should I pick an encounter card from the A (high-risk), B (low-risk), or C (uninterested) pile?"

    All these decisions are made by sampling randomly from a distribution which is affected by the following personality parameters [0-1]:
    - Aggressiveness: how likely someone is to act aggressively in combat
    - Greediness: how likely someone is to do something risky for more resources
    - Cautiousness: how likely someone is to avoid risk, or escape a dangerous situation
    - Strategicness: how likely someone is to take advantage of someone else's bad situation for personal gain
    - Agreeableness: how likely someone is to be cooperative with another player
    - Expendability: someone's propensity for spending finite resources
    - Unpredictability: increases the variance of the distribution
    - Influencability: how much someone's circumstances affect their decision
    These personality parameters' values define the state of the player state machine.

    These factors are also influenced by the player's circumstances, namely:
    - Current life points
    - Level
    - Amount of resources in inventory (healing items, magnetic cards, weapon charges)
    - Strength and number of enemies in combat
    - Strength of their equipped items