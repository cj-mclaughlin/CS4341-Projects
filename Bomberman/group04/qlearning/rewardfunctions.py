import os, sys
import math

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import actions
from featurefunctions import post_action_location

# Reward constant values
R_LIVING = 0
R_EXITED = 10
R_KILLED = -50

# Checking tiles adjacent
DX = [0, 1, 1, 1, 0, -1, -1, -1]
DY = [-1, -1, 0, 1, 1, 1, 0, -1]


# Reward component functions

# Gives a negative reward no matter what has happened (cost of living)
def cost_of_living(state, action, character):
    """Return a constant, negative reward that represents the cost of living"""
    return R_LIVING


# Gives a very negative reward if the agent is killed by bomb or monster
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
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
# PARAM[list(Event)] events: the events that transpired in the last step
def won(events):
    """Earn positive reward if agent has won the game"""
    # Iterate over events to check for win
    for ev in events:
        if ev.tpe == Event.CHARACTER_FOUND_EXIT:
            # Reward for winning
            return R_WON
    
    # Reward for not winning
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
# PARAM[list(Event)] events: the events that transpired in the last step
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def reward(state, events, character):
    """Earn reward based on sum of every reward component"""
    total_reward = 0

    # Sum reward returned from every reward function
    total_reward += cost_of_living()
    total_reward += using_bomb(state)
    #total_reward += hit_walls(events)
    #total_reward += hit_monsters(events)
    total_reward += can_hit_walls(state)
    total_reward += can_hit_monsters(state)
    total_reward += dist_to_exit(state, character)
    total_reward += died(state, events)
    total_reward += won(events)
    
    return total_reward
