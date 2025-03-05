"""
Naam: Simon Plas, Boris Vukaljovic
UvAID: 15249514, 15225054
Description:
This file runs experiments on the genetic algorithm by varying:
 - Mutation rates: [0.01, 0.025, 0.05, 0.075, 0.1]
 - Survivor fractions: [0.01, 0.05, 0.1, 0.15, 0.2, 0.25]

For each run, the metric is computed as the average over generations
of the maximum normalized fitness (as recorded in sim.max_fitnesses).

Three graphs are generated:
1. X-axis: mutation rates, Y-axis: metric.
2. X-axis: survivor fractions, Y-axis: metric.
3. X-axis: tuples (mutation rate, survivor fraction), Y-axis: metric.
   In graph 3, bars are colored based on the mutation rate.
"""
import matplotlib.pyplot as plt
from ipd_simulation.simulation_gui import IPDSimulation

# Initial configuration for the genetic algorithm
init_params = {
    "mode": "Tournament",
    "rounds_per_match": 200,
    "population_size": 100,
    "num_generations": 50,
    "mutation_rate": 0.05,
    "survivor_fraction": 0.15,
    "strategy_A": "Tit for Tat",
    "strategy_B": "Always Defect",
}


# Set y-axis limits to improve visualization.
def set_y_limits(data):
    y_min = min(data)
    y_max = max(data)

    margin = (y_max - y_min) * 0.1 if y_max != y_min else 0.05
    plt.ylim(y_min - margin, y_max + margin)


# Run a single simulation of IPDSimulation
def run_simulation():
    sim = IPDSimulation()

    for key, value in init_params.items():
        setattr(sim, key, value)
    sim.reset()
    while not sim.finished:
        sim.step()

    if sim.max_fitnesses:
        return sum(sim.max_fitnesses) / len(sim.max_fitnesses)
    else:
        return 0

# Function that actually runs the experiment
def main():
    # Define mutation rates and survivor fractions for experiments
    mutation_rates = [0.01, 0.025, 0.05, 0.075, 0.1]
    survivor_fractions = [0.01, 0.05, 0.1, 0.15, 0.2, 0.25]

    # Generate a colormap for visualization
    cmap = plt.get_cmap("viridis", len(mutation_rates))
    color_map = {m: cmap(i) for i, m in enumerate(mutation_rates)}

    # Experiment with different mutation rates
    results_mutation = {}
    for mut in mutation_rates:
        init_params["mutation_rate"] = mut

        metric = run_simulation()
        results_mutation[mut] = metric
        print(f"Mutation Rate {mut}: Metric = {metric}")

    # Plot results for mutation rates
    plt.figure(figsize=(8, 5))
    x_labels = [str(m) for m in results_mutation.keys()]
    y_values = list(results_mutation.values())
    plt.bar(x_labels, y_values)
    plt.xlabel("Mutation Rate")
    plt.ylabel("Avg. Max Normalized Fitness")
    plt.title("Effect of Mutation Rate on GA Performance")
    set_y_limits(y_values)

    # Reset mutation rate and experiment with different survivor fractions
    init_params["mutation_rate"] = 0.05

    results_survivor = {}
    for surv in survivor_fractions:
        init_params["survivor_fraction"] = surv

        metric = run_simulation()
        results_survivor[surv] = metric
        print(f"Survivor Fraction {surv}: Metric = {metric}")

    # Plot results for survivor fractions
    plt.figure(figsize=(8, 5))
    x_labels = [str(s) for s in results_survivor.keys()]
    y_values = list(results_survivor.values())
    plt.bar(x_labels, y_values)
    plt.xlabel("Survivor Fraction")
    plt.ylabel("Avg. Max Normalized Fitness")
    plt.title("Effect of Survivor Fraction on GA Performance")
    set_y_limits(y_values)

    # Reset survivor fraction and experiment with combinations of mutation rates and survivor fractions
    init_params["survivor_fraction"] = 0.15

    results_tuple = {}
    tuple_colors = []
    for mut in mutation_rates:
        for surv in survivor_fractions:
            init_params["mutation_rate"] = mut
            init_params["survivor_fraction"] = surv
            metric = run_simulation()
            results_tuple[(mut, surv)] = metric
            tuple_colors.append(color_map[mut])
            print(f"Mutation {mut}, Survivor {surv}: Metric = {metric}")

    # Plot results for mutation-survivor combinations
    labels = [f"m:{m}, s:{s}" for m, s in results_tuple.keys()]
    values = list(results_tuple.values())

    plt.figure(figsize=(12, 6))
    plt.bar(labels, values, color=tuple_colors)
    plt.xlabel("Mutation Rate and Survivor Fraction (m, s)")
    plt.ylabel("Avg. Max Normalized Fitness")
    plt.title("GA Performance for (Mutation Rate, Survivor Fraction) Combinations")
    plt.xticks(rotation=45, ha="right")
    set_y_limits(values)

    plt.show()


if __name__ == "__main__":
    main()
