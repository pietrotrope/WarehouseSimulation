import multiprocessing
from simulation.tile import Tile
from .direction import Direction
import random

movement = {
    Direction.UP: (0, 1),
    Direction.DOWN: (0, -1),
    Direction.LEFT: (-1, 0),
    Direction.RIGHT: (1, 0)
}


class Agent:

    def __init__(self, agent_id, position, route, env, direction=Direction.DOWN, task_handler=None):
        self.id = agent_id
        self.position = position
        self.direction = direction
        self.route = route
        self.env = env
        self.task_handler = task_handler
        self.task = None
        self.log = []
        self.time = 0

    def get_task(self):
        task = self.task_handler.get_task(self.id)
        if task is None:
            return True
        else:
            self.task = task
            return False

    def declare_route(self):
        conflict = None
        for i in range(len(self.route)):
            x, y = self.route[i]
            if self.env.raster_map[x][y].timestamp[i + self.env.time]:
                self.env.raster_map[x][y].timestamp[i +
                                                    self.env.time].append(self.id)
            else:
                self.env.raster_map[x][y].timestamp[i +
                                                    self.env.time] = [self.id]

            if len(self.env.raster_map[x][y].timestamp[i + self.env.time]) > 1 and conflict is None:
                conflict = (i + self.env.time, (x, y))

            #TODO Trovato problema (se due che hanno priorità hanno + errori sul cammino)

        return conflict

    def get_priority(self):
        return random.random()

    def shift_route(self, shift, bad_conflict):
        #TODO NUOVO PROBLEMA SUI TIPI DI CONFLITTI, Se non finiscono nella stessa cella ma si sovrappongono i cammini
        if bad_conflict:

            if self.direction.value[0] == 0:  # Going up or down
                tile_left = self.env.tile_map[(self.position - (1, 0))]
                tile_right = self.env.tile_map[(self.position + (1, 0))]

                if tile_left.tile != Tile.WALKABLE and tile_left.tile != Tile.ROBOT:
                    self.invalidate_and_declare_route(
                        [self.position + (1, 0), self.position])
                elif tile_right.tile != Tile.WALKABLE and tile_right.tile != Tile.ROBOT:
                    self.invalidate_and_declare_route(
                        [self.position - (1, 0), self.position])
                else:
                    if random.random() < 0.5:
                        self.invalidate_and_declare_route(
                            [self.position + (1, 0), self.position])
                    else:
                        self.invalidate_and_declare_route(
                            [self.position - (1, 0), self.position])
            else:

                tile_down = self.env.tile_map[(self.position - (0, 1))]
                tile_up = self.env.tile_map[(self.position + (0, 1))]

                if tile_down.tile != Tile.WALKABLE and tile_down.tile != Tile.ROBOT:
                    self.invalidate_and_declare_route(
                        [self.position + (0, 1), self.position])
                elif tile_up.tile != Tile.WALKABLE and tile_up.tile != Tile.ROBOT:
                    self.invalidate_and_declare_route(
                        [self.position - (0, 1), self.position])
                else:
                    if random.random() < 0.5:
                        self.invalidate_and_declare_route(
                            [self.position + (0, 1), self.position])
                    else:
                        self.invalidate_and_declare_route(
                            [self.position - (0, 1), self.position])

        else:
            steps = [self.route[0]]*shift
            return self.invalidate_and_declare_route(steps)

    def invalidate_and_declare_route(self, steps):
        t = self.env.time
        for i, pos in enumerate(self.route):
            self.env.tile_map[pos].timestamp[i+t].remove(self.id)
        self.route = steps+self.route
        return self.declare_route()

    def skip_to(self, t):
        self.log = self.log + self.route[0:t]
        self.position = self.route[t-self.time]
        self.route = self.route[t-self.time:len(self.route)]
        self.direction = Direction(self.route[0] - self.route[1])
        self.time = t
        pass
