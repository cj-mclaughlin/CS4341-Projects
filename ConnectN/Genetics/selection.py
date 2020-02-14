import os,sys,inspect,random
from heapq import nlargest
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
import alpha_beta_agent as aba # pylint: disable=import-error
import game # pylint: disable=import-error

# Round Robin Tournament
#
# PARAM [list of tuples(weight1, weight2, weight3)] generation: list of this generations individuals (weights)
# PARAM [int] num_survivors: how many individuals to return after the tournament
# PARAM [int] max_depth: how far each individual should look while playing
# RETURN [list of tuples(weight1, weight2, weight3)]: survivors 
def round_robin_selection(generation, num_survivors, max_depth=4):
    """Runs round robin tournament w/generation and return genotypes carrying over to next generation"""
    # Initialize agents and their tournament results
    agents = [aba.AlphaBetaAgent(":v", max_depth, x) for x in generation]
    scores = {}
    for agent in agents:
        scores[agent] = 0
    # Play
    for i in range(0, len(agents)-1):
        for j in range(i + 1, len(agents)):
            (s1, s2) = play_match(agents[i], agents[j])
            scores[agents[i]] = scores[agents[i]] + s1
            scores[agents[j]] = scores[agents[j]] + s2
    # Return surviving population 
    survivor_agents = nlargest(num_survivors, scores, key = scores.get)
    survivors = []
    for s in survivor_agents:
        print("Agent with heuristic {} survives with result {}".format(s.weights(), scores[s]))
        survivors.append(s.weights())
    # TODO double check that survivors are being added in some order so at the end we know what our highest fitness is    
    return survivors

# Break generation into pools and play tournaments within the pools
#
# PARAM [list of tuples(float, float, float)] generation: list of this generations individuals (weights)
# PARAM [int] num_survivors: how many individuals to return after the tournament
# PARAM [int] max_depth: how far each individual should look while playing
# PARAM [int] n_pools: how many pools to separate the group into
# RETURN [list of tuples(float, float, float)]: survivors 
def pooled_tournament(generation, num_survivors, max_depth=4, n_pools=4): # TODO decide if num_survivors should be used or always be the same as n_pools
    """Break population into pools which each play round robin tournament, return winners of each pool"""
    if len(generation) < 2*n_pools:
        print("Cannot have pooled tournament with {} pools and less than {} individuals".format(n_pools, 2*n_pools))
        return None
    if len(generation) % n_pools != 0:
        print("Cannot have even size pools with given parameters")
        return None
    # Break population into n pools
    pool_size = (int) (len(generation) / n_pools)
    random.shuffle(generation) # shuffle ordering of generation before creating pools
    pools = [generation[i:i+pool_size] for i in range(0, len(generation), pool_size)]
    pool_winners = []
    # Play round robin for each pool, return winners
    for pool in pools:
        pool_winners.append(round_robin_selection(pool, num_survivors=1, max_depth=max_depth)[0])
    # Play round robin with pool winners so we have our desired number of winners
    survivors = round_robin_selection(pool_winners, num_survivors, max_depth)
    return survivors

# Play match
#
# PARAM [agent.Agent] p1: the agent for Player 1
# PARAM [agent.Agent] p2: the agent for Player 2
# PARAM [int]         w:  the board width
# PARAM [int]         h:  the board height
# PARAM [int]         n:  the number of tokens to line up to win
# RETURN [tuple(int, int)]: pair containing net wins from match for (agent1, agent2)
def play_match(agent1, agent2, w=7, h=6, n=4):
    """Play 2 games, switching who plays first, return the scores"""
    # Play the games
    g1 = game.Game(w, h, n, agent1, agent2)
    g2 = game.Game(w, h, n, agent2, agent1)
    o1 = g1.go()
    o2 = g2.go()
    # Calculate scores
    s1 = 0
    s2 = 0
    if o1 == 1:
        s1 = s1 + 1
        s2 = s2 - 1
    elif o1 == 2:
        s1 = s1 - 1
        s2 = s2 + 1
    if o2 == 1:
        s1 = s1 - 1
        s2 = s2 + 1
    elif o2 == 2:
        s1 = s1 + 1
        s2 = s2 - 1
    return (s1, s2)
