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
    """Always cooperates."""
    return COOPERATE

def always_defect(my_history, opponent_history):
    """Always defects."""
    return DEFECT

def tit_for_tat(my_history, opponent_history):
    """
    Cooperates on the first move, then mirrors the opponentss last move.
    """
    if not opponent_history:
        return COOPERATE
    return opponent_history[-1]

def grim_trigger(my_history, opponent_history):
    """
    Cooperates until the opponent defects once, then defects for all following rounds.
    """
    if DEFECT in opponent_history:
        return DEFECT
    return COOPERATE

def win_stay_lose_shift(my_history, opponent_history):
    """
    Starts with cooperation. If the previous move resulted in a payoff of at least 3 (a win),
    it repeats the previous move, else, it switches.
    """
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
    """
    Chooses randomly between cooperation and defection.
    """
    return random.choice([COOPERATE, DEFECT])

def generous_tit_for_tat(my_history, opponent_history):
    """
    Similar to Tit for Tat but more forgiving.
    If the opponent defected in the previous round, cooperates with 70% probability.
    """
    if not opponent_history:
        return COOPERATE
    if opponent_history[-1] == DEFECT:
        return COOPERATE if random.random() < 0.7 else DEFECT
    return COOPERATE

def double_alternator(my_history, opponent_history):
    """
    Follows a fixed cycle of moves: two cooperations and then two defections,
    repeating no matter the opponents moves.
    """
    round_number = len(my_history)
    if round_number % 4 in (0, 1):
        return COOPERATE
    else:
        return DEFECT

def prober(my_history, opponent_history):
    """
    Cooperates for the first 4 rounds.
    On the 5th round, defects to test the opponent.
    After the "probe", if the opponent punished the defection (so defected in round 5),
    the prober defects until the end, else, it reverts to Tit for Tat.
    """
    if len(my_history) < 4:
        return COOPERATE
    elif len(my_history) == 4:
        return DEFECT
    else:
        if len(opponent_history) >= 5 and opponent_history[4] == DEFECT:
            return DEFECT
        return opponent_history[-1] if opponent_history else COOPERATE

def adaptive_ratio(my_history, opponent_history):
    """
    Looks at the opponents cooperation ratio over the last 5 moves (or fewer if not available).
    If the ratio is at least 60%, cooperates, else, defects.
    """
    window = 5
    recent = opponent_history[-window:] if len(opponent_history) >= window else opponent_history
    if not recent:
        return COOPERATE
    cooperation_ratio = recent.count(COOPERATE) / len(recent)
    return COOPERATE if cooperation_ratio >= 0.6 else DEFECT


def run_match(strategy_A, strategy_B, rounds, payoff_matrix=payoff_matrix):
    """
    Runs a match between two strategies for a given number of rounds.
    Each strategy is a function that takes (my_history, opponent_history) as input.
    Returns the move histories and total scores for both players.
    """
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
    """
    Runs a round robin tournament among the provided strategies.
    Each strategy plays against every other (no self play).
    Returns a dictionary mapping strategy names to their total acc score.
    """
    results = {}
    for name in strategies:
        results[name] = 0

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

def rule_table_to_strategy(rule_table):
    def strategy(my_history, opponent_history):
        if not my_history:
            return rule_table[0]
        last_self = my_history[-1]
        last_opp = opponent_history[-1]
        if last_self == COOPERATE and last_opp == COOPERATE:
            index = 1
        elif last_self == DEFECT and last_opp == DEFECT:
            index = 2
        elif last_self == COOPERATE and last_opp == DEFECT:
            index = 3
        elif last_self == DEFECT and last_opp == COOPERATE:
            index = 4
        else:
            index = 1
        return rule_table[index]
    return strategy

def random_rule_table():
    return [random.choice([COOPERATE, DEFECT]) for _ in range(5)]

def crossover(parent1, parent2):
    # 3. Crossover:
    # Combine the genes of two parent chromosomes at a random crossover point.
    point = random.randint(1, len(parent1)-1)
    child = parent1[:point] + parent2[point:]
    return child

