# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
from game import Game

# sys.path.insert(1, '../group04')
from testcharacter import TestCharacter
from interactivecharacter import InteractiveCharacter

# Q-Learning Agent
from qlearning import q_agent

# Create the game
g = Game.fromfile('map.txt')

# TODO Add your character
agent = q_agent.Player("me", "C", 0, 0)
g.add_character(agent)
# final_weights = [29.7, -103.8, 55.1, -50.9, 3.0]
# agent.set_weights(final_weights)

# Run!
g.go(1)
