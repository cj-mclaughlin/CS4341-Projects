import math
import agent
import math
import random
import board
from ast import literal_eval

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
        # Heuristic Weights (From Genetic Algorithm)
        self.adj_util_weight = 0.5
        self.opp_util_weight = 0.5
        self.win_util_weight = 0.5

    # Utility function
    #
    # PARAM [board.Board] brd: the current board state
    # RETURN [int]: utility value
    def utility(self, brd):
        """Heuristic function"""
        adj = self.adj_util_weight * self.adj_utility(brd)
        opp = self.opp_util_weight * self.opportunity_utility(brd)
        win = self.win_util_weight * self.is_game_completed_heuristic(brd)
        sum_util = adj + opp +win
        #print("Total utility = adjacent:{} + opportunity:{} + win:{} = {}".format(adj, opp, win, sum_util))
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

        # print('Utility from adjacent symbols: {}'.format(util))
        return util
    
    # Utility function based on potential lines crated
    #
    # PARAM [board.Board] brd: the current board state
    # RETURN [int]: utility value
    def opportunity_utility(self, brd):
        """Opportunity heuristic function"""
        util = 0
        chain_mappings = self.number_in_a_row(brd)
        # util is sum of length^2 * chain
        for key in chain_mappings.keys():
            util += key * key * chain_mappings[key] 
        # print('Utility from opportunity (chains of symbols): {}'.format(util))
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
                # add found chains to running tally
                for i in range(4): # tuple size 4
                    if curr_chains[i] >= 2 and curr_chains[i] < brd.n:
                        chains[curr_chains[i]] += 1                    
        
        # remove double counted chains (every 3 chain is also being counted as a 2 chain -- could fix this in find_chains method or here)
        for i in range(brd.n, 2, -1):
            chains[i-1] -= chains[i]

        #print("Mapping of consecutive symbols found: {}".format(chains)) 
        return chains
        
    def is_game_completed_heuristic(self, brd):
        outcome = brd.get_outcome()
        if outcome == self.player:
            return 1000
        elif outcome == 0:
            return 0
        else:
            return -1000

    # Return tuple (chain_w, chain_h) containing the number of consecutive similar symbols in positive w/h direction starting from location w,h
    def find_chains(self, brd, w, h):
        """ Find number of consecutive similar tiles in positive directions"""
        symbol = brd.board[w][h]
        other_player = 0
        if symbol != self.player: # if it is not our symbol, we dont care to check
            return (0, 0, 0, 0)
        if self.player == 1:
            other_player = 2
        else:
            other_player = 1
        chain_w = 1
        chain_h = 1
        chain_diag_pos = 1
        chain_diag_neg = 1
        # check in the y (w) direction
        while (self.valid_loc(w + chain_w,h, brd) and brd.board[w + chain_w][h] == self.player):
            chain_w += 1
            if not self.valid_loc(w + chain_w, h, brd) or brd.board[w + chain_w][h] == other_player: # chains shouldn't count if blocked by opponent or going out of bounds
                chain_w = 0
                break
        # check in the x (h) direction
        while (self.valid_loc(w,h + chain_h, brd) and brd.board[w][h + chain_h] == self.player):
            chain_h += 1 
            if not self.valid_loc(w, h + chain_h, brd) or brd.board[w][h + chain_h] == other_player: # chains shouldn't count if blocked by opponent or going out of bounds
                chain_h = 0
                break
        # check in +y, +h direction 
        while (self.valid_loc(w + chain_diag_pos, h + chain_diag_pos, brd) and brd.board[w + chain_diag_pos][h + chain_diag_pos] == self.player):
            chain_diag_pos += 1 
            if not self.valid_loc(w + chain_diag_pos, h + chain_diag_pos, brd) or brd.board[w + chain_diag_pos][h + chain_diag_pos] == other_player: # chains shouldn't count if blocked by opponent or going out of bounds
                chain_diag_pos = 0
                break
        # check in -y, h direction
        while (self.valid_loc(w + chain_diag_neg, h - chain_diag_neg, brd) and brd.board[w + chain_diag_neg][h - chain_diag_neg] == self.player):
            chain_diag_neg += 1 
            if not self.valid_loc(w + chain_diag_neg, h - chain_diag_neg, brd) or brd.board[w + chain_diag_neg][h - chain_diag_neg] == other_player: # chains shouldn't count if blocked by opponent or going out of bounds
                chain_diag_neg = 0
                break
        return (chain_w, chain_h, chain_diag_pos, chain_diag_neg)
        
    # Return max utility value 
    #
    # PARAM [board.Board] brd: current board state
    # PARAM [int] a: alpha value
    # PARAM [int] b: beta value
    # PARAM [int] current_depth: current depth
    # RETURN [int] max utility value
    def max_value(self, brd, a, b, current_depth):
        """Max value fn for alpha-beta search"""
        if self.terminal_test(brd, current_depth):
            return (self.utility(brd), -1)
        
        v = -math.inf
        argmax = 0

        for succ in self.get_successors(brd):
            new_board = succ[0]
            new_val = self.min_value(new_board, a, b, current_depth+1)[0]

            if new_val > v:
                v = new_val
                argmax = succ[1]

            if v >= b:
                return (v, argmax)
            a = max(a, v)

        return (v, argmax)
                
    # Return min utility value 
    #
    # PARAM [board.Board] brd: current board state
    # PARAM [int] a: alpha value
    # PARAM [int] b: beta value
    # PARAM [int] current_depth: current depth for 
    # RETURN [int] min utility value
    def min_value(self, brd, a, b, current_depth):
        """Min value fn for alpha-beta search"""
        if self.terminal_test(brd, current_depth):
            return (self.utility(brd), -1)

        v = math.inf
        argmin = 0

        for succ in self.get_successors(brd):
            new_board = succ[0]
            new_val = self.max_value(new_board, a,b, current_depth+1)[0]

            if new_val < v:
                v = new_val
                argmin = succ[1]
            
            if v <= a:
                return (v, argmin)
            b = min(b,v)

        return (v, argmin)

    # Perform search and return the best action for the given state.
    #
    # PARAM [board.Board] brd: the current board state
    # RETURN [int]: the column where the token must be added
    def alpha_beta_search(self, brd):
        """Search for the best move by evaluating available moves"""

        infinity = math.inf

        # Search for action with maximum value
        (max_val, max_action) = self.max_value(brd, -infinity, infinity, 0)
        
        print("Wonderful AI chose move {} with heuristic value {}".format(max_action, max_val))
        
        return max_action

    # Test if the board is in a terminal state
    #
    # PARAM [board.Board] brd: the current board state
    # RETURN [boolean]: true if the search is in a terminal state
    def terminal_test(self, brd, current_depth):
        # Checks if board is in terminal state
        outcome = brd.get_outcome()
        return outcome != 0 or (current_depth == self.max_depth)

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


def run_tests(heur_func):
    """Read board data from test-cases.txt file and apply heuristic function, printing the result"""
    aba = AlphaBetaAgent('Tester', 2)
    aba.player = 1

    with open('test-cases.txt') as fp:
        while fp.readline() is not '':
            w = int(fp.readline())
            h = int(fp.readline())
            n = int(fp.readline())
            
            board_data = []
            for i in range(h):
                line = fp.readline().strip()
                board_data.insert(0, literal_eval(line))
            brd = board.Board(board_data, w, h, n)
            brd.print_it()
            
            print(heur_func.__name__[0:8] + ': ', heur_func(aba, brd))
