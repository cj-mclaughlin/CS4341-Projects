# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
import random
from game import Game
from monsters.selfpreserving_monster import SelfPreservingMonster

# Q-Learning Agent
sys.path.insert(1, '../group04')
from qlearning import q_agent

# Create the game
#random.seed(123) # TODO Change this if you want different random choices
g = Game.fromfile('map.txt')
g.add_monster(SelfPreservingMonster("selfpreserving", # name
                                    "S",              # avatar
                                    3, 9,             # position
                                    1                 # detection range
))

# TODO finalize weights
agent = q_agent.Player("me", "C", 0, 0)
g.add_character(agent)

# Run!
g.go(1)
