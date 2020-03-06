import os, sys
import math
import collections

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import actions


#Distance Functions

# Function that quantifies how far the player is from the exit
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def dist_to_exit(state, action, character):
    """Check if we are getting closer or further from the exit"""
    new_x, new_y = post_action_location(state, action, character)
    exit_x, exit_y = state.exitcell
    furthest_dist_from_exit = manhattan_dist(0,0,exit_x,exit_y)
    
    return 1/(manhattan_dist(new_x,new_y, exit_x, exit_y) + 1)
    #return (manhattan_dist(new_x,new_y, exit_x, exit_y)/ furthest_dist_from_exit)

# Function that returns distance to closest monster
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def dist_to_monster(state, action, character):
    """Check if we are getting closer/further from a monster"""
    search_radius = 6
    new_x, new_y = post_action_location(state, action, character)
    monsters = find_monsters(state)
    
    if monsters is None:
        return 0
    
    else:
        closest_monster_dist = math.inf
        for m in monsters:
            monster_dist = manhattan_dist(new_x, new_y, m[0], m[1])
            if monster_dist < closest_monster_dist:
                closest_monster_dist = monster_dist

    return 1/(closest_monster_dist + 1)

    # TODO specify vision 'radius'
    #if (closest_monster_dist < search_radius):
        #return 1-(closest_monster_dist/search_radius)
    # else:
    #     return 0

# BFS to move around walls
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def move_around_walls(state, action, character):
    new_x, new_y = post_action_location(state, action, character)
    start = (character.x, character.y)
    queue = collections.deque([[start]])
    seen = set([start])
    # perform bfs, leaving us with path to exit
    while queue:
        path = queue.popleft()
        x, y = path[-1]
        if x == state.exitcell[0] and y == state.exitcell[1]: # check if we have reached exit
            break
        for x2, y2 in ((x+1,y), (x-1,y), (x,y+1), (x,y-1), (x+1, y+1), (x+1, y-1), (x-1, y-1), (x-1, y+1)):
            if 0 <= x2 < state.width() and 0 <= y2 < state.height() and not state.wall_at(x2, y2) and (x2, y2) not in seen:
                queue.append(path + [(x2, y2)])
                seen.add((x2, y2))
    if (len(path) < 2):
        next_step = path[0]
    else:
        next_step = path[1]
    return 1 / (manhattan_dist(new_x, new_y, next_step[0], next_step[1]) + 1)


# TODO Remove when we know we wont be using this
# Function which helps us figure out how tf to move around walls
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def move_towards_gap(state, action, character):
    """Encourage movement to closest gap in next wall, if one exists"""
    dist_to_gap = math.inf
    new_x, new_y = post_action_location(state, action, character)
    
    bomb = find_bomb(state)
    
    # check if we're currently standing in a gap
    has_walls = False
    has_gap = False
    for w in range(state.width()):
        if not state.wall_at(w, new_y):
            has_gap = True
        else:
            has_walls = True
            
    # we are in a gap
    if (has_walls and has_gap and (character.y < new_y)):
        return 1
    
    # find nearest row with a wall that we need to consider
    found_row_with_wall = False
    offset = 0
    h = (new_y + offset + 1)
    while (h < state.height()):
        for w in range(state.width()):
            if state.wall_at(w, h):
                found_row_with_wall = True
                break
        if (found_row_with_wall):
            break
        offset += 1
        h = (new_y + offset + 1)
    
    # find gap in corresponding row
    closest_gap = None
    closest_gap_dist = math.inf
    if (found_row_with_wall):
        for w in range(state.width()):
            # check for existing gap in walls
            if (not state.wall_at(w,h)):
                dist_to_gap = manhattan_dist(new_x, new_y, w, h)
                if dist_to_gap < closest_gap_dist:
                    closest_gap = (w, h)
                    closest_gap_dist = dist_to_gap
                    
    #print("inclined to move towards next gap: ", closest_gap)
    
    # no existing gap
    if (closest_gap is None):
        # check for future gaps in walls (explosions/bombs)
        if (found_row_with_wall):
            for w in range(state.width()):
                if(state.explosion_at(w,h) or (bomb is not None and bomb.x == w and abs(bomb.y - h) < state.expl_range)):
                    if (bomb is not None):
                        closest_gap = (w+1,bomb.y-1) # goal tile is right out of bomb range
                    else:
                        closest_gap = (w+1, h-1) # stand outside explosion
                    break
    
    # shouldnt be here until end
    if (closest_gap is None):
        print("here")
        return 1/(manhattan_dist(new_x,new_y, state.exitcell[0], state.exitcell[1])+1)
    
    # verify that we're going in the direction of the next gap (and not into walls!)
    dx, dy = int(round(closest_gap[0] - character.x)), int(round(closest_gap[1] - character.y))
    if (dx > 1):
        dx = 1
    if (dy > 1):
        dy = 1
    if (dx < -1):
        dx = -1
    if (dy < -1):
        dy = -1
    a_x, a_y =  actions.ActionDirections[action][0], actions.ActionDirections[action][1]
    
    
    return 1/(closest_gap_dist + 1)
    
    # if (closest_gap[0] == character.x and closest_gap[1] == character.y and action == actions.Action.STILL):
    #     return 0
    
    # # check bounds
    # if (character.x + a_x >= state.width() or character.y + a_y >= state.height()):
    #     return 0
    
    # # verify that action helps us go towards goal tile
    # if ((dx != a_x or state.wall_at(character.x + a_x, character.y + a_y)) and (dy != a_y or (state.wall_at(character.x + a_x, character.y + a_y)))):
    #     #print("action dir ({},{}) not move us towards gap ({},{})".format(a_x, a_y, closest_gap[0], closest_gap[1]))
    #     return 1 # moving away from gap is bad
    # else:
    #     return 0


