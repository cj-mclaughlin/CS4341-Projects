import sys
import math
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

from entity import CharacterEntity
from actions import Action, ActionDirections
import featurefunctions as fn


# Note: signiture for CharacterEntity constructor: def __init__(self, name, avatar, x, y):



# TODO verify if working :)
class QAgent(CharacterEntity):
    def __init__(self, name, avatar, x, y):
        self.weights = [1, 1, 1, 1]
        self.feature_functions = [fn.dist_to_exit, fn.dist_to_monster, fn.wall_in_bomb_range, fn.bomb_danger_zone]
        super().__init__(name, avatar, x, y)

    def evaluate_move(self, state, action):
        move_util = 0
        for i in range(len(self.weights)):
            print("action {}, {},{}".format(i, self.weights[i], self.feature_functions[i](state, action)))
            move_util += self.weights[i] * self.feature_functions[i](state, action)
        return move_util


class ExploitationAgent(QAgent):
    def __init__(self, name, avatar, x, y):
        super().__init__(name, avatar, x, y)
        
    def do(self, world):
        """Find and perform best available move"""
        bomb = False
        best_action = None
        best_action_val = -math.inf
        for a in Action:
             if super().evaluate_move(world, a) > best_action_val:
                 best_action = a
                 best_action_val = super().evaluate_move(world, a)
        if best_action == Action.BOMB:
            self.place_bomb()
        else:
            direction = ActionDirections[best_action]
            self.move(direction[0], direction[1])


# Sanity Check

# if __name__ == "__main__":
#     print("Imports passed")
    
    