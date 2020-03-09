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
        self.weights =  [10.4 , -131.4   , -4.7 ,  -52.4  ,  16.2 ]  # angry boy
        #self.weights = [73.0, -186.2, 2.0, -59.9, 15.8]
        #self.weights =  [152.6,-175.5,18.7,-50.2,17.9] # one from overnight training
        #self.weights = [102.3, -181.6, 1.9, -52.9, 15.0]  # <--Outstanding move (scenario1)
        #self.weights = [73.0, -186.2, 2.0, -59.9, 15.8]  # <--Pretty good move (scenario2, all but v3)
        self.safe_threshold = 9
        super().__init__(name, avatar, x, y)

    # Sets the weights used for agent's intelligent behavior
    # PARAM[list(float)] weights: the weight values to use, in order of their features
    def set_weights(self, weights):
        """Set the weights to use with feature functions"""
        self.weights = weights
    
    # Sets the threshold distance for safety from monsters
    # PARAM[int] new_thresh: the new value for the threshold
    def set_safe_threshold(self, new_thresh):
        """Set the threshold for determining safety"""
        self.safe_threshold = new_thresh
    
    # Evaluate the utility of a given action in the given state
    # PARAM[SensedWorld] state: the state of the map to evaluate with
    # PARAM[Action] action: the action to evaluate
    # RETURN[float] : the utility of the given action
    def evaluate_move(self, state, action):
        """Calculate the utility of a given action"""
        move_util = 0
        for i in range(len(self.weights)):
            move_util += self.weights[i] * self.feature_functions[i](state, action, self)
        return move_util
    
    # Determine if the given action will do anything when executed
    # PARAM[SensedWorld] world: the current state of the map
    # PARAM[Action] action: the action to evaluate
    # RETURN[boolean] : True if the action can be performed, False otherwise
    def valid_action(self, world, action):
        """Determing if an action will do something when perfomed"""
        if action is None:
            return False
        # Check bomb
        if action is Action.BOMB:
            # If no bombs, action is good
            return len(world.bombs) == 0
        direction = ActionDirections[action]
        next_x = self.x + direction[0]
        next_y = self.y + direction[1]
        if 0 <= next_x < world.width() and 0 <= next_y < world.height() and not world.wall_at(next_x, next_y):
            return True
        return False
    
    # Determine the best action the agent can take
    # PARAM[SensedWorld] state: the current state that the agent is in
    # RETURN[Action]: the best action that the agent can take 
    def determine_best_action(self, state):
        """Find the best available move"""
        bomb = False
        best_action = Action.STILL
        best_action_val = -math.inf
        for a in Action:
            if self.valid_action(state, a) and self.evaluate_move(state, a) > best_action_val:
                best_action = a
                best_action_val = self.evaluate_move(state, a)
        return best_action


