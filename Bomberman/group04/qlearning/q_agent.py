import sys
import math
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

from entity import CharacterEntity
from actions import Action, ActionDirections
import featurefunctions as fn
from game import Game
import pygame


# Note: signiture for CharacterEntity constructor: def __init__(self, name, avatar, x, y):


# TODO verify if working :)
class QAgent(CharacterEntity):
    def __init__(self, name, avatar, x, y):
        #TODO don't hardcode
        self.weights = [1,1,1,1,1]
        self.feature_functions = fn.feature_functions
        super().__init__(name, avatar, x, y)

    def evaluate_move(self, state, action):
        move_util = 0
        print("Evaluating action {}".format(action))
        for i in range(len(self.weights)):
            print("fn {} yielding {}*{}".format(i, self.weights[i], self.feature_functions[i](state, action, self)))
            move_util += self.weights[i] * self.feature_functions[i](state, action, self)
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
             if super().evaluate_move(world, a) > best_action_val and self.valid_action(world, a):
                 best_action = a
                 best_action_val = super().evaluate_move(world, a)
        if best_action == Action.BOMB:
            self.place_bomb()
        else:
            direction = ActionDirections[best_action]
            self.move(direction[0], direction[1])
            
    def valid_action(self, world, action):
        direction = ActionDirections[action]
        if (self.x + direction[0] < 0 or self.y + direction[1] < 0):
            return False
        return True


class ExplorationAgent(QAgent):
    def __init__(self, name, avatar, x, y):
        super().__init__(name, avatar, x, y)
        self.alpha = 1
        self.generation = 1
        self.weights_filename = "bomberman_weights.txt"
       
    # Connor
    # TODO
    def update_alpha(self):
        pass
    
    # Connor
    # TODO
    def update_weights(self, reward):
        pass