# ipd_simulation/match_tournament.py

from ipd_simulation.strategies import payoff_matrix

def run_match(strategy_A, strategy_B, rounds, payoff_matrix=payoff_matrix):
    history_A = []
    history_B = []
    score_A = 0
    score_B = 0

    for _ in range(rounds):
        move_A = strategy_A(history_A, history_B)
        move_B = strategy_B(history_B, history_A)
        pA, pB = payoff_matrix[(move_A, move_B)]
        score_A += pA
        score_B += pB
        history_A.append(move_A)
        history_B.append(move_B)

    return history_A, history_B, score_A, score_B

def run_tournament(strategies, rounds_per_match):
    results = { name: 0 for name in strategies }
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
