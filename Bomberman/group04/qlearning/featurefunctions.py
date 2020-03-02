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
    """Check if we are getting closer or further from the exit"""
    new_x, new_y = post_action_location(state, action, character)
    exit_x, exit_y = state.exitcell
    
    # TODO figure if we want to normalize this or what, closer should be higher vals, incentive
    return 1 / manhattan_dist(new_x, new_y, exit_x, exit_y)

# TODO Function that quantifies how far the player is from the nearest monster
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def dist_to_monster(state, action, character):
    """Check if we are getting closer/further from a monster"""
    new_x, new_y = post_action_location(state, action, character)
    
    # TODO remove temporary fix
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
    
    # Checking for horizontal wall below character (assumes horizontal walls and exit in +y direction)
    for w in range(state.width()):
        if not state.wall_at(w, char_y + 1):
            blocked_by_wall = False
            break
    
    if (blocked_by_wall and action == actions.Action.BOMB):
        return 1
    
    return 0

# Evaluates danger zone of ticking bombs and active explosions
    # TODO decide if we only want this retval if action=place bomb
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
    
    
    # TODO scale urgency based on how close we are to fuse
    if (in_explosion_radius):
        # more bad depending on how close bomb is to going off
        return 1 / bomb.timer
    
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


# TODO update find_bomb to be constant lookup instead of search if possible

# Helper method to find bomb (hopefully we can just index in the future)
# PARAM[SensedWorld] state: the current state of the map
def find_bomb(state):
    """Returns active bomb if one exists, None otherwise"""
    for w in range(state.width()):
        for h in range(state.height()):
            bomb = state.bomb_at(w, h)
            if bomb is not None:
                return bomb

# Export of the feature functions
feature_functions = [
    dist_to_exit,
    dist_to_monster,
    bomb_danger_zone,
    wall_in_bomb_range
]