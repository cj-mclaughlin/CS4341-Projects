from trainer import Trainer
from qlearning import q_agent

# Debug on small scenarios
if __name__ == "__main__":
    agent = q_agent.ExploitationAgent("me", "C", 0, 0)
    agent.set_weights([409.5, -58.7, 18.9, -41.4, 5.0])
    # agent.set_weights([558.8, -306.9, -11.3, -49.8, 3.0])
    # agent.set_weights([1, -5, -3, -5, 3])
    game = Trainer(agent).random_scenario()
    game.set_agent(agent)
    game.add_agent()
    game.go(wait=0, draw=True)