# Check that the new position is a valid move
# PARAM[SensedWorld] state: the state of the current board
# PARAM[int] new_x: the value of the new x coordinate of the position to check
# PARAM[int] new_y: the value of the new y coordinate of the position to check
# RETURN[boolean] : whether the new move is valid
def valid_location(state, new_x, new_y):
    """Check if we are going out of bounds or into a wall"""
    #Check that there is no wall in the new position
    if (new_x < 0 or new_y < 0 or new_x >= state.width() or new_y >= state.height() or state.wall_at(new_x, new_y)):
        return False
    return True

# Calculates the manhattan distance between two points
# PARAM[int] x1: X value of the first point
# PARAM[int] y1: Y value of the first point
# PARAM[int] x2: X value of the second point
# PARAM[int] y2: Y value of the second point
# RETURN[int] : the manhattan distance between two points
def manhattan_dist(x1, y1, x2, y2):
    """Manhattan distance"""
    return abs(x1-x2) + abs(y1-y2)

  
#Bomb functions

# Checks if we are near a blocking wall
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def wall_in_bomb_range(state, action, character):
    """Checks if we are against a complete blocking wall (bomb necessary)"""
    char_x, char_y = post_action_location(state, action, character)
    blocked_by_wall = True
    
    # First check that we haven't already put down a bomb
    bomb = find_bomb(state)
    if bomb is not None: # should bother putting down another
        return 0
    
    # find nearest row with a wall that we need to consider
    found_row_with_wall = False
    offset = 0
    h = (char_y + offset + 1)
    while (h < state.height()):
        for w in range(state.width()):
            if state.wall_at(w, h):
                found_row_with_wall = True
                break
        if (found_row_with_wall):
            break
        if (h + 1 >= state.expl_range):
            break
        offset += 1
        h = (char_y + offset + 1)
    
    # Checking for horizontal wall below character (assumes horizontal walls and exit in +y direction)
    for w in range(state.width()):
        if (h >= state.height()): # no space to be blocked by a wall
            blocked_by_wall = False 
            break
        if not state.wall_at(w, h) or state.explosion_at(w,h): # found a gap
            blocked_by_wall = False
            break
    
    if (blocked_by_wall and action == actions.Action.BOMB):
        return 1
    
    return 0

# Evaluates danger zone of ticking bombs and active explosions
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def bomb_danger_zone(state, action, character):
    """Checks if action places character in explosion range"""
    char_x, char_y = post_action_location(state, action, character)
    in_explosion_radius = False
    ticking_bomb = False
        
    # Check if a bomb is active
    bomb = find_bomb(state)
    if bomb is not None:
        ticking_bomb = True


    # checks for active bomb
    if (ticking_bomb):
        # check if we are in the x component of explosion
        if (abs(char_x - bomb.x) <= 4 and char_y == bomb.y):
            in_explosion_radius = True
        # y component
        elif (abs(char_y - bomb.y) <= 4 and char_x == bomb.x):
            in_explosion_radius = True
    
    # checks for active explosions
    if (state.explosion_at(char_x, char_y)):
        # really bad
        return 1
    
    if (state.bomb_at(char_x, char_y)):
        # Sitting on bomb can be dangerous
        return 1
    
    if (in_explosion_radius):
        # more bad depending on how close bomb is to going off
        return 1 / (bomb.timer + 1)
    
    return 0 # no active bombs or explosion on new tile


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
    if(not valid_location(state, new_x, new_y)):
        new_x, new_y = cur_x, cur_y
    
    return new_x, new_y


# Helper method to find bomb (hopefully we can just index in the future)
# PARAM[SensedWorld] state: the current state of the map
def find_bomb(state):
    """Returns active bomb if one exists, None otherwise"""
    for bomb in state.bombs.values():
        return bomb
    # for w in range(state.width()):
    #     for h in range(state.height()):
    #         bomb = state.bomb_at(w, h)
    #         if bomb is not None:
    #             return bomb

# Helper method to find monsters
# PARAM[SensedWorld] state: the current state of the map
def find_monsters(state):
    """Returns list of coordinates with monsters"""
    monsters = []
    for w in range(state.width()):
        for h in range(state.height()):
            monster = state.monsters_at(w, h)
            if monster is not None:
                monsters.append((w,h))
    return monsters

# Export of the feature functions
feature_functions = [
    dist_to_exit,
    dist_to_monster,
    move_around_walls,
    bomb_danger_zone,
    wall_in_bomb_range
]