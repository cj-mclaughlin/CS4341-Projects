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
g.add_monster(SelfPreservingMonster("aggressive", # name
                                    "A",          # avatar
                                    3, 13,        # position
                                    2             # detection range
))

# TODO finalize weights
agent = q_agent.Player("me", "C", 0, 0)
g.add_character(agent)
# final_weights = [73.0, -186.2, 2.0, -59.9, 15.8]
# agent.set_weights(final_weights)
agent.set_safe_threshold(10)

# Run!
g.go(1)
