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

    def __init__(self, agent_id, position, env, route=None, direction=Direction.DOWN, task_handler=None):
        if route is None:
            route = []
        self.id = agent_id
        self.position = position
        self.home = position
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
            id_robot = self.env.raster_to_graph[self.position]
            id_pod = self.env.raster_to_graph[task]
            route_to_pod = self.env.routes[str(id_robot)][str(id_pod)]
            route = route_to_pod
            route_to_ps = self.env.routes[str(id_pod)]
            route = route + route_to_ps
            route_to_ps.reverse()
            route = route + route_to_ps
            self.route = [self.env.key_to_raster(cell)[0] for cell in route]
            return False

    def declare_route(self):
        conflicts = set()
        for i in range(len(self.route)):
            x, y = self.route[i]
            if (i + self.env.time) in self.env.tile_map[x][y].timestamp:
                self.env.tile_map[x][y].timestamp[i +
                                                  self.env.time].append(self.id)
            else:
                self.env.tile_map[x][y].timestamp[i +
                                                  self.env.time] = [self.id]

            if len(self.env.tile_map[x][y].timestamp[i + self.env.time]) > 1:
                conflicts.add((i + self.env.time, (x, y)))

            if (i + self.env.time - 1) in self.env.tile_map[x][y].timestamp and i>0:
                for other_agent in self.env.tile_map[x][y].timestamp[i + self.env.time - 1]:
                    try:
                        if self.id != other_agent and len(self.env.agents[other_agent].route) > i:

                            if self.env.agents[other_agent].route[i - 1] == (x, y) and self.env.agents[other_agent].route[i] == self.route[i-1]:
                                conflicts.add((i + self.env.time, (x, y)))
                    except BaseException:
                        breakpoint()
        return conflicts

    @staticmethod
    def get_priority():
        return random.random()

    def shift_route(self, shift, bad_conflict):

        if bad_conflict:

            if self.direction[0] == 0:  # Going up or down
                tile_left = self.env.tile_map[self.position[0] -
                                              1][self.position[1]]
                tile_right = self.env.tile_map[self.position[0] +
                                               1][self.position[1]]

                if tile_left.tile != Tile.WALKABLE and tile_left.tile != Tile.ROBOT:
                    return self.invalidate_and_declare_route(
                        [(self.position[0]+1, self.position[1]), self.position])
                elif tile_right.tile != Tile.WALKABLE and tile_right.tile != Tile.ROBOT:
                    return self.invalidate_and_declare_route(
                        [(self.position[0]-1, self.position[1]), self.position])
                else:
                    if random.random() < 0.5:
                        return self.invalidate_and_declare_route(
                            [(self.position[0]+1, self.position[1]), self.position])
                    else:
                        return self.invalidate_and_declare_route(
                            [(self.position[0]-1, self.position[1]), self.position])
            else:

                tile_down = self.env.tile_map[self.position[0]
                                              ][self.position[1] - 1]
                tile_up = self.env.tile_map[self.position[0]
                                            ][self.position[1]+1]

                if tile_down.tile != Tile.WALKABLE and tile_down.tile != Tile.ROBOT:
                    return self.invalidate_and_declare_route(
                        [(self.position[0], self.position[1]+1), self.position])
                elif tile_up.tile != Tile.WALKABLE and tile_up.tile != Tile.ROBOT:
                    return self.invalidate_and_declare_route(
                        [(self.position[0], self.position[1]-1), self.position])
                else:
                    if random.random() < 0.5:
                        return self.invalidate_and_declare_route(
                            [(self.position[0], self.position[1]+1), self.position])
                    else:
                        return self.invalidate_and_declare_route(
                            [(self.position[0], self.position[1]-1), self.position])

        else:

            steps = [self.route[0]]*shift
            return self.invalidate_and_declare_route(steps)

    def invalidate_and_declare_route(self, steps):

        t = self.env.time
        for i, (x, y) in enumerate(self.route):
            try:
                if i+t in self.env.tile_map[x][y].timestamp and self.id in self.env.tile_map[x][y].timestamp[i+t]:
                    self.env.tile_map[x][y].timestamp[i+t].remove(self.id)
                else:
                    self.env.tile_map[x][y].timestamp[i+t+1].remove(self.id)
            except KeyError:
                breakpoint()
        self.route = steps+self.route
        return self.declare_route()

    def skip_to(self, t):
        delta = t - self.time
        if len(self.route) > delta:
            self.log = self.log + self.route[0:delta]
            self.position = self.route[delta]
            self.route = self.route[delta:]
            if len(self.route) > 1:
                self.direction = (
                    self.route[0][0] - self.route[1][0], self.route[0][1] - self.route[0][1])
            else:
                self.direction = (0, 0)
        else:
            self.position = self.route[-1] if self.route else self.home
            self.route = []
            self.direction = (0, 0)
        self.time = t
