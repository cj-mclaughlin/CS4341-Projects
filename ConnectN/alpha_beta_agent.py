import math
import agent
import math
import random

###########################
# Alpha-Beta Search Agent #
###########################

dx = [ 0,  1,  1,  1,  0, -1, -1, -1]
dy = [-1, -1,  0,  1,  1,  1,  0, -1]


class AlphaBetaAgent(agent.Agent):
    """Agent that uses alpha-beta search"""

    # Class constructor.
    #
    # PARAM [string] name:      the name of this player
    # PARAM [int]    max_depth: the maximum search depth
    def __init__(self, name, max_depth):
        super().__init__(name)
        # Max search depth
        self.max_depth = max_depth

    # Utility function
    #
    # PARAM [board.Board] brd: the current board state
    # RETURN [int]: utility value
    def utility(self, brd):
        """Heuristic function"""
        adj = self.adj_utility(brd)
        opp = self.opportunity_utility(brd)
        win = self.is_game_completed_heuristic(brd)
        if (win == 10000 or win == -10000): # experimental
            adj = 0
            opp = 0
        sum_util = adj + opp +win
        print("Total utility = adjacent:{} + opportunity:{} + win:{} = {}".format(adj, opp, win, sum_util))
        return sum_util
    
    # Utility function based on adjacent friendly tokens
    #
    # PARAM [board.Board] brd: the current board state
    # RETURN [int]: utility value
    def adj_utility(self, brd):
        """Adjacent heuristic function"""
        util = 0

        for i in range(brd.w):
            for j in range(brd.h):
                token = brd.board[j][i]

                # Check adjacent only for my tokens
                if token == self.player:
                    for direction in range(8):
                        next_x = j + dx[direction]
                        next_y = i + dy[direction]
                        if self.valid_loc(next_x, next_y, brd) and brd.board[next_x][next_y] == token:
                            util += 1

        #print('Utility from adjacent symbols: {}'.format(util))
        return util
    
    # Utility function based on potential lines crated
    #
    # PARAM [board.Board] brd: the current board state
    # RETURN [int]: utility value
    def opportunity_utility(self, brd):
        """Opportunity heuristic function"""
        util = 0
        length_heuristic_weight = 2.5 # can play with this in different ways down the line
        chain_mappings = self.number_in_a_row(brd)
        for key in chain_mappings.keys():
            util += length_heuristic_weight * key * chain_mappings[key] 
        #print('Utility from opportunity (chains of symbols): {}'.format(util))
        return util
        
    # Return dictionary mapping frequency of different length symbol chains
    #
    # PARAM [board.Board] brd: the current board state
    # RETURN [dict of int:int]: mapping of {length segments : number of occurances in board}
    def number_in_a_row(self, brd):
        """Calculates partial line segments for use in heuristics"""
        # generate mapping of {length segments : number of occurances in board}
        chains = dict()
        for i in range(2, brd.n+2, 1): # initialize mapping
            chains[i] = 0
        
        # iterate through board counting chains
        for w in range(brd.w-1):
            for h in range(brd.h-1):
                curr_chains = self.find_chains(brd, w, h)
                if curr_chains[0] >= 2:
                    chains[curr_chains[0]] += 1
                if curr_chains[1] >= 2:
                    chains[curr_chains[1]] += 1
        
        # remove double counted chains (every 3 chain is also being counted as a 2 chain -- could fix this in find_chains method or here)
        for i in range(brd.n, 2, -1):
            chains[i-1] -= chains[i]

        #print("Mapping of consecutive symbols found: {}".format(chains)) 
        return chains
        
    def is_game_completed_heuristic(self, brd):
        outcome = brd.get_outcome()
        print(f'Player number: {self.player} Outcome: {outcome}')
        if outcome == self.player:
            return 10000
        elif outcome == 0:
            return 0
        else:
            return -10000

    # Return tuple (chain_w, chain_h) containing the number of consecutive similar symbols in positive w/h direction starting from location w,h
    def find_chains(self, brd, w, h):
        """ Find number of consecutive similar tiles in positive directions"""
        symbol = brd.board[w][h]
        if symbol != self.player: # if it is not our symbol, we dont care to check
            return (0,0)
        chain_w = 1
        chain_h = 1
        # check in the y (w) direction
        while (self.valid_loc( w + chain_w,h, brd) and brd.board[w+chain_w][h] == self.player):
            chain_w += 1
        # check in the x (h) direction
        while (self.valid_loc(w,h + chain_h,  brd) and brd.board[w][h+chain_h] == self.player):
            chain_h += 1 
        return (chain_w, chain_h)
        
    # Return max utility value 
    #
    # PARAM [board.Board] brd: current board state
    # PARAM [int] a: alpha value
    # PARAM [int] b: beta value
    # PARAM [int] current_depth: current depth
    # RETURN [int] max utility value
    def max_value(self, brd, a, b, current_depth):
        """Max value fn for alpha-beta search"""
        terminal = brd.get_outcome()
        if terminal == 1 or terminal == 2:
            return self.utility(brd)
        if current_depth == self.max_depth:
            return self.utility(brd) # previously a
        v = -math.inf
        for succ in self.get_successors(brd):
            new_board = succ[0]
            v = max(v, self.min_value(new_board, a, b, current_depth+1))
            if v >= b:
                pass
            #    return v
            a = max(a, v)
        return v
                
    # Return min utility value 
    #
    # PARAM [board.Board] brd: current board state
    # PARAM [int] a: alpha value
    # PARAM [int] b: beta value
    # PARAM [int] current_depth: current depth for 
    # RETURN [int] min utility value
    def min_value(self, brd, a, b, current_depth):
        """Min value fn for alpha-beta search"""
        terminal = brd.get_outcome()
        if terminal == 1 or terminal == 2:
            return self.utility(brd)
        v = math.inf
        if current_depth == self.max_depth:
            return self.utility(brd) # previously b
        for succ in self.get_successors(brd):
            new_board = succ[0]
            v = min(v, self.max_value(new_board, a,b, current_depth+1))
            if v < a:
                pass
            #    return v
            b = min(b,v)
        return v

    # Perform search and return the best action for the given state.
    #
    # PARAM [board.Board] brd: the current board state
    # RETURN [int]: the column where the token must be added
    def alpha_beta_search(self, brd):
        """Search for the best move by evaluating available moves"""

        infinity = math.inf

        # Get values for available actions
        max_val = -infinity
        max_action = None
        for succ in self.get_successors(brd):
            print('Try move:', succ[1])
            succ[0].print_it()
            val = self.min_value(succ[0], infinity, -infinity, 1)
            print(f'VALUE: {val}')
            # Update maximum valued action
            if val > max_val:
                max_val = val
                max_action = succ[1]
        
        print("Wonderful AI chose move {} with heuristic value {}".format(max_action, max_val))
        
        return max_action

    # Pick a column.
    #
    # PARAM [board.Board] brd: the current board state
    # RETURN [int]: the column where the token must be added
    #
    # NOTE: make sure the column is legal, or you'll lose the game.
    def go(self, brd):
        """Search for the best move (choice of column for the token)"""
        return self.alpha_beta_search(brd)
        

    # Get the successors of the given board.
    #
    # PARAM [board.Board] brd: the board state
    # RETURN [list of (board.Board, int)]: a list of the successor boards,
    #                                      along with the column where the last
    #                                      token was added in it
    def get_successors(self, brd):
        """Returns the reachable boards from the given board brd. The return value is a tuple (new board state, column number where last token was added)."""
        # Get possible actions
        freecols = brd.free_cols()
        # Are there legal actions left?
        if not freecols:
            return []
        # Make a list of the new boards along with the corresponding actions
        succ = []
        for col in freecols:
            # Clone the original board
            nb = brd.copy()
            # Add a token to the new board
            # (This internally changes nb.player, check the method definition!)
            nb.add_token(col)
            # Add board to list of successors
            succ.append((nb,col))
        return succ
    
    # Check if a given coordinate is within the bounds of the board
    # 
    # PARAM [int] x: x-coordinate
    # PARAM [int] y: y-coordinate
    # PARAM [board.Board] brd: board to check location on
    def valid_loc(self, x, y, brd):
        """Returns true if the coordinate is withing the bounds of the board"""
        return 0 <= x < len(brd.board) and 0 <= y < len(brd.board[0])
