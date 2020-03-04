import os, sys
import math

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import actions
from featurefunctions import post_action_location

# Reward constant values
R_LIVING = -1
R_PER_WALL = 5
R_PER_MONSTER = 100
R_DIE = -1000
R_WIN = 1000


# Reward component functions

# Function that gives a negative reward no matter what action is taken (cost of living)
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def cost_of_living(state, action, character):
    """Return a constant, negative reward that represents the cost of living"""
    return R_LIVING


# Function that rewards the agent for successfully blowing up one or more walls
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def blow_up_walls(state, action, character):
    """Earn reward for every destroyed wall"""
    walls_hit = 0

    # Iterate over existing explosions to see if they hit walls
    for explosion in state.explosions.values():
        if state.wall_at(explosion.x, explosion.y):
            walls_hit += 1
    
    return R_PER_WALL * walls_hit


# TODO: Monsters are only rewarded if hit on the frame of the blast, not if they wander into
# the explosion afterwards. Maybe reward can be earned if monster is just one step away from
# death, as their moves cannot be predicted.

# Function that rewards the agent for successfully killing one or more monsters
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def kill_monsters(state, action, character):
    """Earn reward for every killed monster"""
    monsters_hit = 0

    # Iterate over bombs and monsters to see if they will hit enemies
    for bomb in state.bombs.values():
        # Reward for monsters moving into bomb blast zone
        # Bombs blast before agents move, so being in range one frame before blasting causes death
        if bomb.timer <= 1:
            for monster_list in state.monsters.values():
                for monster in monster_list:
                    # Check if monster is in the x component of explosion
                    if (abs(monster.x - bomb.x) <= state.expl_range and monster.y == bomb.y):
                        monsters_hit += 1
                    # y component
                    elif (abs(monster.y - bomb.y) <= state.expl_range and monster.x == bomb.x):
                        monsters_hit += 1
    
    return R_PER_MONSTER * monsters_hit


# Function that gives a very negative reward if the action kills the agent
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def die(state, action, character):
    """Earn negative reward if action kills the agent in this state"""
    char_x, char_y = post_action_location(state, action, character)
    if state.monsters_at(char_x, char_y) or state.explosion_at(char_x, char_y):
        # Reward for moving into death
        return R_DIE

    if state.time == 1:
        # Reward for out of time death
        return R_DIE
    
    for bomb in state.bombs.values():
        # Reward for moving into bomb blast zone
        # Bombs blast before agents move, so being in range one frame before blasting causes death
        if bomb.timer <= 1:
            # Check if we are in the x component of explosion
            if (abs(char_x - bomb.x) <= state.expl_range and char_y == bomb.y):
                return R_DIE
            # y component
            elif (abs(char_y - bomb.y) <= state.expl_range and char_x == bomb.x):
                return R_DIE

    # Reward for survival
    return 0


# Function that gives a very positive reward if the action results in a win for the agent
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def win(state, action, character):
    """Earn positive reward if action causes the agent to win the game"""
    char_x, char_y = post_action_location(state, action, character)
    if state.exit_at(char_x, char_y):
        # Reward for winning
        return R_WIN
    
    # Reward for not winning
    return 0


# Get the reward value for a given state and action
# PARAM[SensedWorld] state: the current state of the map
# PARAM[list(Event)] events: the events that transpired with this action
def reward(state, events):
    """Earn reward based on sum of every reward component"""
    total_reward = 0

    # Sum reward returned from every reward function
    # total_reward += 
    
    return total_reward
