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
    def evaluate_winrate(self, training_pickle):
        num_runs_per_scenario = 10
        num_maps = 2
        num_situations = 5
        
        # Use an Exploitation Agent
        exploitation = q_agent.ExploitationAgent("me", "C", 0, 0)
        exploitation.set_weights(copy.deepcopy(self.agent.weights))
        self.agent = exploitation
        
        # Use pickled list of training scenarios
        scenarios = []
        # unpickle list of training scenarios into list
        
        scenario_winrate = {i: 0 for i in scenarios}

        # Loop through playing scenarios and get win rate for each scenario
        for i in range(len(scenarios)):
            num_wins = 0
            for j in range(num_runs_per_scenario):
                won = scenarios[i].go(freeze_weights = True)
                if(won):
                    num_wins += 1
            
            scenario_winrate[i] = num_wins/num_runs_per_scenario
        
        exploration = q_agent.ExplorationAgent("me", "C", 0, 0)
        exploration.set_weights(copy.deepcopy(self.agent.weights))
        self.agent = exploration
        
        return scenario_winrate
   
    # Train the agent that is  
    def train(self):
        # select scenarios
        num_episodes = 12 # TODO make this 1? idk
        num_generations = 50

        # (for now) generate random pool of scenarios
        scenarios = []
        for i in range(num_episodes):
            scenarios.append(self.random_scenario())
        
        for generation_number in range(num_generations):
            self.run_generation(num_episodes, scenarios) # running all scenarios from pool
            self.write_progress(generation_number) 

    def run_generation(self, num_episodes, pool_scenarios):
        episodes = self.select_scenarios(num_episodes, pool_scenarios)
        for episode in episodes:
            # Reset agent position
            self.agent.x, self.agent.y = 0, 0
            episode.go(freeze_weights = False)
            
        # update epsilon value
        self.agent.update_epsilon()
        
        
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
        maps = ["scenarios/map"+str(i)+".txt" for i in range(1,len(mapfiles)+1)]
        
        # Select Map
        rand_map = maps[random.randint(1,len(mapfiles)+1)]

        # Game object
        g = TrainingScenario.fromfile(rand_map)
        
        # Random drop agent and a monster
        # Drop agent in first or second row
        self.agent_x, self.agent_y = random.randint(0,TrainingScenario.world.width()), random.randint(0,1)

        g.set_reward_function(self.reward)
        
        max_x = max(g.width(), self.agent_x+5)
        monster_x, monster_y = random.randint(0, g.width()), random.randint(self.agent_y+5, self.agent_y+6)

        # TODO think if we should include stupid monsters
        g.add_monster(SelfPreservingMonster("selfpreserving", "S", monster_x, monster_y, 2))
        
        return g
            
    
    # Output data to file
    def write_progress(self, generation_number):
        # check if we are creating or appending
        file_exists = False
        if os.path.exists(self.weightsfile):
            file_exists = True # should be appending to weights file
        
        # write winrate to file
        #winrate = self.evaluate_winrate()
        with open(self.weightsfile, 'a+') as f:
            if (not file_exists):
                f.write("Generation # | Epsilon | Weights [ TODO ] | Winrate\n")
            # TODO write agent generation and winrate etc ...

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
            self.draw() # TODO uncomment after training
            step()
            self.world.next_decisions()
            # evaluate if win
            for event in self.events:
                if(event.tpe == Event.CHARACTER_FOUND_EXIT):
                    return True
        return False
