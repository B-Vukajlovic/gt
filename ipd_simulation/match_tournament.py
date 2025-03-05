"""
Naam: Simon Plas, Boris Vukaljovic
UvAID: 15249514, 15225054
Description:
Implements match and tournament functions for the Iterated Prisoner's Dilemma,
allowing strategies to compete in regular matches and tournaments.
"""
from ipd_simulation.strategies import payoff_matrix


# Fuction to run a match between two strategies
def run_match(strategy_A, strategy_B, rounds, payoff_matrix=payoff_matrix):
    history_A = []
    history_B = []
    score_A = 0
    score_B = 0

    # Play the match for the given number of rounds
    for _ in range(rounds):
        move_A = strategy_A(history_A, history_B)
        move_B = strategy_B(history_B, history_A)

        payoff_A, payoff_B = payoff_matrix[(move_A, move_B)]
        score_A += payoff_A
        score_B += payoff_B

        history_A.append(move_A)
        history_B.append(move_B)

    return history_A, history_B, score_A, score_B


# Runs the tournament between the given strategies
def run_tournament(strategies, rounds_per_match):
    results = {}

    for name in strategies:
        results[name] = 0

    strategy_names = list(strategies.keys())

    # Iterate through all unique pairs of strategies. Let every strategy
    # play against every other strategy
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
