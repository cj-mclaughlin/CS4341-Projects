import os, sys
import math

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import actions
from featurefunctions import valid_location, post_action_location

# Reward constant values
R_LIVING = -1
R_PER_WALL = 5
R_PER_ENEMY = 100
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

    # Reward amount for each blown up wall
    for explosion in state.explosions.values():
        if state.wall_at(explosion.x, explosion.y):
            walls_hit += 1
    
    return R_PER_WALL * walls_hit


# Function that rewards the agent for successfully killing one or more monsters
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def kill_monsters(state, action, character):
    """Earn reward for every killed monster"""
    return 0


# Function that gives a very negative reward if the action kills the agent
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def die(state, action, character):
    """Earn negative reward if action kills the agent in this state"""
    return 0


# Function that gives a very positive reward if the action results in a win for the agent
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def win(state, action, character):
    """Earn positive reward if action causes the agent to win the game"""
    return 0


reward_functions = [
    cost_of_living,
    blow_up_walls,
    kill_monsters,
    die,
    win
]    


# Calculate the total reward as a sum of each component with the given state/action pair
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def reward(state, action, character):
    """Earn reward based on sum of every reward component"""
    total_reward = 0

    # Sum reward returned from every reward function
    for reward_function in reward_functions:
        total_reward += reward_function(state, action)
    
    return total_reward
