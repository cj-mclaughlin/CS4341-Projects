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
    for monsterlist in state.monsters.values():
        for monster in monsterlist:
            path = bfs(state, new_loc, (monster.x, monster.y))
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
    path = bfs(state, new_loc, state.exitcell)

    # No path found
    if path is None:
        return 0

    # Feature is inversely proportional to distance
    return 1 / (len(path) + 1)


# Feature based on monsters blocking character path
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def monster_threat(state, action, character):
    """Feature value that is higher when monster poses more of a threat to the path"""
    new_x, new_y = post_action_location(state, action, character)
    vec_to_exit = (state.exitcell[0] - new_x, state.exitcell[1] - new_y)

    max_threat = -1
    for monsterlist in state.monsters.values():
        for monster in monsterlist:
            vec_to_monster = (monster.x - new_x, monster.y - new_y)
            threat = dotp(vec_to_exit, vec_to_monster)
            if threat > max_threat:
                max_threat = threat

    # Normalize for feature value
    return 0.5 * max_threat + 0.5
    

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
        return 1 / (bomb.timer + 1)
    
    # no active bombs or explosion on new tile
    return 0


# Feature for detecting if a path to the exit exists
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def no_path(state, action, character):
    """Feature returns 1 if no exit path, 0 otherwise"""
    new_loc = post_action_location(state, action, character)
    path = bfs(state, new_loc, state.exitcell)
    if path is None:
        # No path
        return 1
    
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
        return path[1][0] - start[0], path[1][1] - start[1]
    
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
    no_path
]
