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

    rounds_per_match = 100
    tournament_results = run_tournament(strategies, rounds_per_match)

    print("Tournament Results (Total Scores):")
    for name, score in tournament_results.items():
        print(f"{name}: {score}")
