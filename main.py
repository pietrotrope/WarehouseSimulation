from multiprocessing import freeze_support
from random import seed

import numpy as np
from tqdm import tqdm, trange

from simulation.environment import Environment
from time import time
from ga import GA
from gc import disable, enable


def main():
    disable()    
    seed(666)
    task_number = 50
    e = Environment(map_path='rendering/map.csv', save=False, run=False, task_number=task_number, scheduling="Greedy0",
                    simulation_name="test")
    e.task_handler.new_task_pool(task_number)
    t = time()
    ga = GA(0, e.ga_entrypoint, popsize=100, maxepoc=200, n=task_number, m=8, n_core=1)
    last_population = ga.run()
    elapsed = time() - t
    enable()
    #print(last_population)
    print("Elapsed " + str(elapsed))

    Fx_col = len(last_population.columns) - 4
    Fx = last_population.loc[:, Fx_col]
    res = last_population.loc[last_population[Fx_col] == max(Fx)].iloc[0]

    scheduling = res[:Fx_col]
    chromosome = list(map(int, scheduling))
    schedule = ga.chromosome_to_schedule(chromosome=chromosome)
    e.new_simulation(task_number=task_number, save=True, scheduling=schedule, simulation_name="GA")
    e.new_simulation(task_number=task_number, save=True, scheduling="Greedy0", simulation_name="Greedy0")
    e.task_handler.restore_task_pool()
    e.new_simulation(task_number=task_number, save=True, scheduling="Greedy1", simulation_name="Greedy1")
    e.task_handler.restore_task_pool()
    e.new_simulation(task_number=task_number, save=True, scheduling=None, simulation_name="random")
    e.task_handler.restore_task_pool()

    return elapsed


if __name__ == '__main__':
    main()