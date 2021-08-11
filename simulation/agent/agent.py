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
        self.log = [position]
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
                for agent in self.env.tile_map[x][y].timestamp[i + self.env.time]:
                    conflicts.add((i + self.env.time, (x, y), agent, 0))
            else:
                self.env.tile_map[x][y].timestamp[i +
                                                  self.env.time] = [self.id]

            if (i + self.env.time - 1) in self.env.tile_map[x][y].timestamp and i > 0:
                for other_agent in self.env.tile_map[x][y].timestamp[i + self.env.time - 1]:
                    if self.id != other_agent and len(self.env.agents[other_agent].route) > i:
                        if self.env.agents[other_agent].route[i - 1] == self.route[i] and \
                                self.env.agents[other_agent].route[i] == self.route[i - 1]:
                            conflicts.add(
                                (i + self.env.time, (x, y), self.env.agents[other_agent], 1))
                            print(self.env.time + i)
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
                    to_add = [(self.position[0] + 1, self.position[1])] * shift
                    return self.invalidate_and_declare_route(to_add + [self.position])
                elif tile_right.tile != Tile.WALKABLE and tile_right.tile != Tile.ROBOT:
                    to_add = [(self.position[0] - 1, self.position[1])] * shift
                    return self.invalidate_and_declare_route(to_add + [self.position])
                else:
                    if random.random() < 0.5:
                        to_add = [
                            (self.position[0] + 1, self.position[1])] * shift
                        return self.invalidate_and_declare_route(to_add + [self.position])
                    else:
                        to_add = [
                            (self.position[0] - 1, self.position[1])] * shift
                        return self.invalidate_and_declare_route(to_add + [self.position])
            else:

                tile_down = self.env.tile_map[self.position[0]
                                              ][self.position[1] - 1]
                tile_up = self.env.tile_map[self.position[0]
                                            ][self.position[1] + 1]

                if tile_down.tile != Tile.WALKABLE and tile_down.tile != Tile.ROBOT:
                    to_add = [(self.position[0], self.position[1] + 1)] * shift
                    return self.invalidate_and_declare_route(to_add + [self.position])
                elif tile_up.tile != Tile.WALKABLE and tile_up.tile != Tile.ROBOT:
                    to_add = [(self.position[0], self.position[1] - 1)] * shift
                    return self.invalidate_and_declare_route(to_add + [self.position])
                else:
                    if random.random() < 0.5:
                        to_add = [
                            (self.position[0], self.position[1] + 1)] * shift
                        return self.invalidate_and_declare_route(to_add + [self.position])
                    else:
                        to_add = [
                            (self.position[0], self.position[1] - 1)] * shift
                        return self.invalidate_and_declare_route(to_add + [self.position])
        else:
            steps = [self.route[0]] * shift
            return self.invalidate_and_declare_route(steps)

    def invalidate_and_declare_route(self, steps):
        t = self.env.time
        for i, (x, y) in enumerate(self.route):
            self.env.tile_map[x][y].timestamp[i + t].remove(self.id)
        self.route = steps + self.route
        return self.declare_route()

    def skip_to(self, t):
        delta = t - self.time
        if delta > 0:
            if len(self.route) >= delta and delta >= 0:
                self.log = self.log + self.route[0:delta]
                self.position = self.route[delta - 1]
                self.route = self.route[delta:]
                if len(self.route) > 1:
                    self.direction = (
                        self.route[0][0] - self.route[1][0], self.route[0][1] - self.route[0][1])
                else:
                    self.direction = (0, 0)
            else:
                self.position = self.route[-1] if self.route else self.home
                if len(self.route) > 0:
                    self.log = self.log + self.route
                    print("time")
                    print(self.time)
                    print("skip to")
                    print(t)
                    print()
                else:
                    self.log.append(self.position)
                self.route = []
                self.direction = (0, 0)
            self.time = t
