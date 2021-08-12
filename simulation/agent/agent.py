from simulation.tile import Tile
from .direction import Direction
import random

movement = {
    Direction.UP: (0, 1),
    Direction.DOWN: (0, -1),
    Direction.LEFT: (-1, 0),
    Direction.RIGHT: (1, 0)
}


def detect_conflicts(agent, i):
    x, y = agent.route[i]
    check = (i + agent.env.time + 1) in agent.env.tile_map[x][y].timestamp
    conflicts = set()
    if check:
        if len(agent.env.tile_map[x][y].timestamp[i + agent.env.time + 1]) > 1:
            tmp = set([(i + agent.env.time + 1, (x, y), agent_id, 0)
                       for agent_id in agent.env.tile_map[x][y].timestamp[i + agent.env.time + 1]])
            conflicts = conflicts.union(tmp)

        if i > 0:
            tmp = set([(i + agent.env.time + 1, (x, y), other_agent, 1)
                       for other_agent in agent.env.tile_map[x][y].timestamp[i + agent.env.time]
                       if agent.id != other_agent and len(agent.env.agents[other_agent].route) > i
                       if agent.env.agents[other_agent].route[i] == agent.route[i - 1]
                       ])
            conflicts = conflicts.union(tmp)
    return conflicts


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
            id_robot = str(self.env.raster_to_graph[self.position])
            id_pod = str(self.env.raster_to_graph[task])
            route_to_pod = self.env.routes[id_robot][id_pod]
            if not route_to_pod:
                route_to_pod = [self.env.raster_to_graph[self.position]]
            route = route_to_pod
            # TODO se route_to_pod[-1]!=route_to_ps[0] aggiungi 2 step, uno uguale a route_to_pod[-1] ed uno che
            #  porta alla cella vicino a route_to_ps[0]
            route_to_ps = self.env.routes[id_pod].copy()
            route = route + route_to_ps.copy()
            route_to_ps.reverse()
            route = route + route_to_ps
            self.route = [self.env.key_to_raster(cell)[0] for cell in route]
            return False

    def declare_route(self):
        conflicts = set()
        for i in range(len(self.route)):
            x, y = self.route[i]
            self.env.tile_map[x][y].timestamp[i + self.env.time + 1].append(self.id)
            conflicts = conflicts.union(detect_conflicts(self, i))
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

                tile_down = self.env.tile_map[self.position[0]][self.position[1] - 1]
                tile_up = self.env.tile_map[self.position[0]][self.position[1] + 1]

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
            self.env.tile_map[x][y].timestamp[i + t + 1].remove(self.id)
        self.route = steps + self.route
        return self.declare_route()

    def skip_to(self, t):
        delta = t - self.time
        if delta > 0:
            if len(self.route) >= delta:
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
                else:
                    self.log.append(self.position)
                self.route = []
                self.direction = (0, 0)
            self.time = t
