import random

COOPERATE = 'C'
DEFECT = 'D'

payoff_matrix = {
    (COOPERATE, COOPERATE): (3, 3),
    (COOPERATE, DEFECT):    (0, 5),
    (DEFECT, COOPERATE):    (5, 0),
    (DEFECT, DEFECT):       (1, 1)
}

def always_cooperate(my_history, opponent_history):
    return COOPERATE

def always_defect(my_history, opponent_history):
    return DEFECT

def tit_for_tat(my_history, opponent_history):
    if not opponent_history:
        return COOPERATE
    return opponent_history[-1]

def grim_trigger(my_history, opponent_history):
    if DEFECT in opponent_history:
        return DEFECT
    return COOPERATE

def win_stay_lose_shift(my_history, opponent_history):
    if not my_history:
        return COOPERATE
    last_move = my_history[-1]
    last_opponent = opponent_history[-1]
    last_payoff, _ = payoff_matrix[(last_move, last_opponent)]
    if last_payoff >= 3:
        return last_move
    else:
        return DEFECT if last_move == COOPERATE else COOPERATE

def random_strategy(my_history, opponent_history):
    return random.choice([COOPERATE, DEFECT])

def generous_tit_for_tat(my_history, opponent_history):
    if not opponent_history:
        return COOPERATE
    if opponent_history[-1] == DEFECT:
        return COOPERATE if random.random() < 0.7 else DEFECT
    return COOPERATE

def double_alternator(my_history, opponent_history):
    round_number = len(my_history)
    if round_number % 4 in (0, 1):
        return COOPERATE
    else:
        return DEFECT

def prober(my_history, opponent_history):
    if len(my_history) < 4:
        return COOPERATE
    elif len(my_history) == 4:
        return DEFECT
    else:
        if len(opponent_history) >= 5 and opponent_history[4] == DEFECT:
            return DEFECT
        return opponent_history[-1] if opponent_history else COOPERATE

def adaptive_ratio(my_history, opponent_history):
    window = 5
    recent = opponent_history[-window:] if len(opponent_history) >= window else opponent_history
    if not recent:
        return COOPERATE
    cooperation_ratio = recent.count(COOPERATE) / len(recent)
    return COOPERATE if cooperation_ratio >= 0.6 else DEFECT

def run_match(strategy_A, strategy_B, rounds, payoff_matrix=payoff_matrix):
    history_A = []
    history_B = []
    score_A = 0
    score_B = 0

    for _ in range(rounds):
        move_A = strategy_A(history_A, history_B)
        move_B = strategy_B(history_B, history_A)
        payoff_A, payoff_B = payoff_matrix[(move_A, move_B)]
        score_A += payoff_A
        score_B += payoff_B
        history_A.append(move_A)
        history_B.append(move_B)

    return history_A, history_B, score_A, score_B

def run_tournament(strategies, rounds_per_match):
    results = {name: 0 for name in strategies}
    strategy_names = list(strategies.keys())

    for i in range(len(strategy_names)):
        for j in range(i + 1, len(strategy_names)):
            name_A = strategy_names[i]
            name_B = strategy_names[j]
            strat_A = strategies[name_A]
            strat_B = strategies[name_B]
            _, _, score_A, score_B = run_match(strat_A, strat_B, rounds_per_match)
            results[name_A] += score_A
            results[name_B] += score_B
    return results

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
        key = (tuple(my_history[-3:]), tuple(opponent_history[-3:]))
        return individual['rule_table'].get(key, COOPERATE)
    return strategy

def evaluate_individual(individual, opponents, rounds):
    candidate = make_genetic_strategy(individual)
    total = 0
    for opp in opponents.values():
        _, _, score, _ = run_match(candidate, opp, rounds)
        total += score
    return total

def select_survivors(population, fitnesses, survivor_count):
    sorted_pop = [ind for _, ind in sorted(zip(fitnesses, population), key=lambda x: x[0], reverse=True)]
    return sorted_pop[:survivor_count]

