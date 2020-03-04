import trainer
from qlearning import q_agent


if __name__ == "__main__":
    agent = q_agent.ExplorationAgent("me", "C", 0, 0)
    trainer = trainer.Trainer(agent)
    print("Beginning Training.\n")
    trainer.train()