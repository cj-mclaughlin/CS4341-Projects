# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
import random
from game import Game
from monsters.stupid_monster import StupidMonster

# # Original Imports from Starter Code
# sys.path.insert(1, '../group04')
from testcharacter import TestCharacter
from interactivecharacter import InteractiveCharacter

# Q-Learning Agent
sys.path.insert(1, '../group04')
from qlearning import q_agent

# Create the game
#random.seed(123) # TODO Change this if you want different random choices
g = Game.fromfile('map.txt')
g.add_monster(StupidMonster("stupid", # name
                            "S",      # avatar
                            3, 9      # position
))

# TODO finalize weights
agent = q_agent.Player("me", "C", 0, 0)
g.add_character(agent)
# final_weights = [102.3, -181.6, 1.9, -52.9, 3.0]
# agent.set_weights(final_weights)
agent.safe_threshold = 8

# Run!
g.go(1)
