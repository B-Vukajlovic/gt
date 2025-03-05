"""
Naam: Simon Plas, Boris Vukaljovic
UvAID: 15249514, 15225054
Description:
This script runs an Iterated Prisoner's Dilemma simulation with a GUI,
allowing users to use different strategies in a tournament.
"""
from ipd_simulation.simulation_gui import IPDSimulation, IPDGUI


init_params = {
    "mode": "Tournament",
    "rounds_per_match": 200,
    "population_size": 100,
    "num_generations": 50,
    "rounds": 200,
    "mutation_rate": 0.05,
    "survivor_fraction": 0.15,
    "strategy_A": "Tit for Tat",
    "strategy_B": "Always Defect"
}

if __name__ == "__main__":
    sim = IPDSimulation()

    for key, value in init_params.items():
        setattr(sim, key, value)

    gui = IPDGUI(sim, title="IPD Simulation")
    sim.gui = gui
    gui.start()
