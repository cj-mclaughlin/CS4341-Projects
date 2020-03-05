import sys, os
import random
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')
sys.path.insert(2, '.')

from game import Game
from qlearning import q_agent
import rewardfunctions
import pygame as pg
from events import Event

from monsters.stupid_monster import StupidMonster
from monsters.selfpreserving_monster import SelfPreservingMonster


# Class responsible for reinforcement learning of a specified agent
class Trainer():
    def __init__(self, agent, weightsfile="bomberman_weights.txt"):
        self.agent = agent
        self.weightsfile = weightsfile
    
    # Vlad
    # Takes the current agent and plays each scenario 10 times
    # Then returns the winrate for each scenario
    def evaluate_winrate(self):
        num_runs_per_scenario = 10
        num_maps = 2
        num_situations = 5
        
        exploration = self.agent # old agent to remember
        old_weights = exploration.weights
        
        # create exploitation agent with same weights
        test_agent = q_agent.ExploitationAgent("me", "C", 0, 0)
        test_agent.set_weights(old_weights)
        
        self.agent = test_agent
        
        scenario_winrate = {
            1: 0,
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
                # print(f'map_idx: {map_idx} situation_idx: {situation_idx}')
                scenarios.append(self.select_scenario(seed = (map_idx, situation_idx)))

        # Loop through playing scenarios and get win rate for each scenario
        for i in range(len(scenarios)):
            num_wins = 0
            for j in range(num_runs_per_scenario):
                won = scenarios[i].go(freeze_weights = True)
                if(won):
                    num_wins += 1
            
            scenario_winrate[i] = num_wins/num_runs_per_scenario
            
        # set our agent back to the exploration agent
        self.agent = exploration    
        
        return scenario_winrate
   
    # Vlad
    # Train the agent that is  
    def train(self):
        # select scenarios
        num_episodes = 25
        num_generations = 25
        for generation_number in range(num_generations):
            self.run_generation(num_episodes)
            self.write_progress(generation_number) 
            
            # check for convergence
            if (self.agent.alpha < 0.1):
                print("Stopping early due to alpha convergence")
                break
    
    def run_generation(self, num_episodes):
        episodes = self.select_scenarios(num_episodes)
        for episode in episodes:
            # Reset agent position
            self.agent.x, self.agent.y = 0, 0
            episode.go(freeze_weights = False)
            
        # update alpha value -- TODO consider updating this like epsilon instead
        self.agent.increment_generation()
        self.agent.update_alpha()
        self.agent.update_epsilon()

    def select_scenarios(self, num_scenerios):
        scenarios = []
        for i in range(0, num_scenerios):
            scenarios.append(self.select_scenario())
        return scenarios

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
        #self.agent.x, self.agent.y = 0, 12 # TODO test with placing it closer to the exit
        g.set_agent(self.agent)
        g.set_reward_function(self.reward)

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
            else:
                f.write("Generation # | Alpha, Epsilon | Weights [Dist_Exit, Dist_Monster, Move_to_Gap, Bomb_Danger_Zone, Blocking_Wall_In_Bomb_Range] | Winrate\n")
            f.write("Generation {0} | {1:.3f}, {2:.5f} | Weights {3} | Winrate {4}\n".format(
                generation_number,
                self.agent.alpha,
                self.agent.epsilon,
                self.agent.weights,
                winrate))

    # Get the reward value for a given state and new events
    # PARAM[SensedWorld] state: the current state of the map
    # PARAM[list(Event)] events: the events that transpired in the last step
    def reward(self, state, events):
        return rewardfunctions.reward(state, events, self.agent)
    
class TrainingGame(Game):
    def __init__(self, width, height, max_time, bomb_time, expl_duration, expl_range, sprite_dir="../../bomberman/sprites/"):
        super().__init__(width, height, max_time, bomb_time, expl_duration, expl_range, sprite_dir)
    
    def set_agent(self, agent):
        self.agent = agent
        super().add_character(self.agent)

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

        # self.draw()
        step()
        while not self.done():
            cur_state = self.world
            (self.world, self.events) = self.world.next()
            reward = self.reward_fn(self.world, self.events)
            if (not freeze_weights):
                self.agent.update_weights(reward, cur_state, self.world)
            # self.draw() # TODO uncomment after training
            step()
            self.world.next_decisions()
            # evaluate if win
            for event in self.events:
                if(event.tpe == Event.CHARACTER_FOUND_EXIT):
                    return True
        return False