def mutate(rule_table, mutation_rate):
    # 4. Mutation:
    # For each gene in the chromosome, flip its value with probability equal to mutation_rate.
    new_rule_table = []
    for gene in rule_table:
        if random.random() < mutation_rate:
            new_gene = COOPERATE if gene == DEFECT else DEFECT
            new_rule_table.append(new_gene)
        else:
            new_rule_table.append(gene)
    return new_rule_table

def genetic_algorithm_evolve(baseline_strategies, population_size=20, generations=50, mutation_rate=0.1, rounds_per_match=100):
    # 1. Initialization:
    # Initialize a population of random chromosomes (rule tables).
    population = [random_rule_table() for _ in range(population_size)]
    
    for gen in range(generations):
        # 2. Selection:
        # Evaluate the fitness of each chromosome by having the corresponding strategy play
        # against each baseline strategy in a tournament. Fitness is the total accumulated score.
        fitnesses = []
        for rule_table in population:
            strategy = rule_table_to_strategy(rule_table)
            total_score = 0
            for name, baseline_strategy in baseline_strategies.items():
                _, _, score, _ = run_match(strategy, baseline_strategy, rounds=rounds_per_match)
                total_score += score
            fitnesses.append(total_score)
        
        # Sort population by fitness in descending order.
        sorted_population = [x for _, x in sorted(zip(fitnesses, population), key=lambda pair: pair[0], reverse=True)]
        population = sorted_population
        
        best_fitness = max(fitnesses)
        print(f"Generation {gen}, best fitness: {best_fitness}")
        
        # 5. Perform Selection and iterate:
        # Create a new population using elitism and genetic operators (crossover and mutation).
        new_population = []
        elite_count = 2  # Retain top individuals (elitism)
        new_population.extend(population[:elite_count])
        while len(new_population) < population_size:
            parent1 = random.choice(population[:population_size//2])
            parent2 = random.choice(population[:population_size//2])
            child = crossover(parent1, parent2)
            child = mutate(child, mutation_rate)
            new_population.append(child)
        population = new_population
    
    # Final evaluation: pick the best chromosome from the final population.
    fitnesses = []
    for rule_table in population:
        strategy = rule_table_to_strategy(rule_table)
        total_score = 0
        for name, baseline_strategy in baseline_strategies.items():
            _, _, score, _ = run_match(strategy, baseline_strategy, rounds=rounds_per_match)
            total_score += score
        fitnesses.append(total_score)
    best_index = fitnesses.index(max(fitnesses))
    best_rule_table = population[best_index]
    return best_rule_table

if __name__ == "__main__":
    # Define the 10 baseline strategies.
    baseline_strategies = {
        "Always Cooperate": always_cooperate,
        "Always Defect": always_defect,
        "Tit for Tat": tit_for_tat,
        "Grim Trigger": grim_trigger,
        "Win-Stay Lose-Shift": win_stay_lose_shift,
        "Random Strategy": random_strategy,
        "Generous Tit-for-Tat": generous_tit_for_tat,
        "Double Alternator": double_alternator,
        "Prober": prober,
        "Adaptive Strategy": adaptive_ratio
    }
    
    rounds_per_match = 100

    # Run a tournament with the baseline strategies.
    tournament_results = run_tournament(baseline_strategies, rounds_per_match)
    print("Baseline Tournament Results (Total Scores):")
    for name, score in tournament_results.items():
        print(f"{name}: {score}")
    
    # Evolve a new strategy using the genetic algorithm.
    print("\nEvolving new strategy using genetic algorithm...")
    best_rule_table = genetic_algorithm_evolve(baseline_strategies, population_size=20, generations=50, mutation_rate=0.1, rounds_per_match=rounds_per_match)
    print("\nBest evolved rule table:", best_rule_table)
    
    # Convert the best rule table to a strategy function.
    evolved_strategy = rule_table_to_strategy(best_rule_table)
    
    # Add the evolved strategy to the baseline and run a new tournament.
    baseline_strategies["Evolved Strategy"] = evolved_strategy
    tournament_results = run_tournament(baseline_strategies, rounds_per_match)
    print("\nTournament Results Including Evolved Strategy (Total Scores):")
    for name, score in tournament_results.items():
        print(f"{name}: {score}")
