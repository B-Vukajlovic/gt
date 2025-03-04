# ipd_simulation/strategies.py

import random

COOPERATE = 'C'
DEFECT = 'D'

payoff_matrix = {
    (COOPERATE, COOPERATE): (3, 3),
    (COOPERATE, DEFECT):    (0, 5),
    (DEFECT, COOPERATE):    (5, 0),
    (DEFECT, DEFECT):       (1, 1)
}


# Always cooperate
def always_cooperate(my_history, opponent_history):
    return COOPERATE


# Always defect
def always_defect(my_history, opponent_history):
    return DEFECT


# Tit for tat, copy opponents last move
def tit_for_tat(my_history, opponent_history):
    if not opponent_history:
        return COOPERATE
    return opponent_history[-1]


# Cooperate until opponent defects once, and then defect forever
def grim_trigger(my_history, opponent_history):
    if DEFECT in opponent_history:
        return DEFECT
    return COOPERATE


# If the last rounds outcome has a good scare, repeat last move.
# Otherwise switch move
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


# Randomly select between cooperate and defect
def random_strategy(my_history, opponent_history):
    return random.choice([COOPERATE, DEFECT])


# Tit for tat but has a 70% to cooperate if opponents defect, thus is forgiving
def generous_tit_for_tat(my_history, opponent_history):
    if not opponent_history:
        return COOPERATE
    if opponent_history[-1] == DEFECT:
        return COOPERATE if random.random() < 0.7 else DEFECT

    return COOPERATE


# Alternates every two rounds between cooperate and defect
def double_alternator(my_history, opponent_history):
    round_number = len(my_history)

    if round_number % 4 in (0, 1):
        return COOPERATE
    else:
        return DEFECT


# Starts with four rounds of cooperate, then tries to defect. If opponent
# also defects then tit for that.
def prober(my_history, opponent_history):
    if len(my_history) < 4:
        return COOPERATE
    elif len(my_history) == 4:
        return DEFECT
    else:
        if len(opponent_history) >= 5 and opponent_history[4] == DEFECT:
            return DEFECT
        return opponent_history[-1] if opponent_history else COOPERATE


# Look at last 5 moves of opponent and check how much they cooperate. If they
# cooperate more than 60% of the time, also cooperate, else defect.
def adaptive_ratio(my_history, opponent_history):
    recent = opponent_history[-5:] if len(opponent_history) >= 5 else opponent_history
    if not recent:
        return COOPERATE
    cooperation_ratio = recent.count(COOPERATE) / len(recent)
    return COOPERATE if cooperation_ratio >= 0.6 else DEFECT

non_genetic_strategies = {
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
