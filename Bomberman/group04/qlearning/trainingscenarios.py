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


class TrainingScenario(Game):
    # Initializes a Training Scenario Object
    # PARAM[int] width: the width of the board to initialize
    # PARAM[int] height: the height of the board to initialize
    # PARAM[int] max_time: the max time this game will be played
    # PARAM[int] bomb_time: the fuse length of the bombs in this game
    # PARAM[int] expl_duration: the length of time an explosion will stay on the map
    # PARAM[int] expl_range: how far in each direction the explosion will go
    # PARAM[string] sprite_dir: the directory where sprite bitmaps are stored
    def __init__(self, width, height, max_time, bomb_time, expl_duration, expl_range, sprite_dir="../../bomberman/sprites/"):
        super().__init__(width, height, max_time, bomb_time, expl_duration, expl_range, sprite_dir)

    # set agent for scenario
    # PARAM[MovableEntity] agent: the agent which will be used in this game
    def set_agent(self, agent):
        self.agent = agent

    # add the agent to the game
    def add_agent(self):
        super().add_character(self.agent)

    # Sets the function that can be called to get a reward for each game state
    # PARAM[function] reward_fn: the function which will be called to get a reward
    def set_reward_function(self, reward_fn):
        self.reward_fn = reward_fn

    # Overload go function to run
    # PARAM [int] wait: length of time to wait before the next step is completed. If 0 passed in wait for enter to be pressed before continuing
    # PARAM [boolean] freeze_weights: Whether or not weights should be changed throughout this game
    # PARAM [boolean] draw: whether to draw the game board each turn
    # RETURN [Boolean]: whether or not the game was completed by the agent
    def go(self, wait=1, freeze_weights = True, draw=False):
        if wait == 0:
            def step():
                pg.event.clear()
                # print(featurefunctions.bomb_danger_zone(self.world, None))
                input("Press Enter to continue or CTRL-C to stop...")
        else:
            def step():
                pg.time.wait(abs(wait))

        if (draw):
            self.draw()
        step()
        while not self.done():
            cur_state = self.world
            (self.world, self.events) = self.world.next()
            if not freeze_weights:
                self.agent.update_weights(self.reward_fn, cur_state, self.world)
            if (draw):
                self.draw()
            step()
            self.world.next_decisions()
            # evaluate if win
            for event in self.events:
                if(event.tpe == Event.CHARACTER_FOUND_EXIT):
                    return True
        return False