class Player(QAgent):
    
    # Determine if the given location is in range of a present or near future explosion
    # PARAM[SensedWorld] state: the current state of the world
    # PARAM[int] x: the x-coordinate to test
    # PARAM[int] y: the y-coordinate to test
    # RETURN[boolean] : True if the location is in danger of exploding, False otherwise
    def in_bomb_zone(self, state, x, y):
        """Check if location has or will soon have explosions"""
        bomb = None
        ticking_bomb, in_explosion_radius = False, False
        for b in state.bombs.values():
            bomb = b

        # Check if a bomb is active
        if bomb is not None:
            ticking_bomb = True

        # Checks for active bomb
        if (ticking_bomb and bomb.timer <= 1):
            # Check if we are in the x component of explosion
            if (abs(x - bomb.x) <= 4 and y == bomb.y):
                in_explosion_radius = True
            # Check y component
            elif (abs(y - bomb.y) <= 4 and x == bomb.x):
                in_explosion_radius = True
        
        if (in_explosion_radius or state.explosion_at(x, y)):
            return True
        
        else: 
            return False
    
    # Checks if we are in danger of a bomb or monster
    # PARAM[SensedWorld] state: the current state of the world
    # RETURN[boolean] : True if the agent is safe and may proceed to exit, False otherwise
    def is_safe(self, state):
        """Check if this state is safe for the agent"""
        best_path_vec = self.find_best_path_vector(state)
        if not self.monster_on_path(state):
            return not self.in_bomb_zone(state, self.x, self.y), best_path_vec
        closest_monster_dist = self.dist_to_nearest_monster(state)
        return not (closest_monster_dist < self.safe_threshold or self.in_bomb_zone(state, self.x, self.y)), best_path_vec
    
    # Check if a monster is below us or if our exit path is blocked, leaving us vulnerable
    # PARAM[SensedWorld] state: the current state of the world
    # RETURN[boolean] : True if a monster threatens the path to exit, False otherwise
    def monster_on_path(self, state):
        """Check if a monster threatens our safety on path to the exit"""
        max_y = 0
        for mlist in state.monsters.values():
            for monster in mlist:
                max_y = max(max_y, monster.y)
        if self.y > max_y + 1:
            # We are ahead, but if no path, we're in danger from behind anyway
            exit_path = fn.A_star(state, (self.x, self.y), state.exitcell)
            return fn.wall_in_path(state, exit_path)
        # Monster is ahead
        return True
    
    # Checks if our best path is leading us to a wall that must be blown up
    # PARAM[SensedWorld] state: the current state of the world
    # PARAM[tuple(int, int)] best_next_move_vec: the location the A* algorithm would like to go to
    # RETURN[boolean] : True if the location needs bombing, False otherwise
    def should_place_bomb(self, state, best_next_move_vec):
        """Check if we must bomb to continue on best path"""
        # No possible moves from pathplanning search
        return state.wall_at(best_next_move_vec[0], best_next_move_vec[1])
    
    # Perform the agent's turn
    # PARAM[SensedWorld] state: the current state of the world
    def do(self, world):
        safe, best_path_vec = self.is_safe(world)
        if(safe):
            if(self.should_place_bomb(world, (self.x+ best_path_vec[0], self.y + best_path_vec[1]))):
                self.place_bomb()
                self.move(0, 0)
            else:
                # Make move to best postition based on best path
                # First make sure we arent running into a dangerous bomb/explosion
                bomb_danger = False
                next_x, next_y = self.x + best_path_vec[0], self.y + best_path_vec[1]
                
                # Don't walk over bombs that are gonna explode soon
                if self.in_bomb_zone(world, next_x, next_y):
                    bomb_danger = True
                if (bomb_danger): # override moving to death
                    self.move(0,0)
                else:
                    self.move(best_path_vec[0], best_path_vec[1])
        else:
            best_action = self.determine_best_action(world)
            if best_action == Action.BOMB:
                self.place_bomb()
                self.move(0, 0)
            else:
                direction = ActionDirections[best_action]
                self.move(direction[0], direction[1])
                pass

    # Finds the best next step to victory
    # PARAM[SensedWorld] state: the current state of the world
    # RETURN[tuple(int, int)] : the direction vector to move in to follow the path
    def find_best_path_vector(self, state):
        """Finds the best next step to victory"""
        loc = (self.x, self.y)
        return self.A_star(state, loc, state.exitcell)[0]

    # Calculate the A* path cost to the nearest monster
    # PARAM[SensedWorld] state: the current state of the world
    # RETURN[int] : the A* cost to get to the closest monster
    def dist_to_nearest_monster(self, state):
        """Get A* distance to closest monster"""
        monsters = self.find_monsters(state)
        
        if monsters is None:
            return 0
        
        else:
            closest_monster_dist = math.inf
            for m in monsters:
                monster_dist = self.A_star(state, (self.x, self.y), m)[1]
                if monster_dist < closest_monster_dist:
                    closest_monster_dist = monster_dist
            return closest_monster_dist

    # Calculates the step distance between two points without walls
    # PARAM[int] x1: X value of the first point
    # PARAM[int] y1: Y value of the first point
    # PARAM[int] x2: X value of the second point
    # PARAM[int] y2: Y value of the second point
    # RETURN[int] : the step distance between two points
    def tile_dist(self, x1, y1, x2, y2):
        """Step distance without walls"""
        return max(abs(x1-x2), abs(y1-y2))

    # Helper method to find monsters
    # PARAM[SensedWorld] state: the current state of the map
    # RETURN[list(tuple(int, int))] : a list of all monster coordinate tuples
    def find_monsters(self, state):
        """Returns list of coordinates with monsters"""
        monsters = []
        for w in range(state.width()):
            for h in range(state.height()):
                monster = state.monsters_at(w, h)
                if monster is not None:
                    monsters.append((w,h))
        return monsters

    # Finds an optimal path from start to goal using the A* algorithm
    # PARAM[SensedWorld] state: the current state of the map
    # PARAM[tuple(int, int)] start: the starting coordinates
    # PARAM[tuple(int, int)] goal: the goal coordinates
    # RETURN[tuple(int, int), int] : the direction vector for the next step and the cost to the goal
    def A_star(self, state, start, goal):
        """Perform A* search with walls cost 3"""
        def g(state, pos):
            return 3 if(state.wall_at(*pos)) else 1
        def h(state, pos):
            return self.tile_dist(*pos, *goal)

        frontier = PriorityQueue()
        frontier.put((0, start))
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0
        
        while not frontier.empty():
            priority_pair = frontier.get()
            current = priority_pair[1]

            if(current == goal):
                break

            # Add neighbors to queue
            x,y = current[0], current[1]
            for next_pos in ((x+1,y), (x-1,y), (x,y+1), (x,y-1), (x+1, y+1), (x+1, y-1), (x-1, y-1), (x-1, y+1)):
                
                # Check that the position is valid
                if 0 <= next_pos[0] < state.width() and 0 <= next_pos[1] < state.height():
                    new_cost = cost_so_far[current] + g(state, next_pos)

                    if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                        cost_so_far[next_pos] = new_cost
                        priority = new_cost + h(state, next_pos)
                        frontier.put((priority, next_pos))
                        came_from[next_pos] = current

        # Loop back and find optimal move vector
        cur_coor = current
        while(came_from[cur_coor] != start):
            cur_coor = came_from[cur_coor]
        
        return (cur_coor[0] - start[0], cur_coor[1] - start[1]), cost_so_far[goal]


