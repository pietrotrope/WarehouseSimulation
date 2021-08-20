from os import stat
import random
from numpy.lib.function_base import average
from numpy.lib.npyio import save
from simulation.environment import Environment
import time
import statistics
import json

if __name__ == '__main__':
    random.seed(666)
    s = time.time()
    e = Environment(map_path='./map.csv', save=True, task_number=100)
    end = time.time() - s
    print("done in {} seconds".format(end))
    times = []
    for i in range(2):
        s = time.time()
        print(i)
        e.new_simulation(task_number=100, save=True)
        end = time.time() - s
        times.append(end)
    print(statistics.mean(times))

    exit(0)
