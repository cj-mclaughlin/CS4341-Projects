import os, sys
import math

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import actions

#Distance Functions

# Function that quantifies how far the player is from the exit
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def dist_to_exit(state, action, character):
    x_dir, y_dir = actions.ActionDirections[action]
    cur_x, cur_y = character.x, character.y
    new_x, new_y = x_dir+cur_x, y_dir+cur_y
    exit_x, exit_y = state.exitcell
    #Check that new position is valid and if not calculate move function based on current position
    if(not valid_location(state, new_x, new_y)):
        new_x, new_y = cur_x, cur_y
    #Calculate manhatan distance between two points
    return manhattan_dist(new_x, new_y, exit_x, exit_y)

# TODO Function that quantifies how far the player is from the nearest monster
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def dist_to_monster(state, action, character):
    x_dir, y_dir = actions.ActionDirections[action]
    cur_x, cur_y = character.x, character.y
    new_x, new_y = x_dir+cur_x, y_dir+cur_y

    #Check that new position is valid and if not calculate move function based on current position
    if(not valid_location(state, new_x, new_y)):
        new_x, new_y = cur_x, cur_y
    
    
    # TODO temporary
    return 0
    
    # TODO Find the closest monster coordinates
    c_mon_x, c_mon_y, c_mon_dist = math.inf, math.inf, math.inf
    #for mon in state.monsters.

# Check that the new position is a valid move
# PARAM[SensedWorld] state: the state of the current board
# PARAM[int] new_x: the value of the new x coordinate of the position to check
# PARAM[int] new_y: the value of the new y coordinate of the position to check
# RETURN[boolean] : whether the new move is valid
def valid_location(state, new_x, new_y):
    #Check that there is no wall in the new position
    return state.wall_at(new_x, new_y)

# Calculates the manhattan distance between two points
# PARAM[int] x1: X value of the first point
# PARAM[int] y1: Y value of the first point
# PARAM[int] x2: X value of the second point
# PARAM[int] y2: Y value of the second point
# RETURN[int] : the manhattan distance between two points
def manhattan_dist(x1, y1, x2, y2):
    return abs(x1-x2) + abs(y1-y2)

  
#Bomb functions

# Checks if we are near a blocking wall
# PARAM[SensedWorld] world: the current state of the map
# PARAM[Action] action: the action to evaluate
def wall_in_bomb_range(world, action):
    """Checks if we are against a complete blocking wall (bomb necessary)"""
    
    # Checking for horizontal wall below character
    character = find_char(world)
    blocked_by_wall = True
    
    for w in range(world.width()):
        if not world.wall_at(w, character.y + 1):
            blocked_by_wall = False
            break
    
    # TODO decide if we only want this retval if action=place bomb
    if (blocked_by_wall):
        return 1
    
    return 0

# Checks if we are in the explosion radius of an active bomb
# PARAM[SensedWorld] world: the current state of the map
# PARAM[Action] action: the action to evaluate
def bomb_danger_zone(world, action):
    """Checks if action places character in explosion range"""
    character = find_char(world)
    in_explosion_radius = False
    
    # Check if a bomb is active
    bomb = find_bomb(world)
    if bomb is None:
        return 0

    # check if we are in the x component of explosion
    if (abs(character.x - bomb.x) <= 4 and character.y == bomb.y):
        in_explosion_radius = True
    # y component
    elif (abs(character.y - bomb.y) <= 4 and character.x == bomb.x):
        in_explosion_radius = True
    
    # TODO scale urgency based on how close we are to fuse
    if (in_explosion_radius):
        return 1
    else: 
        return 0
      

# TODO update find_methods to be constant lookups, or a single search

# Helper method to find bomb (hopefully we can just index in the future)
# PARAM[SensedWorld] world: the current state of the map
def find_bomb(world):
    # TODO find without search
    for w in range(world.width()):
        for h in range(world.height()):
            bomb = world.bomb_at(w, h)
            if bomb is not None:
                return bomb
            
# Helper method to find character (hopefully we can just index in the future)
# PARAM[SensedWorld] world: the current state of the map
def find_char(world):
    # TODO find without search
    for w in range(world.width()):
        for h in range(world.height()):
            char = world.characters_at(w, h)
            if char is not None:
                return char[0]

# Export of the feature functions
feature_functions = [
    dist_to_exit,
    dist_to_monster,
    bomb_danger_zone,
    wall_in_bomb_range
]