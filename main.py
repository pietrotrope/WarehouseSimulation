from os import stat
import random
from numpy.lib.function_base import average
from numpy.lib.npyio import save
from simulation.environment import Environment
import time
import statistics
import json
from ga import GA


def main2():
    random.seed(666)
    task_number = 50
    e = Environment(map_path='rendering/map.csv', save=False, run=False, task_number=task_number, scheduling="Greedy0",
                    simulation_name="test")
    e.task_handler.new_task_pool(task_number)
    t = time.time()
    ga = GA(0, e.ga_entrypoint, popsize=10, maxepoc=10, n=task_number, m=8)
    last_population = ga.run()
    elapsed = time.time() - t
    # print("Initial population|Fx")
    # print(initial)
    # print("Last population|Fx")
    print(last_population)
    print("Elapsed " + str(elapsed))
    #last_population.to_csv("ga_lastpop_test0.csv", index=False)

    Fx_col = len(last_population.columns) - 4
    Fx = last_population.loc[:, Fx_col]
    res = last_population.loc[last_population[Fx_col] == max(Fx)].iloc[0]
    tt = res[Fx_col + 1]
    ttc = res[Fx_col + 2]
    bu = res[Fx_col + 3]
    scheduling = res[:Fx_col]
    chromosome = list(map(int, scheduling))
    schedule = ga.chromosome_to_schedule(chromosome=chromosome)
    print(schedule)
    print(e.task_handler.initial_task_pool)
    e.new_simulation(task_number=task_number, save=True, scheduling=schedule)


def main1():
    random.seed(666)
    task_number = 100
    s = time.time()
    e = Environment(map_path='rendering/map.csv', save=True, task_number=task_number, scheduling="Greedy0",
                    simulation_name="test")
    end = time.time() - s
    print("done in {} seconds".format(end))
    times = []
    e.task_handler.new_task_pool(task_number)
    for i in range(2):
        s = time.time()
        print("run {}".format(i))
        e.new_simulation(task_number=task_number, save=True, scheduling=None, new_task_pool=False)
        end = time.time() - s
        times.append(end)
    print(statistics.mean(times))

    exit(0)


if __name__ == '__main__':
    # main1()
    main2()
