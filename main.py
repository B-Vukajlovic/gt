# main.py

init_params = {
    "mode": "Tournament",
    "rounds_per_match": 300,
    "population_size": 100,
    "num_generations": 50,
    "rounds": 200,
    "mutation_rate": 0.1,
    "survivor_fraction": 0.3,
    "elite_count": 5,
    "strategy_A": "Tit for Tat",
    "strategy_B": "Always Defect"
}

from ipd_simulation.simulation_gui import IPDSimulation, IPDGUI

if __name__ == "__main__":
    sim = IPDSimulation()

    for key, value in init_params.items():
        setattr(sim, key, value)

    gui = IPDGUI(sim, title="IPD Simulation")
    sim.gui = gui
    gui.start()
