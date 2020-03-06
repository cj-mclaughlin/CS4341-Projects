import os, sys
import math
import collections

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import actions


# TODO feature functions for small boards lol


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
        if x == goal[0] and y == goal[1]: # check if we have reached exit
            break
        for x2, y2 in ((x+1,y), (x-1,y), (x,y+1), (x,y-1), (x+1, y+1), (x+1, y-1), (x-1, y-1), (x-1, y+1)):
            if 0 <= x2 < state.width() and 0 <= y2 < state.height() and not state.wall_at(x2, y2) and (x2, y2) not in seen:
                queue.append(path + [(x2, y2)])
                seen.add((x2, y2))
    return path

# TODO export function
feature_functions = [
]