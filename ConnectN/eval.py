import random
import game
import agent
import sys
import alpha_beta_agent as aba

n_games = 100
total_wins = 0
losses = []
losing_games = []

def run_evaluation(agent1, agent2, n_games=100, total_wins=0, losses=[], losing_games=[]):
    for i in range(n_games):
        random.seed(i)
        g = game.Game(7, # width
                    6, # height
                    4, # tokens in a row to win
                    agent1,        # player 1
                    agent2)        # player 2
        outcome = g.go()
        if outcome == 2:
            total_wins+=1
        else:
            losses.append(i)
            losing_games.append(g)
    return (total_wins, losses, losing_games)

random_agent = agent.RandomAgent("random")
aba_agent1 = aba.AlphaBetaAgent("ab-agent1", 1)
aba_agent2 = aba.AlphaBetaAgent("ab-agent2", 2)
total_wins, losses, losing_games = run_evaluation(random_agent, aba_agent2, n_games, total_wins, losses, losing_games)

print("Player 2 Won {}, lost {} (winrate = {})".format(total_wins, n_games-total_wins, total_wins/n_games))
print("Seeds which we lost to: {}".format(losses))

print("See 'lost-games.txt' for final board state of all lost games")
sys.stdout = open("lost-games.txt", 'w')
for i in range(len(losing_games)):
    print("Final board for seed {}".format(losses[i]))
    losing_games[i].board.print_it()
    print("\n")
    
print("Seeds lost: {}".format(losses))