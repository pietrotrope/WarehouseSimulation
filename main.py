import gc
from random import seed
from simulation.tools import *
from simulation.environment import Environment
from time import time
from ga import GA
from gc import disable, enable
import json
import csv


def main():
    seed(666)
    task_number = 50

    routes = {}
    with open('astar/astarRoutes.json', 'r') as f:
        routes = json.load(f) 
    raster_map = get_raster_map('rendering/map.csv')
    graph, raster_to_graph, agents_positions, picking_stations = gen_graph(raster_map)
    graph_to_raster = gen_graph_to_raster(graph)
    new_dic = {}
    for key, value in routes.items():
        if isinstance(value, dict):
            new_dic[graph_to_raster[int(key)][0]] = {}
            for key2, value2 in value.items():
                nl = []
                for i in value2:
                    nl.append(graph_to_raster[int(i)][0])
                new_dic[graph_to_raster[int(key)][0]][graph_to_raster[int(key2)][0]] = nl
        else:
            nl = []
            for i in value:
                nl.append(graph_to_raster[int(i)][0])
            new_dic[graph_to_raster[int(key)][0]] = nl
    routes = new_dic
    disable() 

    for task_number in range(50, 450, 50):
        e = Environment(task_number=task_number, scheduling="Greedy0",
                        simulation_name="test", raster_map=raster_map, graph=graph, raster_to_graph=raster_to_graph,
                        agents_positions=agents_positions, graph_to_raster=graph_to_raster, routes=routes, picking_stations = picking_stations)

        e.task_handler.new_task_pool(task_number)
        Fx_col = task_number + 7
        Fx_col_plus_one = Fx_col + 1
        Fx_col_plus_two = Fx_col + 2
        Fx_col_plus_three = Fx_col + 3
        #ga_best_individuals = []
        ga_best = []
        greedy0_best = []
        greedy1_best = []
        random_best = []

        name_ga = "".join(["ga_", str(task_number), ".csv"])
        name_greedy0 = "".join(["greedy0_", str(task_number), ".csv"])
        name_greedy1 = "".join(["greedy1_", str(task_number), ".csv"])
        name_random = "".join(["random_", str(task_number), ".csv"])

        t = time()

        """
        #################################
        # run ga
        for seed_i in range(0, 20):
            ga = GA(seed_i, e.new_simulation, popsize=100, maxepoc=100000, n=task_number, m=8)
            gc.collect()
            best_individual = ga.run()
            # elapsed = time() - t
            #ga_best_individuals.append(best_individual)
            ga_best.append((best_individual[Fx_col_plus_one],
                            best_individual[Fx_col_plus_two],
                            best_individual[Fx_col_plus_three]))
            e.task_handler.restore_task_pool()
        with open(name_ga, 'w') as f:
            write = csv.writer(f)
            write.writerows(ga_best)
        #################################
        """

        # run greedy0
        for seed_i in range(0, 20):
            e.seed = seed_i
            e.task_handler.new_task_pool(task_number)
            TT, TTC, BU = e.new_simulation(task_number=task_number, save=False, scheduling="Greedy0",
                                           simulation_name="Greedy0")
            gc.collect()
            greedy0_best.append((TT, TTC, BU))
        with open(name_greedy0, 'w') as f:
            write = csv.writer(f)
            write.writerows(greedy0_best)
        #################################
        # run greedy1
        for seed_i in range(0, 20):
            e.seed = seed_i
            e.task_handler.new_task_pool(task_number)
            TT, TTC, BU = e.new_simulation(task_number=task_number, save=False, scheduling="Greedy1",
                                           simulation_name="Greedy1")
            gc.collect()
            greedy1_best.append((TT, TTC, BU))
        with open(name_greedy1, 'w') as f:
            write = csv.writer(f)
            write.writerows(greedy1_best)
        #################################

        # run random
        for seed_i in range(0, 20):
            e.seed = seed_i
            e.task_handler.new_task_pool(task_number)
            TT, TTC, BU = e.new_simulation(task_number=task_number, save=False, scheduling="random",
                                           simulation_name="random")
            gc.collect()
            random_best.append((TT, TTC, BU))
        with open(name_random, 'w') as f:
            write = csv.writer(f)
            write.writerows(random_best)
        #################################
        elapsed = time() - t
        print("Elapsed: "+str(elapsed))
        """
        scheduling = best_individual[:Fx_col]
        chromosome = list(map(int, scheduling))
        schedule = ga.chromosome_to_schedule(chromosome=chromosome)
        e.new_simulation(task_number=task_number, save=True, scheduling=schedule, simulation_name="GA")
        e.new_simulation(task_number=task_number, save=True, scheduling="Greedy0", simulation_name="Greedy0")
        e.task_handler.restore_task_pool()
        e.new_simulation(task_number=task_number, save=True, scheduling="Greedy1", simulation_name="Greedy1")
        e.task_handler.restore_task_pool()
        e.new_simulation(task_number=task_number, save=True, scheduling=None, simulation_name="random")
        e.task_handler.restore_task_pool()
        
        # return elapsed
        """


if __name__ == '__main__':
    main()
