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

# Run!
g.go(1)
