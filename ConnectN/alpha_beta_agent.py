import math
import agent
import math
import random

###########################
# Alpha-Beta Search Agent #
###########################

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
        return random.randrange(1, 5) #TODO implement
    
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
            return a
        v = -math.inf
        for succ in self.get_successors(brd):
            new_board = succ[0]
            v = max(v, self.min_value(new_board, a, b, current_depth+1))
            if v >= b:
                return v
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
            return b
        for succ in self.get_successors(brd):
            new_board = succ[0]
            v = min(v, self.max_value(new_board, a,b, current_depth+1))
            if v < a:
                return v
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
            val = self.max_value(succ[0], infinity, -infinity, 1)
            
            # Update maximum valued action
            if val > max_val:
                max_val = val
                max_action = succ[1]
        
        print("Wonderful AI chose to move {}".format(max_action))
        
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
