from multiprocessing import freeze_support
from random import seed

import numpy as np
from tqdm import tqdm, trange

from simulation.tools import *
from simulation.environment import Environment
from time import time
from ga import GA
from gc import disable, enable
import json


def main():
    disable()    
    seed(666)
    task_number = 50

    routes = {}
    with open('astar/astarRoutes.json', 'r') as f:
        routes = json.load(f)

    raster_map = get_raster_map('rendering/map.csv')
    graph, raster_to_graph, agents_positions = gen_graph(raster_map)
    graph_to_raster = gen_graph_to_raster(graph)

    e = Environment(task_number=task_number, scheduling="Greedy0",
                    simulation_name="test", raster_map = raster_map, graph=graph, raster_to_graph=raster_to_graph,
                    agents_positions=agents_positions, graph_to_raster=graph_to_raster, routes=routes)
    
                    
    e.task_handler.new_task_pool(task_number)
    t = time()
    ga = GA(0, e.new_simulation, popsize=100, maxepoc=10, n=task_number, m=8)
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