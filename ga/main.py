import pandas as pd
import numpy as np
import sys
import random
from ga import GA
import time
from simulation.environment import Environment


def fitness(schedule):
    TT = max([sum(schedule[i]) for i in range(len(schedule))]) + 1
    TTC = min([sum(schedule[i]) for i in range(len(schedule))]) + 1
    BU = sum([sum(schedule[i]) for i in range(len(schedule))]) / 10 + 1
    return TT, TTC, BU


def main2():
    random.seed(666)
    task_number = 50
    e = Environment(map_path='/rendering/map.csv', save=False, run=False, task_number=task_number, scheduling="Greedy0",
                    simulation_name="test")
    t = time.time()
    ga = GA(0, e.ga_entrypoint, popsize=100, maxepoc=100, n=task_number, m=8)
    last_population = ga.run()
    elapsed = time.time() - t
    # print("Initial population|Fx")
    # print(initial)
    print("Last population|Fx")
    print(last_population)
    print("Elapsed " + str(elapsed))
    last_population.to_csv("ga_lastpop_test0.csv", index=False)


if __name__ == "__main__":
    main2()
