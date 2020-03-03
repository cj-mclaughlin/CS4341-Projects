import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

from game import Game
from qlearning import q_agent
import pygame as pg

# TODO potentially move to other file
class Trainer():
    def __init__(self, ExplorationAgent):
        self.agent = ExplorationAgent
    
    # Vlad
    # Takes the current agent and plays each scenario 10 times
    # Then saves information for each scenario and weights to a file
    def evaluate_winrate(self):
        # freeze weights and play scenarios
        # Create a queue of scenarios to play
        # Loop through playing scenarios and get win rate
        # Serialize win rate and agent paramters
        self.write_progress()
        pass

    
    # Vlad
    # Train the agent that is  
    def train(self):
        # select scenarios

        scenarios = self.select_scenarios() # assuming it gives more than one scenario

        # update weights while doing scenarios
        # write progress every output_frequency generations
        pass 
    
    def select_scenerios(self, num_scenerios):
        pass

    # Connor
    # TODO
    def select_scenario(self):
        pass
    
    # Connor
    # Output generation #, weights and current winrate after playing each scenarios 10x to file
    def write_progress(self):
        pass
    
    # Will (also decide if we want to look at a post-state action or take both the state and action and calulate resulting state)
    # TODO
    def reward(self, state, action):
        pass
    
class TrainingGame(Game):
    def __init__(self, width, height, max_time, bomb_time, expl_duration, expl_range, sprite_dir="../../bomberman/sprites/"):
        super().__init__(width, height, max_time, bomb_time, expl_duration, expl_range, sprite_dir)
        #self.agent = agent
    
    #Overload go function to run
    def go(self, wait=0):
        if wait is 0:
            def step():
                pg.event.clear()
                # print(featurefunctions.bomb_danger_zone(self.world, None))
                input("Press Enter to continue or CTRL-C to stop...")
        else:
            def step():
                pg.time.wait(abs(wait))

        #colorama.init(autoreset=True)
        #self.display_gui()
        self.draw()
        step()
        while not self.done():
            (self.world, self.events) = self.world.next()
            #self.display_gui()
            self.draw()
            step()
            self.world.next_decisions()
        #colorama.deinit()

if __name__ == "__main__":
    g = TrainingGame.fromfile('map.txt')

    # TODO Add your character
    agent = q_agent.ExploitationAgent
    g.add_character(agent("me", # name
                                "C",  # avatar
                                0, 0  # position
    ))

    # Run!
    g.go(wait = 1)
    print("All imports are a go")
