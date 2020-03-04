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
        self.inital_alpha = 1
        self.alpha = self.inital_alpha
        self.generation = 1
        self.weights_filename = "bomberman_weights.txt"
       
    # Update alpha with exponential decay
    # PARAM[float] k: scale factor for exponential decay
    def update_alpha(self, k=0.1):
        self.alpha = self.inital_alpha * math.exp(-k*self.generation)
    
    # Update weights after taking a step in world
    # PARAM[float] reward: reward recieved for last action in world
    # PARAM[SensedWorld] current_state: the state of the world
    # PARAM[Action] current_action: the action to evaluate
    # PARAM[float] current_utility: sum utility evaluaton for (current_state, current_action)
    # PARAM[SensedWorld] next_state: the state of the world after action
    # PARAM[Action] next_action: the best action after entering next state (argmax)
    # PARAM[float] discount: discounting rate
    def update_weights(self, reward, current_state, current_action, current_utility, next_state, next_action, discount=0.9):
        # delta = r + v(max(a')(Q(s',a'))) - Q(s,a)
        delta = (reward + (discount*self.evaluate_move(next_state, next_action))) - current_utility
        # wi = wi + a*delta*fi(s,a)
        for w_idx in range(len(self.weights)):
            self.weights[w_idx] = self.weights[w_idx] + self.alpha*delta*self.feature_functions[w_idx](current_state, current_action)
        # update alpha
        self.update_alpha()
        
        # update generation
        self.generation += 1