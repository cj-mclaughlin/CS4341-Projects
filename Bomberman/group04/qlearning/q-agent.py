import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

from entity import CharacterEntity
from actions import Action

# TODO implement
class QAgent(CharacterEntity):
    def __init__(self):
        self.weights = []
        self.feature_functions = []

    # TODO evaluate the quality of the current move using the feature functions and weights
    def evaluate_move(self, action):
        pass

if __name__ == "__main__":
    print("Imports passed")
    
    