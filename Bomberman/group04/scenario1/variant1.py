# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
from game import Game

# # Original Imports from Starter Code
# sys.path.insert(1, '../group04')
from testcharacter import TestCharacter
from interactivecharacter import InteractiveCharacter

# Q-Learning Agent
sys.path.insert(1, '../group04')
from qlearning import q_agent

# Create the game
g = Game.fromfile('map.txt')

# TODO finalize weights
agent = q_agent.ExploitationAgent("me", "C", 0, 0)
# final_weights = [...]
# agent.set_weights(final_weights)
g.add_character(agent)

# Run!
g.go()
