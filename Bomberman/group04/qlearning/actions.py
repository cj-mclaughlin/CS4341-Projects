from enum import Enum

class Action(Enum):
    NORTH = 1
    SOUTH = 2
    WEST = 3
    EAST = 4
    BOMB = 5
# Representation of the directions associated with all the different actions
# Directions held in the following format (x,y)
ActionDirections = {
    #TODO check to see if North and South directions are correct
    Action.NORTH : (0,-1),
    Action.SOUTH : (0,1),
    Action.WEST : (-1,0),
    Action.EAST : (1,0),
    Action.BOMB : (0,0)
}