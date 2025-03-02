# In ipd_simulation/genetic_backend.py

import random
from ipd_simulation.strategies import COOPERATE, DEFECT
from ipd_simulation.match_tournament import run_match

def all_combinations(n):
    combos = []
    for i in range(2 ** n):
        combo = []
        for j in range(n):
            combo.append(DEFECT if (i >> (n - j - 1)) & 1 else COOPERATE)
        combos.append(tuple(combo))
    return combos

def random_individual():
    opening = [random.choice([COOPERATE, DEFECT]) for _ in range(3)]
    rule_table = {}
    self_combos = all_combinations(3)
    opp_combos = all_combinations(3)
    for self_moves in self_combos:
        for opp_moves in opp_combos:
            rule_table[(self_moves, opp_moves)] = random.choice([COOPERATE, DEFECT])
    return {"opening": opening, "rule_table": rule_table}

def make_genetic_strategy(individual):
    def strategy(my_history, opponent_history):
        if len(my_history) < 3:
            return individual['opening'][len(my_history)]
        my_last_moves = (my_history[-3], my_history[-2], my_history[-1])
        opponent_last_moves = (opponent_history[-3], opponent_history[-2], opponent_history[-1])
        if (my_last_moves, opponent_last_moves) in individual['rule_table']:
            return individual['rule_table'][(my_last_moves, opponent_last_moves)]
        else:
            return COOPERATE
    return strategy

def evaluate_individual(individual, opponents, rounds):
    candidate = make_genetic_strategy(individual)
    total = 0
    for opp in opponents.values():
        _, _, score, _ = run_match(candidate, opp, rounds)
        total += score
    return total

def select_survivors(population, fitnesses, survivor_count):
    paired_list = []
    for i in range(len(population)):
        paired_list.append((fitnesses[i], population[i]))
    paired_list.sort(reverse=True, key=lambda pair: pair[0])
    survivors = []
    for i in range(survivor_count):
        survivors.append(paired_list[i][1])
    return survivors

def crossover(parent1, parent2):
    child_opening = []
    for i in range(3):
        move = random.choice([parent1['opening'][i], parent2['opening'][i]])
        child_opening.append(move)
    child_rule_table = {}
    for move_history in parent1['rule_table']:
        child_rule = random.choice([parent1['rule_table'][move_history],
                                     parent2['rule_table'][move_history]])
        child_rule_table[move_history] = child_rule
    return {"opening": child_opening, "rule_table": child_rule_table}

def mutate(individual, mutation_rate=0.05):
    new_opening = []
    for move in individual['opening']:
        if move == COOPERATE and random.random() < mutation_rate:
            new_opening.append(DEFECT)
        elif move == DEFECT and random.random() < mutation_rate:
            new_opening.append(COOPERATE)
        else:
            new_opening.append(move)
    individual['opening'] = new_opening
    for key in individual['rule_table']:
        if random.random() < mutation_rate:
            current = individual['rule_table'][key]
            individual['rule_table'][key] = DEFECT if current == COOPERATE else COOPERATE
    return individual

def genetic_algorithm_step(population, opponents, rounds, mutation_rate, survivor_fraction, elite_count):
    """
    Performs a single generation step on the given population.
    Returns the new population, the best individual of the generation, and its fitness.
    """
    fitnesses = [evaluate_individual(ind, opponents, rounds) for ind in population]
    best_fitness = max(fitnesses)
    best_individual = population[fitnesses.index(best_fitness)]
    survivor_count = int(len(population) * survivor_fraction)
    survivors = select_survivors(population, fitnesses, survivor_count)
    new_population = survivors[:elite_count]
    while len(new_population) < len(population):
        parent1 = random.choice(survivors)
        parent2 = random.choice(survivors)
        child = crossover(parent1, parent2)
        child = mutate(child, mutation_rate)
        new_population.append(child)
    return new_population, best_individual, best_fitness

def genetic_algorithm(opponents, population_size, num_generations, rounds, mutation_rate, survivor_fraction, elite_count):
    """
    Runs the full genetic algorithm for num_generations.
    """
    population = [random_individual() for _ in range(population_size)]
    best_individual = None
    best_fitness = float('-inf')
    for generation in range(num_generations):
        population, gen_best_individual, gen_best_fitness = genetic_algorithm_step(
            population, opponents, rounds, mutation_rate, survivor_fraction, elite_count)
        if gen_best_fitness > best_fitness:
            best_fitness = gen_best_fitness
            best_individual = gen_best_individual
        print(f"Generation {generation}: Best Fitness = {gen_best_fitness}")
    return best_individual, best_fitness
