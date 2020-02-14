import os,sys,inspect,time,random
# leaving imports like this so its very obvious where functions are coming from for right now
import crossover
import mutation
import selection
# importing packages from parent directory
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
import game # pylint: disable=import-error
import agent # pylint: disable=import-error
import alpha_beta_agent as aba # pylint: disable=import-error
import ast
import copy

DATA_FILE_NAME = "final-data.txt"

# Define Genotype as Tuple (adj_util_scale, opp_util_scale, win_util_scale)

# Generate Random Initial Population
#
# PARAM [int] size : number of individuals for population
# RETURN [list(tuple(float, float, float))] : list of genotypes for the population
def random_population(size):
    """Randomly generated population"""
    population = []
    for i in range(size):
        population.append((random.uniform(-1,1), random.uniform(-1,1), random.uniform(0,1))) # random genotypes for starting pop - discuss later
    return population

def genetic_algorithm(init_population, fitness_fn):
    return 0 # TODO implement something that runs until we stop it (no specified end condition)

# Run Genetic Algorithm til Depth Threshold
#
# PARAM [list(tuple(float, float, float))] init_population : starting population
# PARAM [int] max_generations : how many generations to run
# PARAM [function(list(tuple(float, float, float), int))] selection_fn : which selection/fitness to run (default - pooled tournament)
# RETURN [list(tuple(float, float, float))] : the most fit individuals after max_generations
def depth_constrainted_genetic(init_population, max_generations, selection_fn=selection.pooled_tournament):
    """Runs genetic algorithm for set number of generations"""
    size_generation = len(init_population)
    survivors_per_generation = 2 # TODO discuss - could be size_generation/2, etc
    past_gen = init_population
    for g in range(1, max_generations+1):
        print("Generation {} begins with: {}".format(g, past_gen))
        # TODO discuss how many parents to have and how to determine which pairs will crossover? Random?
        survivors = selection_fn(past_gen, survivors_per_generation)
        #print(survivors)
        child = crossover.crossover(survivors[0], survivors[1], crossover.uniform_cross)
        next_gen = copy.deepcopy(survivors)
        for i in range(size_generation - survivors_per_generation):
            next_gen.append(mutation.mutate_genotype(child, g))
        past_gen = next_gen
    # TODO keep track of best from generations, (note: survivors should be sorted in order of fitness) -- have some tournament for returning best individual
    # Alternatively, we could just take the one with the best results from pools (we would have to store the scores from the selection fn)
    
    print(f'Survivors {survivors}')
    write_to_file(survivors, DATA_FILE_NAME) # write final data
    read_winners(DATA_FILE_NAME)
    return survivors # decide if this should be past_gen, etc

# Write genome data to file
#
# PARAM [list(tuple(float, float, float))] data : genomes to record
# PARAM [string] filename : file to write the data to
def write_to_file(data, filename):
    """Writes a list of genomes to the specified file"""
    with open(filename, 'a+') as f:
        for line in data:
            f.write(f'{str(line)}\n')
    f.close()

# Read genome data from file
#
# PARAM [string] filename : file to write the data to
# RETURN [list(tuple(float, float, float))] : genomes from each line of the file
def read_winners(filename):
    """Returns a list of genomes read from the specified file"""
    f = open(filename)
    lines = [ast.literal_eval(line.strip()) for line in f.readlines()]
    f.close()
    return lines

if __name__ == "__main__":
    tup = read_winners(DATA_FILE_NAME)
    start = time.time()
    population_size = 16
    max_generations = 100
    init_population = random_population(population_size)
    print(depth_constrainted_genetic(init_population, max_generations))
    total_time = time.time() - start
    print("Running {} generations on population size {} took {} seconds".format(max_generations, population_size, total_time))