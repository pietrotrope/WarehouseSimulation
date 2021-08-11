from simulation.environment import Environment
import time
import json

if __name__ == '__main__':
    s = time.time()
    e = Environment(map_path='./map.csv', save=True, task_number=100)
    end = time.time() - s
    print("done in {} seconds".format(end))
    print()
    print("starting new simulation in same environment")
    s = time.time()
    e.new_simulation()
    end = time.time() - s
    print("done in {} seconds".format(end))

    exit(0)

