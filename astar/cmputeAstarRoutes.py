from simulation.environment import Environment
from astar.astar import computeAstarRoutes
import time
import json


def AstarRoutesToFile():
    env = Environment()
    start = time.time()
    dic = computeAstarRoutes(env)
    with open("astarRoutes.json", "w") as fp:
        json.dump(dic, fp)
    print(time.time() - start)
    print("seconds to compute all the routes")
