# In ipd_simulation/genetic_backend.py

import random
from ipd_simulation.strategies import COOPERATE, DEFECT
from ipd_simulation.match_tournament import run_match


# Generates all possible sequences of length of n of COOPERATE and DEFECT
def all_combinations(n):
    combos = []

    for i in range(2 ** n):
        combo = []

        # Convert the number to a binary representation determining choices
        for j in range(n):
            if (i >> (n - j - 1)) & 1:
                combo.append(DEFECT)  # DEFECT if the bit is 1
            else:
                combo.append(COOPERATE)  # COOPERATE if the bit is 0
        combos.append(tuple(combo))

    return combos


# Creates a random strategy
def random_individual():
    # Random opening for the first three moves
    opening = [random.choice([COOPERATE, DEFECT]) for _ in range(3)]

    rule_table = {}

    # Generate all possible histories for self and opponent
    my_combinations = all_combinations(3)
    opponent_combinations = all_combinations(3)

    # Assign a random response for each combination of history
    for my_moves in my_combinations:
        for opponent_moves in opponent_combinations:
            rule_table[(my_moves, opponent_moves)] = random.choice([COOPERATE, DEFECT])

    return {"opening": opening, "rule_table": rule_table}


# Converts a rule table into a fuction
def make_genetic_strategy(individual):
    def strategy(my_history, opponent_history):
        # If less than 3 rounds played use opening
        if len(my_history) < 3:
            return individual['opening'][len(my_history)]

        # Moves from myself and the opponent for the last 3 rounds
        my_last_moves = (my_history[-3], my_history[-2], my_history[-1])
        opponent_last_moves = (opponent_history[-3], opponent_history[-2], opponent_history[-1])

        # If my last 3 moves and opponents last 3 moves are in the rule table
        # then return the resulting next move
        if (my_last_moves, opponent_last_moves) in individual['rule_table']:
            return individual['rule_table'][(my_last_moves, opponent_last_moves)]
        else:
            return COOPERATE
    return strategy


# Evaluate the performance of an algorithm
def evaluate_individual(individual, opponents, rounds):
    # Play against each opponent that was passed along with this function
    # and calculate the total payoff
    individual = make_genetic_strategy(individual)
    total = 0

    for opponent in opponents.values():
        _, _, score, _ = run_match(individual, opponent, rounds)
        total += score
    return total


# Select survivors based on fitness
def select_survivors(population, fitnesses, survivor_count):
    pairs = []

    # Pair each strategy with its fitness
    for i in range(len(population)):
        pairs.append((fitnesses[i], population[i]))

    # Sort the list with pairs based on fitness
    pairs.sort(reverse=True, key=lambda pair: pair[0])

    survivors = []
    for i in range(survivor_count):
        survivors.append(pairs[i][1])

    return survivors


# Does crossover between two parents and then creates a new child
def crossover(parent1, parent2):
    new_opening = []
    # Create new opening sequence by randomly picking from parents
    for i in range(3):
        move = random.choice([parent1['opening'][i], parent2['opening'][i]])
        new_opening.append(move)


    new_rule_table = {}
    # Create new rule table by randomly picking rules from parents
    for move_history in parent1['rule_table']:
        parent1_move = parent1['rule_table'][move_history]
        parent2_move = parent2['rule_table'][move_history]

        child_move = random.choice([parent1_move, parent2_move])

        new_rule_table[move_history] = child_move

    return {"opening": new_opening, "rule_table": new_rule_table}


# Mutates a strategy by the given mutation rate
def mutate(individual, mutation_rate=0.05):
    new_opening = []
    # Mutate opening of rule table
    for move in individual['opening']:
        if move == COOPERATE and random.random() < mutation_rate:
            new_opening.append(DEFECT)
        elif move == DEFECT and random.random() < mutation_rate:
            new_opening.append(COOPERATE)
        else:
            new_opening.append(move)
    individual['opening'] = new_opening

    # Mutate the rule table
    for key in individual['rule_table']:
        if random.random() < mutation_rate:
            current = individual['rule_table'][key]
            individual['rule_table'][key] = DEFECT if current == COOPERATE else COOPERATE

    return individual


# Performs one step in the genetic algorithm
def genetic_algorithm_step(population, opponents, rounds, mutation_rate, survivor_fraction, elite_count):
    # Fitness of each individual
    fitnesses = [evaluate_individual(ind, opponents, rounds) for ind in population]

    best_individual = None
    best_fitness = float('-inf')

    # Find best individual and corresponding fitness
    for i in range(len(population)):
        if fitnesses[i] > best_fitness:
            best_fitness = fitnesses[i]
            best_individual = population[i]

    # Make new population based on the survivor fraction and pick an elite
    survivor_count = int(len(population) * survivor_fraction)
    survivors = select_survivors(population, fitnesses, survivor_count)
    new_population = survivors[:elite_count]

    # Fill the rest of the spots left in the population with mutated survivors
    while len(new_population) < len(population):
        parent1 = random.choice(survivors)
        parent2 = random.choice(survivors)
        child = crossover(parent1, parent2)
        child = mutate(child, mutation_rate)
        new_population.append(child)
    return new_population, best_individual, best_fitness


# Runs the full genetic
def genetic_algorithm(opponents, population_size, num_generations, rounds, mutation_rate, survivor_fraction, elite_count):
    # Make a population of random strategies
    population = [random_individual() for _ in range(population_size)]

    best_individual = None
    best_fitness = float('-inf')

    # Run the genetic algorithm for 'num_generations' generations
    for generation in range(num_generations):
        population, current_best_individual, current_best_fitness = genetic_algorithm_step(
            population, opponents, rounds, mutation_rate, survivor_fraction, elite_count)

        # Update best fitness if the best fitness of the latest generation
        # is greater than previous best fitnesses
        if current_best_fitness > best_fitness:
            best_fitness = current_best_fitness
            best_individual = current_best_individual

        print(f"Generation {generation}: Best Fitness = {current_best_fitness}")
    return best_individual, best_fitness