class ExploitationAgent(QAgent):
    def __init__(self, name, avatar, x, y):
        super().__init__(name, avatar, x, y)
    
    # Perform the agent's turn (always best action)
    # PARAM[SensedWorld] state: the current state of the map
    def do(self, world):
        """Find and perform best available move"""
        best_action = self.determine_best_action(world)
        if best_action == Action.BOMB:
            self.place_bomb()
            self.move(0, 0)
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
        """Update weights based on rewards while training"""
        current_action = self.last_action
        reward = rewardfunctions.reward(current_state, current_action, self)
        current_utility = self.evaluate_move(current_state, current_action)
        next_action = self.determine_best_action(next_state)
        # delta = r + v(max(a')(Q(s',a'))) - Q(s,a)
        delta = (reward + (discount*self.evaluate_move(next_state, next_action))) - current_utility\
        # wi = wi + a*delta*fi(s,a)
        for w_idx in range(len(self.weights)):
            self.weights[w_idx] = self.weights[w_idx] + self.alpha*delta*self.feature_functions[w_idx](current_state, current_action, self)

    # Perform the agent's turn (epsilon-greedy)
    # PARAM[SensedWorld] state: the current state of the map
    def do(self, world):
        """Perform a move using epsilon greedy algorithm"""
        x = random.random()
        if(x < self.epsilon):
            best_action = self.generate_random_action()
        else:
            best_action = self.determine_best_action(world)
        
        self.last_action = best_action
        
        if best_action == Action.BOMB:
            self.place_bomb()
            self.move(0, 0)
        else:
            direction = ActionDirections[best_action]
            self.move(direction[0], direction[1])
    
    # Decrease epsilon by self.epsilon_decrement
    def update_epsilon(self):
        """Decrement epsilon"""
        self.epsilon -= self.epsilon_decrement
    
    # Select a random action
    # RETURN[Action] : any random action
    def generate_random_action(self):
        """Select a random action"""
        action_num = random.randint(1,10)
        action = Action(action_num)
        return action
