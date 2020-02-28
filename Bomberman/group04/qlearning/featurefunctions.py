import actions

# Distance Functions

# Function that quantifies how far the player is from the exit
# PARAM[SensedWorld] state: the current state of the map
# PARAM[Action] action: the action to evaluate
# PARAM[MovableEntity] character: the bomberman character this is evaluating for
def distToExit(state, action, character):
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
def distToMonster(state, action, character):
    x_dir, y_dir = actions.ActionDirections[action]
    cur_x, cur_y = character.x, character.y
    new_x, new_y = x_dir+cur_x, y_dir+cur_y

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