import random

# Perform Crossover
#
# PARAM [tuple(float, float, float)] parent1 : genotype of first parent
# PARAM [tuple(float, float, float)] parent2 : genotype of second parent
# PARAM [function(parent1, parent2)] func : crossover function to use
# RETURN [tuple(float, float, float)] : genotype of offspring
def crossover(parent1, parent2, func):
    """Perform crossover with given function"""
    return func(parent1, parent2)

# K-Point Crossover
#
# PARAM [tuple(float, float, float)] parent1 : genotype of first parent
# PARAM [tuple(float, float, float)] parent2 : genotype of second parent
# PARAM [int] k : number of points to cross at
# RETURN [tuple(float, float, float)] : genotype of offspring
def k_point_cross(parent1, parent2, k=None):
    """Perform k-point crossover and return the offspring"""
    num_genes = len(parent1)
    points = set()
    if k is None:
        k = random.randrange(1, num_genes)
    elif k > num_genes:
        k = num_genes

    # Select random crossover points until k points are picked
    while len(points) < k:
        if k == 1:
            # If there's only one point, don't switch and pick all parent2
            point = random.randrange(1, num_genes)
        else:
            point = random.randrange(0, num_genes)
        points.add(point)

    genes = []
    p = 0

    # Select genes
    for i in range(num_genes):
        if i in points:
            # Crossover point, switch current parent
            p = (p + 1) % 2
        if p == 0:
            genes.append(parent1[i])
        else:
            genes.append(parent2[i])
    
    return tuple(g for g in genes)
        
# Uniform Crossover
#
# PARAM [tuple(float, float, float)] parent1 : genotype of first parent
# PARAM [tuple(float, float, float)] parent2 : genotype of second parent
# RETURN [tuple(float, float, float)] : genotype of offspring
def uniform_cross(parent1, parent2):
    """Perform uniform crossover and return the offspring"""
    genes = []
    num_genes = len(parent1)
    for i in range(num_genes):
        # Flip a coin for which parent for each gene
        p = random.randint(1,2)
        if p == 1:
            genes.append(parent1[i])
        else: 
            genes.append(parent2[i])
    return tuple(g for g in genes)
