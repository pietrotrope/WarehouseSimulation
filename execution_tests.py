from simulation.tools import *
from simulation.environment import Environment
from time import time
from ga import GA
from gc import disable, enable
import json


def main():   
    task_number = 50

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
    
                    
    e.task_handler.new_task_pool(task_number)
    t = time()
    ga = GA(5, e.new_simulation, popsize=100, maxepoc=100000, n=task_number, m=8)
    ga.run()
    elapsed = time() - t
    enable()
    #print(last_population)
    print("Elapsed " + str(elapsed))


    e.new_simulation(task_number=task_number, save=True, scheduling="Greedy0", simulation_name="Greedy0")
    e.task_handler.restore_task_pool()
    e.new_simulation(task_number=task_number, save=True, scheduling="Greedy1", simulation_name="Greedy1")
    e.task_handler.restore_task_pool()
    e.new_simulation(task_number=task_number, save=True, scheduling="Random", simulation_name="random")
    e.task_handler.restore_task_pool()

    return elapsed


if __name__ == '__main__':
    main()