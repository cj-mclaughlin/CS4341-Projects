import os, sys
import math
import collections

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import actions
from queue import PriorityQueue

import numpy as np


# Feature based on distance to nearest monster
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def dist_to_monster(state, action, character):
    """Feature value that is higher when closer to monster"""
    new_loc = post_action_location(state, action, character)
    shortest_len = math.inf
    shortest_path = None
    
    # Iterate over all monsters in world
    for monsterlist in state.monsters.values():
        for monster in monsterlist:
            path = A_star(state, new_loc, (monster.x, monster.y))
            if len(path) < shortest_len:
                shortest_path = path
                shortest_len = len(path)

    # No monsters
    if shortest_path is None:
        return 0
    
    # Feature is inversely proportional to distance
    return 1 / len(shortest_path)


# Feature based on distance to exit
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def dist_to_exit(state, action, character):
    """Feature value that is higher when closer to exit"""
    new_loc = post_action_location(state, action, character)
    path = A_star(state, new_loc, state.exitcell)

    # No path found
    if wall_in_path(state, path):
        return 0

    # Feature is inversely proportional to distance
    return 1 / len(path)


# Feature based on monsters blocking character path
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def monster_threat(state, action, character):
    """Feature value that is higher when monster poses more of a threat to the path"""
    new_x, new_y = post_action_location(state, action, character)
    exit_vec = [state.exitcell[0] - new_x, state.exitcell[1] - new_y] # old way
    
    normal_exit_vec, normal_monster_vec = [], []
    
    # Normalize vector
    exit_vec_length = math.sqrt(exit_vec[0]**2 + exit_vec[1]**2)
    if exit_vec_length == 0:
        normal_exit_vec = [0,0]
    else:
        normal_exit_vec = [vector/exit_vec_length for vector in exit_vec]

    max_threat = -1
    for monsterlist in state.monsters.values():
        for monster in monsterlist:
            monster_vec = [monster.x - new_x, monster.y - new_y] # old way
            
            # Normalize vector
            monster_vec_length = math.sqrt(monster_vec[0]**2 + monster_vec[1]**2)
            if monster_vec_length == 0:
                normal_monster_vec = [0,0]
            else:
                normal_monster_vec = [vector/monster_vec_length for vector in monster_vec]
            
            threat = np.dot(normal_exit_vec, normal_monster_vec)
            threat = threat ** 3
            if threat > max_threat:
                max_threat = threat
    
    # Normalize for feature value
    return (0.5 * max_threat) + 0.5
    

# Evaluates danger zone of ticking bombs and active explosions
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def bomb_danger_zone(state, action, character):
    """Checks if action places character in explosion range"""
    new_x, new_y = post_action_location(state, action, character)
    in_explosion_radius = False
    ticking_bomb = False
    
    # Get bomb from bombs dict
    bomb = None
    for b in state.bombs.values():
        bomb = b

    # Check if a bomb is active
    if bomb is not None:
        ticking_bomb = True


    # Checks for active bomb
    if (ticking_bomb):
        # Check if we are in the x component of explosion
        if (abs(new_x - bomb.x) <= 4 and new_y == bomb.y):
            in_explosion_radius = True
        # Check y component
        elif (abs(new_y - bomb.y) <= 4 and new_x == bomb.x):
            in_explosion_radius = True
    
    # Checks for active explosions
    if (state.explosion_at(new_x, new_y)):
        # really bad
        return 1
    
    if (in_explosion_radius):
        # Only bad if bomb is close to going off
        if bomb.timer <= 1:
            return 1
        return 0
    
    # No active bombs or explosion on new tile
    return 0


# Feature for detecting if a path to the exit exists, or is about to be blown open
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def no_path_bomb(state, action, character):
    """Feature returns 1 if exit path blocked, 0 if available or about to be freed by bomb"""
    new_loc = post_action_location(state, action, character)
    path = A_star(state, new_loc, state.exitcell)
    if wall_in_path(state, path):
        # No path. Can bomb make path?
        if action == actions.Action.BOMB:
            for i in range(1, state.expl_range + 1):
                expl_x, expl_y = character.x, character.y + i
                if 0 <= expl_x < state.width() and 0 <= expl_y < state.height() and state.wall_at(expl_x, expl_y):
                    # Wall found in south direction
                    return 1
        # Not placing bomb
        return 0
    
    # Path found
    return 0


# Finds an optimal path from start to goal using the A* algorithm
# PARAM[SensedWorld] state: the current state of the map
# PARAM[tuple(int, int)] start: the starting coordinates
# PARAM[tuple(int, int)] goal: the goal coordinates
def A_star(state, start, goal):
    """Performs A* search to find a path from start to goal"""
    def g(state, pos):
        return 11 if(state.wall_at(*pos)) else 1
    def h(state, pos):
        return tile_dist(*pos, *goal)

    frontier = PriorityQueue()
    frontier.put((0, start))
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0
    
    while not frontier.empty():
        priority_pair = frontier.get()
        current = priority_pair[1]

        if (current == goal):
            break

        # Add neighbors to queue
        x,y = current[0], current[1]
        for next_pos in ((x+1,y), (x-1,y), (x,y+1), (x,y-1)):
            
            # Check that the position is valid
            if 0 <= next_pos[0] < state.width() and 0 <= next_pos[1] < state.height():
                new_cost = cost_so_far[current] + g(state, next_pos)

                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + h(state, next_pos)
                    frontier.put((priority, next_pos))
                    came_from[next_pos] = current

    # Loop back and build the path
    cur_coor = current
    path = [cur_coor]
    while(cur_coor != None):
        cur_coor = came_from[cur_coor]
        path.insert(0, cur_coor)
    return path


# Calculates the step distance between two points without walls
# PARAM[int] x1: X value of the first point
# PARAM[int] y1: Y value of the first point
# PARAM[int] x2: X value of the second point
# PARAM[int] y2: Y value of the second point
# RETURN[int] : the step distance between two points
def tile_dist(x1, y1, x2, y2):
    """Step distance without walls"""
    return max(abs(x1-x2), abs(y1-y2))


# Returns true if one of the tiles in the given path is a wall
# PARAM[SensedWorld] state: the current state of the map
# PARAM[list(tuple(int, int))] path: the path to evaluate
def wall_in_path(state, path):
    for loc in path:
        if loc is not None and state.wall_at(*loc):
            return True
    return False


# Returns the locaton of character after taking action in state
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def post_action_location(state, action, character):
    """Returns where we would be after taking specified action"""
    x_dir, y_dir = actions.ActionDirections[action]
    cur_x, cur_y = character.x, character.y
    new_x, new_y = x_dir+cur_x, y_dir+cur_y

    # See if action would put us out of bounds or into a wall (no effective movement)
    if not valid_location(state, new_x, new_y):
        new_x, new_y = cur_x, cur_y
    
    return new_x, new_y


# Check that the position is a valid move
# PARAM[SensedWorld] state: the state of the current board
# PARAM[int] x: the value of the x coordinate of the position to check
# PARAM[int] y: the value of the y coordinate of the position to check
# RETURN[boolean] : whether the position is valid
def valid_location(state, x, y):
    """Check if we are going out of bounds or into a wall"""
    # Check that there is no wall in the new position
    if 0 <= x < state.width() and 0 <= y < state.height() and not state.wall_at(x, y):
        return True
    return False


feature_functions = [
    dist_to_exit,
    dist_to_monster,
    monster_threat,
    bomb_danger_zone,
    no_path_bomb
]
