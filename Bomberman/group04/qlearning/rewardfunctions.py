import os, sys
import math

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import actions
from featurefunctions import post_action_location

# Reward constant values
R_LIVING = 0 # TODO test with small cost of living
R_BREAK_DOWN = 15
R_EXITED = 15
R_DIED = -50

# Checking tiles adjacent
DX = [0, 1, 1, 1, 0, -1, -1, -1]
DY = [-1, -1, 0, 1, 1, 1, 0, -1]


# Reward component functions

# Gives a negative reward no matter what has happened (cost of living)
# RETURN[int] : a small negative amount to urge the agent onward
def cost_of_living():
    """Return a constant, negative reward that represents the cost of living"""
    return R_LIVING


# Gives a positive reward for placing a bomb where it can break a block to the south
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
# RETURN[int] : positive reward for aiming a bomb to the south, 0 otherwise
def break_down(state, action, character):
    """Earn reward if agent places a bomb to destory a southern block"""
    if action == actions.Action.BOMB:
        for i in range(1, state.expl_range + 1):
            expl_x, expl_y = character.x, character.y + i
            if valid_loc(state, expl_x, expl_y) and state.wall_at(expl_x, expl_y):
                # Wall found in south direction
                return R_BREAK_DOWN
    # No bomb or bomb misses southern wall
    return 0


# Gives a very negative reward if the agent is killed by bomb or monster
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
# RETURN[int] : very negative reward if the agent will die with this action, 0 otherwise
def died(state, action, character):
    """Earn negative reward if agent is killed"""
    new_x, new_y = post_action_location(state, action, character)

    # Check for explosive death
    if state.explosion_at(new_x, new_y):
        return R_DIED
    
    # If moving within one step of a monster, aggressive monsters will kill
    for i in range(len(DX)):
        if state.monsters_at(new_x + DX[i], new_y + DY[i]):
            return R_DIED
    
    # If moving into bomb range with one or two steps on bomb timer, also certain death
    for bomb in state.bombs.values():
        if bomb.timer <= 1:
            if new_x == bomb.x and abs(new_y - bomb.y) <= state.expl_range:
                return R_DIED
            if new_y == bomb.y and abs(new_x - bomb.x) <= state.expl_range:
                return R_DIED

    # Reward for survival
    return 0


# Gives a very positive reward if the agent has won
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
# RETURN[int] : positive reward for reaching exit, 0 otherwise
def exited(state, action, character):
    """Earn positive reward if agent has reached the exit"""
    new_loc = post_action_location(state, action, character)
    if state.exitcell == new_loc:
        return R_EXITED
    
    # Reward for not exiting
    return 0


# Check that the new position is a valid move
# PARAM[SensedWorld] state: the state of the current board
# PARAM[int] x: the x coordinate of the position to check
# PARAM[int] y: the y coordinate of the position to check
# RETURN[boolean] : whether the location is on the grid
def valid_loc(state, x, y):
    """Check if we are going out of bounds"""
    # Check that there is no wall in the new position
    if 0 <= x < state.width() and 0 <= y < state.height():
        return True
    
    # Out of bounds
    return False


# Get the reward value for a given state and events
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
# RETURN[int] : the total reward based on various reward components
def reward(state, action, character):
    """Earn reward based on sum of every reward component"""
    total_reward = 0

    # Sum reward returned from every reward function
    total_reward += cost_of_living()
    total_reward += break_down(state, action, character)
    total_reward += died(state, action, character)
    total_reward += exited(state, action, character)
    
    return total_reward
