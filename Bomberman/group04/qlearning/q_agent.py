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

import rewardfunctions
import math
import collections

from queue import PriorityQueue

# Note: signiture for CharacterEntity constructor: def __init__(self, name, avatar, x, y):


class QAgent(CharacterEntity):
    def __init__(self, name, avatar, x, y):
        self.feature_functions = fn.feature_functions
        self.weights = [1 * len(self.feature_functions)] # TODO fix initialization
        super().__init__(name, avatar, x, y)

    def set_weights(self, weights):
        self.weights = weights

    def evaluate_move(self, state, action):
        move_util = 0
        #print("Evaluating action {}".format(action))
        for i in range(len(self.weights)):
            #print("fn {} ({}*{}) yielding {}".format(i, self.weights[i], self.feature_functions[i](state, action, self), self.weights[i] * self.feature_functions[i](state, action, self)))
            move_util += self.weights[i] * self.feature_functions[i](state, action, self)
        return move_util
    
    def valid_action(self, world, action):
        if action is None:
            return False
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
        best_action = Action.STILL
        best_action_val = -math.inf
        for a in Action:
            #print("{} value {}".format(a, self.evaluate_move(state, a)))
            if self.valid_action(state, a) and self.evaluate_move(state, a) > best_action_val:
                best_action = a
                best_action_val = self.evaluate_move(state, a)
        return best_action

class Player(QAgent):
    
    def is_safe(self, state, threshold = 5):
        best_path_vec = self.find_best_path_vector(state)
        closest_monster_dist = self.dist_to_nearest_monster(state, best_path_vec) 
        return closest_monster_dist > threshold, best_path_vec

    def should_place_bomb(self, state, best_next_move_vec):
        #No possible moves from pathplanning search
        return best_next_move_vec == None

    def do(self, world):
        is_safe, best_path_vec = self.is_safe(world)
        if(is_safe):
            if(self.should_place_bomb(world, best_path_vec)):
                self.place_bomb()
            else:
                #Make move to best postition based on best path
                self.move(best_path_vec[0], best_path_vec[1])
        else:
            best_action = self.determine_best_action(world)
            if best_action == Action.BOMB:
                self.place_bomb()
            else:
                direction = ActionDirections[best_action]
                self.move(direction[0], direction[1])
                pass

    #Finds the best 
    def find_best_path_vector(self, state):
        loc = (self.x, self.y)
        return self.A_star(state, loc, state.exitcell)

    def dist_to_nearest_monster(self, state, movement_vec):
        """Check if we are getting closer/further from a monster"""
        search_radius = 5
        new_x, new_y = movement_vec
        monsters = self.find_monsters(state)
        
        if monsters is None:
            return 0
        
        else:
            closest_monster_dist = math.inf
            for m in monsters:
                monster_dist = self.manhattan_dist(new_x, new_y, m[0], m[1])
                if monster_dist < closest_monster_dist:
                    closest_monster_dist = monster_dist
            return closest_monster_dist

    # Calculates the manhattan distance between two points
    # PARAM[int] x1: X value of the first point
    # PARAM[int] y1: Y value of the first point
    # PARAM[int] x2: X value of the second point
    # PARAM[int] y2: Y value of the second point
    # RETURN[int] : the manhattan distance between two points
    def manhattan_dist(self, x1, y1, x2, y2):
        """Manhattan distance"""
        return abs(x1-x2) + abs(y1-y2)

    # Calculates the Euclidean distance between two points
    # PARAM[int] x1: X value of the first point
    # PARAM[int] y1: Y value of the first point
    # PARAM[int] x2: X value of the second point
    # PARAM[int] y2: Y value of the second point
    # RETURN[int] : the Euclidean distance between two points
    def euclidean_dist(self, x1,y1, x2, y2):
        return math.sqrt(pow(x2-x1,2) + pow(y2-y1,2))

    # Helper method to find monsters
    # PARAM[SensedWorld] state: the current state of the map
    def find_monsters(self, state):
        """Returns list of coordinates with monsters"""
        monsters = []
        for w in range(state.width()):
            for h in range(state.height()):
                monster = state.monsters_at(w, h)
                if monster is not None:
                    monsters.append((w,h))
        return monsters

    # BFS for optimal path
    # PARAM[SensedWorld] state: the current state of the board
    # PARAM[tuple(int, int)] start: starting coordinates
    # PARAM[tuple(int, int)] goal: goal coordinates
    def bfs(self, state, start, goal):
        queue = collections.deque([[start]])
        seen = set([start])

        # perform bfs, leaving us with path to exit
        exit_found = False
        while queue:
            path = queue.popleft()
            x, y = path[-1]

            # check if we have reached exit
            if x == goal[0] and y == goal[1]:
                exit_found = True
                break

            # Add neighbors to queue
            for x2, y2 in ((x+1,y), (x-1,y), (x,y+1), (x,y-1), (x+1, y+1), (x+1, y-1), (x-1, y-1), (x-1, y+1)):
                if 0 <= x2 < state.width() and 0 <= y2 < state.height() and not state.wall_at(x2, y2) and (x2, y2) not in seen:
                    queue.append(path + [(x2, y2)])
                    seen.add((x2, y2))

        if exit_found:
            return path[1][0] - start[0], path[1][1] - start[1]
        
        # No path
        return None
    
    def A_star(self, state, start, goal):
        def h(state, x, y):
            return 11 if(state.wall_at(x,y)) else 1
        
        # @dataclass(order = True)
        # class prioritized_item:
        #     priority: int
        #     item: Any=field(compare=False)

        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0
        
        while(not frontier.empty()):
            current = frontier.get()
            x,y = current[0], current[1]
            if(current == goal):
                break

            # Add neighbors to queue
            for x2, y2 in ((x+1,y), (x-1,y), (x,y+1), (x,y-1), (x+1, y+1), (x+1, y-1), (x-1, y-1), (x-1, y+1)):
                
                #Check that the value is a valid move
                if 0 <= x2 < state.width() and 0 <= y2 < state.height():
                    new_cost = cost_so_far[(x,y)] + 1 + h(state, x2, y2)
                    if(y2 ==4): print(x2, y2, new_cost)
                    if((x2,y2) not in cost_so_far or new_cost < cost_so_far[(x2,y2)]):
                        cost_so_far[(x2,y2)] = new_cost
                        priority = new_cost
                        frontier.put((x2,y2),priority)
                        came_from[(x2,y2)] = current

        #Loop back and find optimal move vector
        cur_coor = current
        while(came_from[cur_coor] != start):
            print(cur_coor)
            cur_coor = came_from[cur_coor]
        
        return (cur_coor[0] - start[0], cur_coor[1] - start[1])

