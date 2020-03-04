import sys, os
import random
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

from game import Game
from qlearning import q_agent
import pygame as pg
from events import Event

from monsters.stupid_monster import StupidMonster
from monsters.selfpreserving_monster import SelfPreservingMonster
#TODO delete after debugging
import pdb

# Class responsible for reinforcement learning of a specified agent
class Trainer():
    def __init__(self, agent, weightsfile="bomberman_weights.txt"):
        self.agent = agent
        self.weightsfile = weightsfile
    
    # Vlad
    # Takes the current agent and plays each scenario 10 times
    # Then returns the winrate for each scenario
    def evaluate_winrate(self):
        num_runs_per_scenario = 1
        num_maps = 2
        num_situations = 5
        scenario_winrate = {
            1 : 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
            7: 0,
            8: 0,
            9: 0,
            10: 0
        }
        # Create a queue of scenarios to play
        scenarios = []
        for map_idx in range(num_maps):
            for situation_idx in range(num_situations):
                print(f'map_idx: {map_idx} situation_idx: {situation_idx}')
                scenarios.append(self.select_scenario(seed = (map_idx, situation_idx)))

        # Loop through playing scenarios and get win rate for each scenario
        for i in range(1, len(scenarios)):
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
            self.write_progress(generation_number) 
    
    def run_generation(self, num_episodes):
        episodes = self.select_scenarios(num_episodes)
        for episode in episodes:
            episode.go(freeze_weights = False)

    def select_scenarios(self, num_scenerios):
        scenarios = []
        for i in range(0, num_scenerios):
            scenarios.append(self.select_scenario())
        return scenarios

    # TODO verify if working :)
    # Select one of the 10 variants from the 5 situations and 2 maps
    # PARAM [Tuple] seed: the scenario that we want this to return in the format (MapIdx, Situation)
    def select_scenario(self, seed = None):
        # maps
        maps = ["trainingset/map1.txt", "trainingset/map2.txt"]
        
        # situations
        # 1 - no monster
        # 2 - stupid monster at (3,9)
        # 3 - self preserving monster at (3,9) with detection range 1
        # 4 - self preserving monster at (3,13) with detection range 2
        # 5 - stupid monster at (3,5) and self preserving monster at (3,13) with detection range 2
                
        # TODO random selection
        # Select Map
        if(seed == None):
            rand_map = maps[random.randint(0,1)]
        else:
            rand_map = maps[seed[0]]
        # Select Situation / Create it
        if(seed == None):
            rand_situation = random.randint(1,5)
        else:
            rand_situation = seed[1]
        
        g = TrainingGame.fromfile(rand_map)
        g.add_character(self.agent)

        if (rand_situation == 2):
            g.add_monster(StupidMonster("stupid", "S", 3, 9))
        elif (rand_situation == 3):
            g.add_monster(SelfPreservingMonster("selfpreserving", "S",3, 9, 1))
        elif (rand_situation == 4):
            g.add_monster(SelfPreservingMonster("selfpreserving", "S",3, 13, 2))
        elif (rand_situation == 5):
            g.add_monster(StupidMonster("stupid", "S", 3, 5))
            g.add_monster(SelfPreservingMonster("selfpreserving", "S",3, 13, 2))
        
        return g
            
    
    # TODO verify if working :)
    # Output generation #, weights and current winrate after playing each scenarios 10x to file
    # PARAM [int] generation_number: which generation we are on
    def write_progress(self, generation_number):
        # check if we are creating or appending
        file_exists = False
        if os.path.exists(self.weightsfile):
            file_exists = True # should be appending to weights file
        
        # write winrate to file
        winrate = self.evaluate_winrate()
        with open(self.weightsfile, 'a+') as f:
            if (file_exists):
                f.write("\n")
            f.write("Generation {} | Weights {} | Winrate {}\n".format(generation_number, self.agent.weights, winrate))
        f.close()

    
    # Will (also decide if we want to look at a post-state action or take both the state and action and calulate resulting state)
    # TODO
    def reward(self, state, action):
        pass
    
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
            # evaluate if win
            for event in self.events:
                if(event.tpe == Event.CHARACTER_FOUND_EXIT):
                    return True
        return False

if __name__ == "__main__":
    agent = q_agent.ExploitationAgent("me", "C", 0, 0)
    trainer = Trainer(agent)
    print(f'Trainor created')
    print(f' winrate = {trainer.evaluate_winrate()}')
    #trainer.train()

