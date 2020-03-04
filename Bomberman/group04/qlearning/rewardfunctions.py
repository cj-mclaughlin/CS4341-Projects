import os, sys
import math

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import actions
from events import Event
from featurefunctions import post_action_location

# Reward constant values
R_LIVING = -1
R_PER_WALL = 5
R_PER_MONSTER = 100
R_DIED = -1000
R_WON = 1000


# Reward component functions

# Gives a negative reward no matter what has happened (cost of living)
def cost_of_living():
    """Return a constant, negative reward that represents the cost of living"""
    return R_LIVING


# Rewards the agent for successfully blowing up one or more walls
# PARAM[list(Event)] events: the events that transpired in the last step
def blew_up_walls(events):
    """Earn reward for every destroyed wall"""
    walls_hit = 0

    # Iterate over events to count how many walls were hit
    for ev in events:
        if ev.tpe == Event.BOMB_HIT_WALL:
            walls_hit += 1
    
    return R_PER_WALL * walls_hit


# TODO: Monsters are only rewarded if hit on the frame of the blast, not if they wander into
# the explosion afterwards. Maybe reward can be earned if monster is just one step away from
# death, as their moves cannot be predicted.

# Rewards the agent for successfully killing one or more monsters
# PARAM[list(Event)] events: the events that transpired in the last step
def killed_monsters(events):
    """Earn reward for every killed monster"""
    monsters_hit = 0

    # Iterate over events to count how many monsters were hit
    for ev in events:
        if ev.tpe == Event.BOMB_HIT_MONSTER:
            monsters_hit += 1
    
    return R_PER_MONSTER * monsters_hit


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


# Get the reward value for a given state and events
# PARAM[SensedWorld] state: the current state of the map
# PARAM[list(Event)] events: the events that transpired in the last step
def reward(state, events):
    """Earn reward based on sum of every reward component"""
    total_reward = 0

    # Sum reward returned from every reward function
    total_reward += cost_of_living()
    total_reward += blew_up_walls(events)
    total_reward += killed_monsters(events)
    total_reward += died(state, events)
    total_reward += won(events)
    
    return total_reward