class ExploitationAgent(QAgent):
    def __init__(self, name, avatar, x, y):
        super().__init__(name, avatar, x, y)
    
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
        self.alpha = 0.25
        self.generation = 1
        self.weights_filename = "bomberman_weights.txt"
        self.epsilon = 0.8
        self.epsilon_decrement = 0.025 # TODO what this should be
        self.last_action = Action.STILL
            
    # Update weights after taking a step in world
    # PARAM[float] reward: reward recieved for last action in world
    # PARAM[SensedWorld] current_state: the state of the world
    # PARAM[float] current_utility: sum utility evaluaton for (current_state, current_action)
    # PARAM[SensedWorld] next_state: the state of the world after action
    # PARAM[Action] next_action: the best action after entering next state (argmax)
    # PARAM[float] discount: discounting rate
    def update_weights(self, reward_fn, current_state, next_state, discount=0.9):
        current_action = self.last_action
        reward = rewardfunctions.reward(current_state, current_action, self)
        #print("reward in update_weights evaluating to {}".format(reward))
        current_utility = self.evaluate_move(current_state, current_action)
        next_action = self.determine_best_action(next_state)
        # delta = r + v(max(a')(Q(s',a'))) - Q(s,a)
        delta = (reward + (discount*self.evaluate_move(next_state, next_action))) - current_utility
        #print("delta value found to be {}".format(delta))
        # wi = wi + a*delta*fi(s,a)
        for w_idx in range(len(self.weights)):
            #print("weight {}, val {}, changing by {}".format(w_idx, self.weights[w_idx], self.alpha*delta*self.feature_functions[w_idx](current_state, current_action, self)))
            self.weights[w_idx] = self.weights[w_idx] + self.alpha*delta*self.feature_functions[w_idx](current_state, current_action, self)

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

    def update_epsilon(self):
        self.epsilon -= self.epsilon_decrement

    def generate_random_action(self):
        action_num = random.randint(1,10)
        action = Action(action_num)
        return action