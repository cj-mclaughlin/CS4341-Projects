import random
import math

def mutate_gene(gene, generation):
    """Returns mutated gene"""
    new_gene = (scale_factor(generation) * select_random) + gene
    return new_gene
    
def select_random():
    """Select random value between [-1,1] - distribution subject to change"""
    return random.randrange(-1, 1)

def scale_factor(generation, exp_factor=1, upper_bound=1, lower_bound=0):
    """Returns scale factor at given generation"""
    sf = upper_bound * math.exp(-generation * exp_factor) + lower_bound
    return sf