from simulation.environment import Environment
import time
import json

if __name__ == '__main__':
    s = time.time()
    e = Environment(map_path='./map.csv', save=True, task_number=20)

    end = time.time() - s
    print("done in {} seconds".format(end))
    exit(0)

