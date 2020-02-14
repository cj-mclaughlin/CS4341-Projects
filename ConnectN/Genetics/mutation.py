import random
import math

# Mutate entire genotype
#
# PARAM [tuple(float, float, float)] genotype : genotype (weights) that we are mutating
# PARAM [int] generation: which generation we are on
# RETURN [tuple(float, float, float)] : the mutated genotype
def mutate_genotype(genotype, generation):
    """Returns an entire mutated genome"""
    return (mutate_gene(genotype[0], generation), mutate_gene(genotype[1], generation), mutate_gene(genotype[2], generation))

# Mutate single gene
#
# PARAM [float] gene : value of the gene we are mutating
# PARAM [int] generation : which generation we are on
# RETURN [float] : mutated gene value
def mutate_gene(gene, generation):
    """Returns mutated gene"""
    new_gene = (0.1*select_random()) + gene
    return new_gene

# Mutate single gene w/exp decay factor
#
# PARAM [float] gene : value of the gene we are mutating
# PARAM [int] generation : which generation we are on
# RETURN [float] : mutated gene value
def mutate_gene_exp_decay(gene, generation):
    """Returns mutated gene"""
    new_gene = (scale_factor(generation, 0.25) * select_random()) + gene
    return new_gene
    
# Selects random number [-1,1]
#
# RETURN [float]: random value
def select_random():
    """Select random value between [-1,1] - distribution subject to change"""
    return random.uniform(-1, 1)

# Exponential Decay Scale Factor
#
# PARAM [int] generation : which generation we are on
# PARAM [int] exp_factor : coefficient for exponential decay (default 1 - no scaling)
# PARAM [int] upper_bound : upper bound of scale factor (default 1)
# PARAM [int] lower_bound : lower bound of scale factor
# RETURN [int] : scale factor 
def scale_factor(generation, exp_factor=1, upper_bound=1, lower_bound=0):
    """Returns scale factor at given generation"""
    sf = upper_bound * math.exp(-generation * exp_factor) + lower_bound
    return sf
