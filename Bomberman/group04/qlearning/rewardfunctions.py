import os, sys
import math

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import actions
from events import Event
from featurefunctions import manhattan_dist

import pdb

# Reward constant values
R_LIVING = -1
R_BOMB_PLACED = -5
R_WALL_IN_RANGE = 6
R_WALL_HIT = 10
R_MONSTER_IN_RANGE = 50
R_MONSTER_HIT = 200
R_NEAR_EXIT = 8  # Reward when on top of exit
R_DIED = -1000
R_WON = 1000


# Reward component functions

# Gives a negative reward no matter what has happened (cost of living)
def cost_of_living():
    """Return a constant, negative reward that represents the cost of living"""
    return R_LIVING


# Gives a negative reward if using the bomb to prevent overuse
# PARAM[SensedWorld] state: the current state of the map
def using_bomb(state):
    """Return a constant, negative reward if bomb is out"""
    if len(state.bombs) > 0:
        return R_BOMB_PLACED
    
    # No bomb
    return 0


# Rewards the agent for successfully blowing up one or more walls
# PARAM[list(Event)] events: the events that transpired in the last step
def hit_walls(events):
    """Earn reward for every destroyed wall"""
    walls_hit = 0

    # Iterate over events to count how many walls were hit
    for ev in events:
        if ev.tpe == Event.BOMB_HIT_WALL:
            walls_hit += 1
    
    return R_WALL_HIT * walls_hit


# Rewards the agent for successfully killing one or more monsters
# PARAM[list(Event)] events: the events that transpired in the last step
def hit_monsters(events):
    """Earn reward for every killed monster"""
    monsters_hit = 0

    # Iterate over events to count how many monsters were hit
    for ev in events:
        if ev.tpe == Event.BOMB_HIT_MONSTER:
            monsters_hit += 1
    
    return R_MONSTER_HIT * monsters_hit


# Rewards the agent for every wall in range of a bomb explosion
# PARAM[SensedWorld] state: the current state of the map
def can_hit_walls(state):
    """Earn reward for every hittable wall"""
    hittable_walls = 0
    dist = state.expl_range

    # Iterate over every bomb
    for bomb in state.bombs.values():
        # Check for walls
        # +x direction
        for i in range(1, dist + 1):
            x, y = bomb.x + i, bomb.y
            if valid_loc(state, x, y) and state.wall_at(x, y):
                hittable_walls += 1
                break
        # -x direction
        for i in range(1, dist + 1):
            x, y = bomb.x - i, bomb.y
            if valid_loc(state, x, y) and state.wall_at(x, y):
                hittable_walls += 1
                break
        # +y direction
        for i in range(1, dist + 1):
            x, y = bomb.x, bomb.y + i
            if valid_loc(state, x, y) and state.wall_at(x, y):
                hittable_walls += 1
                break
        # -y direction
        for i in range(1, dist + 1):
            x, y = bomb.x, bomb.y - i
            if valid_loc(state, x, y) and state.wall_at(x, y):
                hittable_walls += 1
                break
    
    return R_WALL_IN_RANGE * hittable_walls


# Rewards the agent for every monster in range of a bomb explosion
# PARAM[SensedWorld] state: the current state of the map
def can_hit_monsters(state):
    hittable_monsters = 0
    dist = state.expl_range

    # Iterate over every bomb
    for bomb in state.bombs.values():
        # Check for walls
        # +x direction
        for i in range(1, dist + 1):
            x, y = bomb.x + i, bomb.y
            if valid_loc(state, x, y) and state.monsters_at(x, y):
                hittable_monsters += 1
                break
        # -x direction
        for i in range(1, dist + 1):
            x, y = bomb.x - i, bomb.y
            if valid_loc(state, x, y) and state.monsters_at(x, y):
                hittable_monsters += 1
                break
        # +y direction
        for i in range(1, dist + 1):
            x, y = bomb.x, bomb.y + i
            if valid_loc(state, x, y) and state.monsters_at(x, y):
                hittable_monsters += 1
                break
        # -y direction
        for i in range(1, dist + 1):
            x, y = bomb.x, bomb.y - i
            if valid_loc(state, x, y) and state.monsters_at(x, y):
                hittable_monsters += 1
                break
    
    return R_MONSTER_IN_RANGE * hittable_monsters


# Gives a reward based on how far the agent is from the exit
# PARAM[SensedWorld] state: the current state of the map
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def dist_to_exit(state, character):
    """Earn reward based on closeness to exit"""
    max_manhattan_dist = 27
    closeness = 1 - (manhattan_dist(character.x, character.y, *state.exitcell) / max_manhattan_dist)
    return R_NEAR_EXIT * closeness
    
    # No character found
    return 0



# Gives a very negative reward if the agent is killed or runs out of time
# PARAM[SensedWorld] state: the current state of the map
# PARAM[list(Event)] events: the events that transpired in the last step
def died(state, events):
    """Earn negative reward if agent is killed or out of time"""
    # Iterate over events to check for death
    for ev in events:
        if ev.tpe == Event.CHARACTER_KILLED_BY_MONSTER or ev.tpe == Event.BOMB_HIT_CHARACTER:
            # Reward for monster or explosive death
            return R_DIED

    if state.time == 1:
        # Reward for out of time death
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
    total_reward += hit_walls(events)
    total_reward += hit_monsters(events)
    total_reward += can_hit_walls(state)
    total_reward += can_hit_monsters(state)
    total_reward += dist_to_exit(state, character)
    total_reward += died(state, events)
    total_reward += won(events)
    
    return total_reward