def crossover(parent1, parent2):
    child_opening = [parent1['opening'][i] if random.random() < 0.5 else parent2['opening'][i] for i in range(3)]
    child_rule_table = {}
    for key in parent1['rule_table']:
        child_rule_table[key] = parent1['rule_table'][key] if random.random() < 0.5 else parent2['rule_table'][key]
    return {"opening": child_opening, "rule_table": child_rule_table}

def mutate(individual, mutation_rate=0.05):
    individual['opening'] = [DEFECT if (move == COOPERATE and random.random() < mutation_rate)
                               else COOPERATE if (move == DEFECT and random.random() < mutation_rate)
                               else move for move in individual['opening']]
    for key in individual['rule_table']:
        if random.random() < mutation_rate:
            current = individual['rule_table'][key]
            individual['rule_table'][key] = DEFECT if current == COOPERATE else COOPERATE
    return individual

def genetic_algorithm(opponents, population_size, num_generations, rounds, mutation_rate, survivor_fraction, elite_count):
    population = [random_individual() for _ in range(population_size)]
    best_individual = None
    best_fitness = float('-inf')

    for generation in range(num_generations):
        fitnesses = [evaluate_individual(ind, opponents, rounds) for ind in population]
        gen_best = max(fitnesses)

        if gen_best > best_fitness:
            best_fitness = gen_best
            best_individual = population[fitnesses.index(gen_best)]
        print(f"Generation {generation}: Best Fitness = {gen_best}")

        survivor_count = int(population_size * survivor_fraction)
        survivors = select_survivors(population, fitnesses, survivor_count)
        new_population = survivors[:elite_count]

        while len(new_population) < population_size:
            parent1 = random.choice(survivors)
            parent2 = random.choice(survivors)
            child = crossover(parent1, parent2)
            child = mutate(child, mutation_rate)
            new_population.append(child)
        population = new_population

    return best_individual, best_fitness

if __name__ == "__main__":
    strategies = {
        "Always Cooperate": always_cooperate,
        "Always Defect": always_defect,
        "Tit for Tat": tit_for_tat,
        "Grim Trigger": grim_trigger,
        "Win-Stay Lose-Shift": win_stay_lose_shift,
        "Random Strategy": random_strategy,
        "Generous Tit-for-Tat": generous_tit_for_tat,
        "Double Alternator": double_alternator,
        "Prober": prober,
        "Adaptive Ratio": adaptive_ratio
    }

    rounds_per_match = 50
    population_size=100
    num_generations=50
    rounds=200
    mutation_rate=0.1
    survivor_fraction=0.25
    elite_count=2

    tournament_results = run_tournament(strategies, rounds_per_match)
    print("Tournament Results (Original Strategies):")
    for name, score in tournament_results.items():
        print(f"{name}: {score}")

    print("\nStarting Genetic Algorithm evolution...")
    best_individual, best_fitness = genetic_algorithm(strategies,
                                                      population_size,
                                                      num_generations,
                                                      rounds,
                                                      mutation_rate,
                                                      survivor_fraction,
                                                      elite_count)

    print("\nBest evolved individual (Fitness: {}):".format(best_fitness))
    print("Opening sequence:", best_individual['opening'])
    print("Sample rule table entries:")
    count = 0
    for key, move in best_individual['rule_table'].items():
        if count >= 5:
            break
        print(f"Self last 3: {key[0]}, Opponent last 3: {key[1]} -> Next move: {move}")
        count += 1

    genetic_strategy = make_genetic_strategy(best_individual)
    strategies["Genetic Strategy"] = genetic_strategy
    tournament_results = run_tournament(strategies, rounds_per_match)
    print("\nTournament Results (Including Genetic Strategy):")
    for name, score in tournament_results.items():
        print(f"{name}: {score}")
