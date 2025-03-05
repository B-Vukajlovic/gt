# Iterated Prisoner's Dilemma Simulation

## Overview
This project simulates the Iterated Prisoner's Dilemma (IPD) using both
human submitted and genetically evolved strategies. A GUI is also included.

## File Structure

### Simulation
#### ipd_simulation/strategies.py
Defines various non-genetic strategies (e.g., Tit for Tat, Grim Trigger, Random Strategy).

#### ipd_simulation/match_tournament.py
Implements functions for running matches and tournaments.

#### ipd_simulation/genetic_backend.py
Contains the genetic algorithm for evolving strategies.

#### ipd_simulation/simulation_gui.py
Provides the GUI for configuring and running the simulation.

### Execution

#### main.py
The main file for launching the simulation with the GUI.

#### experiment.py
The file that runs experiments on the parameters of a tournament with the
human submitted strategies but also the genetically evolved ones. Further
explanation is in the file itself.

## How to run

### Launching GUI and simulation
To launch the GUI and start the simulation, run:
python3 main.py

### Launching the experiment
To analyze how mutation rates and survivor fractions affect evolution, run:
python3 experiment_mutation_survivor.py

## Contributors
Simon Plas (UvAID: 15249514)
Boris Vukaljovic (UvAID: 15225054)


