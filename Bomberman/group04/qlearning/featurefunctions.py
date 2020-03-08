import os, sys
import math
import collections

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import actions
from queue import PriorityQueue

import numpy as np


# TODO feature functions for small boards lol

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

    if shortest_path is None:
        # No monsters
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
    
    # try normalizing vector before
    exit_vec_length = math.sqrt(exit_vec[0]**2 + exit_vec[1]**2)
    if exit_vec_length == 0:
        normal_exit_vec = [0,0]
    else:
        normal_exit_vec = [vector/exit_vec_length for vector in exit_vec]
    #print(normal_exit_vec)

    max_threat = -1
    for monsterlist in state.monsters.values():
        for monster in monsterlist:
            monster_vec = [monster.x - new_x, monster.y - new_y] # old way
            
            # try normalizing vector before
            monster_vec_length = math.sqrt(monster_vec[0]**2 + monster_vec[1]**2)
            if monster_vec_length == 0:
                normal_monster_vec = [0,0]
            else:
                normal_monster_vec = [vector/monster_vec_length for vector in monster_vec]
            #print(normal_monster_vec)
            
            #threat = dotp(exit_vec, monster_vec) # old way
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


    # checks for active bomb
    if (ticking_bomb):
        # check if we are in the x component of explosion
        if (abs(new_x - bomb.x) <= 4 and new_y == bomb.y):
            in_explosion_radius = True
        # y component
        elif (abs(new_y - bomb.y) <= 4 and new_x == bomb.x):
            in_explosion_radius = True
    
    # checks for active explosions
    if (state.explosion_at(new_x, new_y)):
        # really bad
        return 1
    
    if (in_explosion_radius):
        # more bad depending on how close bomb is to going off
        if bomb.timer <= 1:
            return 1
        return 0
    
    # no active bombs or explosion on new tile
    return 0


# Feature for detecting if a path to the exit exists
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
        return 0
    
    # Path found
    return 0


# BFS for optimal path
# PARAM[SensedWorld] state: the current state of the board
# PARAM[tuple(int, int)] start: starting coordinates
# PARAM[tuple(int, int)] goal: goal coordinates
def bfs(state, start, goal):
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
        # TODO what should this be
        return path
        #return path[1][0] - start[0], path[1][1] - start[1]
    
    # No path
    return None


def A_star(state, start, goal):
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

                if((x2,y2) not in cost_so_far or new_cost < cost_so_far[(x2,y2)]):
                    cost_so_far[(x2,y2)] = new_cost
                    priority = new_cost
                    frontier.put((x2,y2),priority)
                    came_from[(x2,y2)] = current

    #Loop back and build the path
    cur_coor = current
    path = [cur_coor]
    #print(f'Start: {start} Cur: {cur_coor}')
    while(cur_coor != None):
        cur_coor = came_from[cur_coor]
        path.insert(0, cur_coor)
    return path


# Returns true if one of the tiles in the given path is a wall
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


# Compute the dot product of two vectors
# PARAM[tuple(int...)] v1: the first vector
# PARAM[tuple(int...)] v2: the second vector
def dotp(v1, v2):
    """Return the dot product of the two vectors"""
    mag1, mag2 = 0, 0
    for i in range(len(v1)):
        mag1 += v1[i] * v1[i]
        mag2 += v2[i] * v2[i]
    mag1 = math.sqrt(mag1)
    mag2 = math.sqrt(mag2)

    if mag1 == 0 or mag2 == 0:
        return 0

    return sum([(v1[i] / mag1) * (v2[i] / mag2) for i in range(len(v1))])


feature_functions = [
    dist_to_exit,
    dist_to_monster,
    monster_threat,
    bomb_danger_zone,
    no_path_bomb
]