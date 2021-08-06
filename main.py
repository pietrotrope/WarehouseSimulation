from simulation.environment import Environment

if __name__ == '__main__':

    try:
        e = Environment(map_path='./map.csv', save=True)
    except KeyError:
        exit(0)
