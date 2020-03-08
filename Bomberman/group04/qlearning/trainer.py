import sys, os, copy
import random
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')
sys.path.insert(2, '.')

from game import Game
from qlearning import q_agent
import rewardfunctions
import pygame as pg
from events import Event

from trainingscenarios import TrainingScenario

from monsters.stupid_monster import StupidMonster
from monsters.selfpreserving_monster import SelfPreservingMonster


# Class responsible for reinforcement learning of a specified agent
class Trainer():
    def __init__(self, agent, weightsfile="bomberman_weights.txt"):
        self.agent = agent
        self.weightsfile = weightsfile
    
    # Evaluation of agent against sub scenarios
    # PARAM[filename] training_pickle: serialized copy of list of scenarios we want to train against
    def evaluate_winrate(self):
        num_scenarios = 3
        num_runs_per_scenario = 5
        
        old_epsilon = self.agent.epsilon

        # Use an Exploitation Agent
        exploitation = q_agent.ExploitationAgent("me", "C", 0, 0)
        exploitation.set_weights(copy.deepcopy(self.agent.weights))
        self.agent = exploitation
        
        # TODO potentially serialize scenarios
                
        scenario_winrate = {i: 0 for i in range(num_scenarios)}

        # Loop through playing scenarios and get win rate for each scenario
        for i in range(num_scenarios):
            num_wins = 0
            for j in range(num_runs_per_scenario):
                # Create scenario
                map_file = "scenarios/map"+str(i + 6)+".txt"
                g = TrainingScenario.fromfile(map_file)
                
                # Random drop agent and a monster
                # Drop agent in first or second row
                self.agent.x, self.agent.y = random.randrange(0, g.world.width()), random.randint(0,1)

                g.set_reward_function(self.reward)
                
                max_x = max(g.world.width(), self.agent.x+5)
                monster_x, monster_y = random.randrange(0, g.world.width()), random.randint(self.agent.y+5, self.agent.y+6)

                # TODO think if we should include stupid monsters
                g.add_monster(SelfPreservingMonster("selfpreserving", "S", monster_x, monster_y, 2))

                g.set_agent(self.agent)

                print('game', i, 'run', j)
                g.add_agent() # add its agent to the game
                # Drop agent in first or second row
                self.agent.x, self.agent.y = random.randrange(0, g.world.width()), random.randint(0,1)
                won = g.go(freeze_weights = True)
                if(won):
                    num_wins += 1
            
            scenario_winrate[i] = num_wins/num_runs_per_scenario
        
        exploration = q_agent.ExplorationAgent("me", "C", 0, 0)
        exploration.set_weights(copy.deepcopy(self.agent.weights))
        exploration.epsilon = old_epsilon
        self.agent = exploration
        
        return scenario_winrate
   
    # Train the agent that is  
    def train(self):
        # select scenarios
        num_episodes = 10 # TODO make this 1? idk
        num_generations = 30

        # (for now) generate random pool of scenarios
        # scenarios = []
        # for i in range(num_episodes):
        #     scenarios.append(self.random_scenario())
        
        for generation_number in range(num_generations):
            # self.run_generation(num_episodes, scenarios) # running all scenarios from pool
            self.run_generation(num_episodes)
            self.write_progress(generation_number)
    

    def run_generation(self, num_episodes):
        for i in range(num_episodes):
            testingscenario = self.random_scenario()
            testingscenario.set_agent(self.agent)
            testingscenario.add_agent()
            testingscenario.go(wait=1, freeze_weights=False)
        self.agent.update_epsilon()


    # def run_generation(self, num_episodes, pool_scenarios):
    #     episodes = self.select_scenarios(num_episodes, pool_scenarios)
    #     for episode in episodes:
    #         episode.go(freeze_weights = False)
            
    #     # update epsilon value
    #     self.agent.update_epsilon()
        
        
    # select num_scenarios from pool_scenarios
    # PARAM[int] num_scenarios: how many to choose
    # PARAM[list:TrainingScenario]: which games to choose from
    def select_scenarios(self, num_scenerios, pool_scenarios):
        return random.choices(pool_scenarios, k=num_scenerios)

    # Generate a random training scenario
    # PARAM [Boolean] exploitation: whether or not to run the scenario in exploration or exploitation
    def random_scenario(self):
        # maps
        p, d, mapfiles = next(os.walk("scenarios/"))
        maps = ["scenarios/map"+str(i)+".txt" for i in range(7,len(mapfiles)+1)]
        
        # Select Map
        rand_map = maps[random.randrange(0,3)]

        # Game object
        g = TrainingScenario.fromfile(rand_map)
        
        # Random drop agent and a monster
        # Drop agent in first or second row
        self.agent.x, self.agent.y = random.randrange(0, g.world.width()), random.randint(0,1)

        g.set_reward_function(self.reward)
        
        max_x = max(g.world.width(), self.agent.x+5)
        monster_x, monster_y = random.randrange(0, g.world.width()), random.randint(self.agent.y+5, self.agent.y+6)

        # TODO think if we should include stupid monsters
        g.add_monster(SelfPreservingMonster("selfpreserving", "S", monster_x, monster_y, 2))

        g.set_agent(self.agent)

        return g
            
    
    # Output data to file
    def write_progress(self, generation_number):
        # check if we are creating or appending
        file_exists = False
        if os.path.exists(self.weightsfile):
            file_exists = True # should be appending to weights file
        
        # write winrate to file
        winrate = self.evaluate_winrate()
        with open(self.weightsfile, 'a+') as f:
            if not file_exists:
                f.write("Generation ## | Epsilon | Dist_Exit Dist_Monster Vector_Threat Bomb_Threat No_Path | Winrate\n\n")
            
            f.write("Generation {0:2d} | {1:.5f} | {2:7.1f} {3:7.1f} {4:7.1f} {5:7.1f} {6:7.1f} | ".format(
                generation_number,
                self.agent.epsilon,
                *self.agent.weights))
            f.write("{}\n".format(winrate))         


    # Get the reward value for a given state and action
    # PARAM[SensedWorld] state: the current state of the map
    # PARAM[Action] action: the action to evaluate
    # PARAM[MovableEntity] character: the bomberman character this is evaluating for
    def reward(self, state, events):
        return rewardfunctions.reward(state, events, self.agent)