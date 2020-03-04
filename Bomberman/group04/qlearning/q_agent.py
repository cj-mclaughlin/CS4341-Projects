import sys
import math
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

from entity import CharacterEntity
from actions import Action, ActionDirections
import featurefunctions as fn
from game import Game
import pygame
import random


# Note: signiture for CharacterEntity constructor: def __init__(self, name, avatar, x, y):


class QAgent(CharacterEntity):
    def __init__(self, name, avatar, x, y):
        #TODO don't hardcode
        self.weights = [1,1,1,1,1]
        self.feature_functions = fn.feature_functions
        super().__init__(name, avatar, x, y)

    def evaluate_move(self, state, action):
        move_util = 0
        #print("Evaluating action {}".format(action))
        for i in range(len(self.weights)):
            #print("fn {} yielding {}*{}".format(i, self.weights[i], self.feature_functions[i](state, action, self)))
            move_util += self.weights[i] * self.feature_functions[i](state, action, self)
        return move_util
    
    def valid_action(self, world, action):
        direction = ActionDirections[action]
        if (self.x + direction[0] < 0 or self.y + direction[1] < 0):
            return False
        return True
    
    # Determine the best action the agent can take
    # PARAM [World] state: the current state that the agent is in
    # RETURN [Action]: the best action that the agent can take 
    def determine_best_action(self, state):
        """Find the best available move"""
        bomb = False
        best_action = None
        best_action_val = -math.inf
        for a in Action:
             if self.valid_action(state, a) and self.evaluate_move(state, a) > best_action_val:
                 best_action = a
                 best_action_val = self.evaluate_move(state, a)
        return best_action

class ExploitationAgent(QAgent):
    def __init__(self, name, avatar, x, y):
        super().__init__(name, avatar, x, y)
        
    def set_weights(self, weights):
        self.weights = weights
    
    def do(self, world):
        """Find and perform best available move"""
        best_action = self.determine_best_action(world)
        if best_action == Action.BOMB:
            self.place_bomb()
        else:
            direction = ActionDirections[best_action]
            self.move(direction[0], direction[1])
         

class ExplorationAgent(QAgent):
    def __init__(self, name, avatar, x, y):
        super().__init__(name, avatar, x, y)
        self.inital_alpha = 1
        self.alpha = self.inital_alpha
        self.generation = 1
        self.weights_filename = "bomberman_weights.txt"
        self.epsilon = 1
        self.num_actions_completed = 0
        self.k = .1
        self.last_action = Action.STILL
       
    # Update alpha with exponential decay
    # PARAM[float] k: scale factor for exponential decay
    def update_alpha(self, k=0.1):
        self.alpha = self.inital_alpha * math.exp(-k*self.generation)
    
    # Update weights after taking a step in world
    # PARAM[float] reward: reward recieved for last action in world
    # PARAM[SensedWorld] current_state: the state of the world
    # PARAM[float] current_utility: sum utility evaluaton for (current_state, current_action)
    # PARAM[SensedWorld] next_state: the state of the world after action
    # PARAM[Action] next_action: the best action after entering next state (argmax)
    # PARAM[float] discount: discounting rate
    def update_weights(self, reward, current_state, next_state, discount=0.9):
        current_action = self.last_action
        current_utility = self.evaluate_move(current_state, current_action)
        next_action = self.determine_best_action(next_state)
        # delta = r + v(max(a')(Q(s',a'))) - Q(s,a)
        delta = (reward + (discount*self.evaluate_move(next_state, next_action))) - current_utility
        # wi = wi + a*delta*fi(s,a)
        for w_idx in range(len(self.weights)):
            self.weights[w_idx] = self.weights[w_idx] + self.alpha*delta*self.feature_functions[w_idx](current_state, current_action, self)
        # update alpha
        self.update_alpha() # TODO move
        
        # update generation
        self.generation += 1 # TODO move

    def do(self, world):
        x = random.random()
        if(x < self.epsilon):
            best_action = self.generate_random_action()
        else:
            best_action = self.determine_best_action(world)
        
        self.last_action = best_action
        
        if best_action == Action.BOMB:
            self.place_bomb()
        else:
            direction = ActionDirections[best_action]
            self.move(direction[0], direction[1])
        self.num_actions_completed += 1

    def update_epsilon(self):
        self.epsilon = math.exp(-self.k * self.num_actions_completed)

    def generate_random_action(self):
        action_num = random.randint(1,6)
        action = Action(action_num)
        return action