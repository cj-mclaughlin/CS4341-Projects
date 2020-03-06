import os, sys
import math
import collections

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import actions


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
    for monster in state.monsters.values():
        path = bfs(new_loc, (monster.x, monster.y))
        if path is not None and len(path) < shortest_len:
            shortest_path = path
            shortest_len = len(path)

    if shortest_path is None:
        # No monsters
        return 0
    
    # Feature is inversely proportional to distance
    return 1 / (len(path) + 1)


# Feature based on distance to exit
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def dist_to_exit(state, action, character):
    """Feature value that is higher when closer to exit"""
    new_loc = post_action_location(state, action, character)
    path = bfs(new_loc, state.exitcell)

    # Shouldn't happen, but just in case
    if path is None:
        return 0

    # Feature is inversely proportional to distance
    return 1 / (len(path) + 1)


# BFS for optimal path
# PARAM[SensedWorld] state: the current state of the board
# PARAM[tuple(int, int)] start: starting coordinates
# PARAM[tuple(int, int)] goal: goal coordinates
def bfs(state, start, goal):
    queue = collections.deque([[start]])
    seen = set([start])
    # perform bfs, leaving us with path to exit
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
        return path
    
    # No path
    return None


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


# TODO export function
feature_functions = [
]