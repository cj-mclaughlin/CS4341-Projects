from enum import Enum

class Action(Enum):
    NORTH = 1
    SOUTH = 2
    WEST = 3
    EAST = 4
    BOMB = 5
    STILL = 6
    NORTHEAST = 7
    NORTHWEST = 8
    SOUTHEAST = 9
    SOUTHWEST = 10
# Representation of the directions associated with all the different actions
# Directions held in the following format (x,y)
ActionDirections = {
    Action.NORTH : (0,-1),
    Action.SOUTH : (0,1),
    Action.WEST : (-1,0),
    Action.EAST : (1,0),
    Action.BOMB : (0,0),
    Action.STILL : (0,0),
    Action.NORTHEAST : (1,-1),
    Action.NORTHWEST : (-1,-1),
    Action.SOUTHEAST : (1,1),
    Action.SOUTHWEST : (-1,1)
}