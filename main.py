from simulation.environment import Environment
import time

if __name__ == '__main__':
    s = time.time()
    e = Environment(map_path='./map.csv', save=True, task_number=100)
    end = time.time() - s
    print("done in {} seconds".format(end))
    exit(0)
