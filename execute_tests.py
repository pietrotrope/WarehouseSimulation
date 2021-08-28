import gc
from random import seed
from simulation.tools import *
from simulation.environment import Environment
from time import time
from ga import GA
from gc import disable, enable
import json
import csv
import sys
from pathlib import Path


def main(task_number):
    routes = {}
    with open('astar/astarRoutes.json', 'r') as f:
        routes = json.load(f) 
    raster_map = get_raster_map('rendering/map.csv')
    graph, raster_to_graph, agents_positions = gen_graph(raster_map)
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

    e = Environment(task_number=task_number, scheduling="Greedy0",
                    simulation_name="test", raster_map=raster_map, graph=graph, raster_to_graph=raster_to_graph,
                    agents_positions=agents_positions, graph_to_raster=graph_to_raster, routes=routes)

    name_ga = "".join(["ga_", str(task_number), ".csv"])
    t = time()

    start = 0
    my_file = Path(name_ga)
    if my_file.is_file():
        file = open(name_ga, "r")
        line_count = 0
        for line in file:
            if line != "\n":
                line_count += 1
        file.close()
        start = line_count

    # file exists
    # run GA
    with open(name_ga, 'a') as f:
        write = csv.writer(f)
        for seed_i in range(start, 20):
            e.seed = seed_i
            e.task_handler.new_task_pool(task_number)
            print("Ga run number "+str(seed_i+1))
            ga = GA(0, e.new_simulation, popsize=100, maxepoc=100000, n=task_number, m=8)
            res = ga.run()
            gc.collect()
            write.writerow(res)
    #################################
    elapsed = time() - t
    print("Elapsed: "+str(elapsed))


if __name__ == '__main__':
    print(sys.argv[1]+" tasks")
    main(int(sys.argv[1]))
