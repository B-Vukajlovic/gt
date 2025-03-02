# ipd_simulation/simulation_gui.py

from tkinter import *
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

from pyics import Model, GUI

from ipd_simulation.strategies import non_genetic_strategies
from ipd_simulation.match_tournament import run_match, run_tournament
from ipd_simulation.genetic_backend import *

class IPDSimulation(Model):
    def __init__(self):
        Model.__init__(self)
        self.make_param('mode', 'Tournament', str)
        self.make_param('rounds_per_match', 50, int)
        self.make_param('population_size', 100, int)
        self.make_param('num_generations', 50, int)
        self.make_param('rounds', 200, int)
        self.make_param('mutation_rate', 0.1, float)
        self.make_param('survivor_fraction', 0.7, float)
        self.make_param('elite_count', 10, int)

        self.make_param('strategy_A', 'Tit for Tat', str)
        self.make_param('strategy_B', 'Always Defect', str)

        self.phase = None
        self.current_generation = 0
        self.population = None
        self.best_individual = None
        self.best_fitness = None
        self.gens = []
        self.max_fitnesses = []
        self.log = ""
        self.finished = False
        self.match_result = None

        self.non_genetic_strategies = non_genetic_strategies

    def reset(self):
        self.current_generation = 0
        self.gens = []
        self.max_fitnesses = []
        self.log = ""
        self.finished = False

        if self.mode not in ("Tournament", "Match"):
            self.phase = "error"
            self.append_log("ERROR: Invalid mode value '" + str(self.mode) + "'. Use 'Tournament' or 'Match'.")
            return

        if self.mode == "Tournament":
            self.phase = "initial_tournament"
        elif self.mode == "Match":
            self.phase = "match"

        self.population = None
        self.best_individual = None
        self.best_fitness = None
        if hasattr(self, 'gui') and self.gui is not None:
            self.gui.clear_terminal()
        self.append_log("Simulation reset. Mode: " + self.mode)

    def step(self):
        if self.phase == "error":
            return True

        if self.mode == "Tournament":
            if self.phase == "initial_tournament":
                self.append_log("Running initial tournament among non-genetic strategies...")
                results = run_tournament(self.non_genetic_strategies, self.rounds_per_match)
                for name, score in results.items():
                    self.append_log(f"{name}: {score}")
                self.population = [random_individual() for _ in range(self.population_size)]
                self.current_generation = 0
                self.phase = "genetic_phase"
                return False
            elif self.phase == "genetic_phase":
                from ipd_simulation.genetic_backend import genetic_algorithm_step
                population, gen_best_individual, gen_best_fitness = genetic_algorithm_step(
                    self.population,
                    self.non_genetic_strategies,
                    self.rounds,
                    self.mutation_rate,
                    self.survivor_fraction,
                    self.elite_count
                )
                self.population = population
                self.append_log(f"Generation {self.current_generation}: Best Fitness = {gen_best_fitness}")
                self.gens.append(self.current_generation)
                self.max_fitnesses.append(gen_best_fitness)
                if self.current_generation >= self.num_generations - 1:
                    self.best_individual = gen_best_individual
                    self.best_fitness = gen_best_fitness
                    self.phase = "final_tournament"
                    return False
                self.current_generation += 1
                return False
            elif self.phase == "final_tournament":
                genetic_strategy = make_genetic_strategy(self.best_individual)
                strategies = self.non_genetic_strategies.copy()
                strategies["Genetic Strategy"] = genetic_strategy
                self.append_log("Running final tournament including Genetic Strategy...")
                results = run_tournament(strategies, self.rounds_per_match)
                for name, score in results.items():
                    self.append_log(f"{name}: {score}")
                self.phase = "finished"
                self.finished = True
                return True

        elif self.mode == "Match":
            if self.phase == "match":
                valid_strategies = list(self.non_genetic_strategies.keys()) + ["Genetic Strategy"]
                strat_A_name = self.strategy_A
                strat_B_name = self.strategy_B
                if strat_A_name not in valid_strategies:
                    self.append_log(f"ERROR: Strategy A '{strat_A_name}' is invalid. Valid options: {valid_strategies}")
                    self.phase = "error"
                    return True
                if strat_B_name not in valid_strategies:
                    self.append_log(f"ERROR: Strategy B '{strat_B_name}' is invalid. Valid options: {valid_strategies}")
                    self.phase = "error"
                    return True
                if strat_A_name == "Genetic Strategy" and strat_B_name == "Genetic Strategy":
                    self.append_log("ERROR: Both strategies cannot be 'Genetic Strategy'.")
                    self.phase = "error"
                    return True

                strategies_for_match = self.non_genetic_strategies.copy()
                if strat_A_name == "Genetic Strategy":
                    self.append_log("Evolving Genetic Strategy for match against " + strat_B_name + "...")
                    opponents = { strat_B_name: strategies_for_match[strat_B_name] }
                    best_ind, best_fit = genetic_algorithm(
                        opponents,
                        self.population_size,
                        self.num_generations,
                        self.rounds,
                        self.mutation_rate,
                        self.survivor_fraction,
                        self.elite_count)
                    genetic_strategy = make_genetic_strategy(best_ind)
                    strategies_for_match["Genetic Strategy"] = genetic_strategy
                    self.append_log(f"Evolved Genetic Strategy with fitness {best_fit}")
                elif strat_B_name == "Genetic Strategy":
                    self.append_log("Evolving Genetic Strategy for match against " + strat_A_name + "...")
                    opponents = { strat_A_name: strategies_for_match[strat_A_name] }
                    best_ind, best_fit = genetic_algorithm(
                        opponents,
                        self.population_size,
                        self.num_generations,
                        self.rounds,
                        self.mutation_rate,
                        self.survivor_fraction,
                        self.elite_count)
                    genetic_strategy = make_genetic_strategy(best_ind)
                    strategies_for_match["Genetic Strategy"] = genetic_strategy
                    self.append_log(f"Evolved Genetic Strategy with fitness {best_fit}")

                strat_A = strategies_for_match.get(strat_A_name)
                strat_B = strategies_for_match.get(strat_B_name)
                self.append_log(f"Running match: {strat_A_name} vs {strat_B_name}")
                history_A, history_B, score_A, score_B = run_match(strat_A, strat_B, self.rounds_per_match)
                self.append_log("Match Results:")
                self.append_log(f"{strat_A_name}: {score_A}")
                self.append_log(f"{strat_B_name}: {score_B}")
                self.phase = "finished"
                self.finished = True
                return True
        return True

    def draw(self):
        if self.mode == "Tournament" and self.phase in ["genetic_phase", "final_tournament", "finished"]:
            plt.clf()
            plt.plot(self.gens, self.max_fitnesses)
            plt.xlabel("Generation")
            plt.ylabel("Max Fitness")
            plt.title("Genetic Algorithm Evolution")
            plt.draw()
        if hasattr(self, 'gui') and self.gui is not None:
            self.gui.update_terminal(self.log)

    def append_log(self, message):
        self.log += message + "\n"
        if hasattr(self, 'gui') and self.gui is not None:
            self.gui.append_terminal(message)

class IPDGUI(GUI):
    def initGUI(self):
        super().initGUI()
        self.rootWindow.geometry("800x900")
        self.terminal_frame = Frame(self.rootWindow, height=300, bd=2, relief="sunken")
        self.terminal_frame.pack(side=BOTTOM, fill="x")
        self.terminal_text = Text(self.terminal_frame, height=15, wrap=WORD)
        self.terminal_text.pack(side=LEFT, fill="both", expand=True)
        self.terminal_scroll = Scrollbar(self.terminal_frame, command=self.terminal_text.yview)
        self.terminal_scroll.pack(side=RIGHT, fill=Y)
        self.terminal_text.config(yscrollcommand=self.terminal_scroll.set)
        self.terminal_text.insert(END, "Terminal Output:\n")

    def append_terminal(self, message):
        self.terminal_text.insert(END, message + "\n")
        self.terminal_text.see(END)

    def clear_terminal(self):
        self.terminal_text.delete(1.0, END)

    def update_terminal(self, log_text):
        pass
