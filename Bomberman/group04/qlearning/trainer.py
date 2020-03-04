import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')
sys.path.insert(2, '.')

from game import Game
from qlearning import q_agent
import rewardfunctions
import pygame as pg
from events import Event

# Class responsible for reinforcement learning of a specified agent
class Trainer():
    def __init__(self, agent):
        self.agent = agent
    
    # Vlad
    # Takes the current agent and plays each scenario 10 times
    # Then returns the winrate for each scenario
    def evaluate_winrate(self):
        num_runs_per_scenario = 10
        scenario_winrate = {
            1 : 0,
            2: 0,
            3: 0,
            4 : 0,
            5: 0,
            6: 0,
            7 : 0,
            8: 0,
            9: 0,
            10: 0
        }
        # Create a queue of scenarios to play
        #TODO after have all scenarios accessible
        scenarios = []
        # Loop through playing scenarios and get win rate for each scenario
        for i in range(len(scenarios)):
            num_wins = 0
            for j in range(num_runs_per_scenario):
                won = scenarios[i].go(freeze_weights = True)
                if(won):
                    num_wins += 1
            scenario_winrate[i] = num_wins/num_runs_per_scenario
        return scenario_winrate
   
    # Vlad
    # Train the agent that is  
    def train(self):
        # select scenarios
        num_episodes = 25
        num_generations = 10
        for generation_number in range(num_generations):
            self.run_generation(num_episodes)
            self.write_progress() 
    
    def run_generation(self, num_episodes):
        episodes = self.select_scenarios(num_episodes)
        for episode in episodes:
            episode.go(freeze_weights = False)


    def select_scenarios(self, num_scenerios):
        scenarios = []
        for i in range(0, num_scenerios):
            scenarios.append(self.select_scenario())
        return scenarios

    # Connor
    # TODO
    def select_scenario(self):
        TrainingGame.fromfile('map.txt')
    
    # Connor
    # Output generation #, weights and current winrate after playing each scenarios 10x to file
    def write_progress(self):
        pass
    
    # Will (also decide if we want to look at a post-state action or take both the state and action and calulate resulting state)
    # TODO
    def reward(self, state, action):
        return rewardfunctions.reward(state, action)
    
class TrainingGame(Game):
    def __init__(self, width, height, max_time, bomb_time, expl_duration, expl_range, sprite_dir="../../bomberman/sprites/"):
        super().__init__(width, height, max_time, bomb_time, expl_duration, expl_range, sprite_dir)
    
    def set_agent(self, agent):
        self.agent = agent

    def set_reward_function(self, reward_fn):
        self.reward_fn = reward_fn

    # Overload go function to run
    # RETURN [Boolean]: whether or not the game was completed by the agent
    def go(self, wait=1, freeze_weights = True):
        if wait is 0:
            def step():
                pg.event.clear()
                # print(featurefunctions.bomb_danger_zone(self.world, None))
                input("Press Enter to continue or CTRL-C to stop...")
        else:
            def step():
                pg.time.wait(abs(wait))

        self.draw()
        step()
        while not self.done():
            (self.world, self.events) = self.world.next()
            self.draw()
            step()
            self.world.next_decisions()
            #TODO evaluate if win
            print('Searching events')
            for event in self.events:
                if(event.tpe == Event.CHARACTER_FOUND_EXIT):
                    return True
        return False

if __name__ == "__main__":
    # agent = q_agent.ExploitationAgent("me", "C", 0, 0)
    # trainer = Trainer(agent)
    # trainer.train()

    #Testing for custom game
    g = TrainingGame.fromfile('map.txt')

    # TODO Add your character
    agent = q_agent.ExploitationAgent
    g.add_character(agent("me", # name
                                "C",  # avatar
                                0, 0  # position
    ))

    # Run!
    print(g.go(wait = 0))

