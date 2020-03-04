import os, sys
import math

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import actions
from featurefunctions import valid_location, manhattan_dist, post_action_location, find_bomb


# Reward component functions

# Function that gives a negative reward no matter what action is taken (cost of living)
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
def cost_of_living(state, action):
    """Return a constant, negative reward that represents the cost of living"""
    return -1


# Function that rewards the agent for successfully blowing up one or more walls
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
def blow_up_walls(state, action):
    """Earn reward for every destroyed wall"""
    return 0


# Function that rewards the agent for successfully killing one or more monsters
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
def kill_monsters(state, action):
    """Earn reward for every killed monster"""
    return 0


# Function that gives a very negative reward if the action kills the agent
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
def die(state, action):
    """Earn negative reward if action kills the agent in this state"""
    return 0


# Function that gives a very positive reward if the action results in a win for the agent
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
def win(state, action):
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
def reward(state, action):
    """Earn reward based on sum of every reward component"""
    total_reward = 0

    # Sum reward returned from every reward function
    for reward_function in reward_functions:
        total_reward += reward_function(state, action, character)
    
    return total_reward
