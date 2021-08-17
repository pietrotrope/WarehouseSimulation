from simulation.tile import Tile
from .direction import Direction
import random
import time


def find_jump(x, y):
    if abs(x[0]-y[1]) + abs(x[1]-y[1]) >= 1:
        return True
    return False


def detect_possible_conflict(agent, i):
    x, y = agent.route[i]

    if (i + agent.env.time + 1) in agent.env.tile_map[x][y].timestamp:
        if len(agent.env.tile_map[x][y].timestamp[i + agent.env.time + 1]) != 0:
            print(agent.env.tile_map[x][y].timestamp[i + agent.env.time + 1])
            other_agent = agent.env.agents[agent.env.tile_map[x][y].timestamp[i +
                                                                              agent.env.time + 1][0]]
            if len(other_agent.route) > i:
                if i == 0 and agent.position == other_agent.route[i]:
                    return (i, agent.id, other_agent.id)
                else:
                    if other_agent.route[i+1] == agent.route[i-1]:
                        return (i, agent.id, other_agent.id)
            if i == 0:
                return (i, agent.id, -1)
            return (i, agent.id, -1)

    for other_agent in agent.env.tile_map[x][y].timestamp[i + agent.env.time + 2]:
        if agent.id != other_agent and i > 0:
            if agent.env.agents[other_agent].route[i] == agent.route[i+1]:
                return (i, agent.id, -1)
    return None


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
            # TODO se route_to_pod[-1]!=route_to_ps[0] aggiungi 2 step, uno uguale a route_to_pod[-1] ed uno che porta alla cella vicino a
            # route_to_ps[0]
            route_to_ps = self.env.routes[id_pod].copy()
            route = [*route, *route_to_ps.copy()]
            route_to_ps.reverse()
            route = [*route, *route_to_ps]
            self.route = [self.env.key_to_raster(cell)[0] for cell in route]
            return False

    def declare_route(self, pos=0, swap=False):
        if not swap:
            conflict = detect_possible_conflict(self, pos)
            if conflict:
                return conflict
        x, y = self.route[pos]
        for i in range(pos + 1, len(self.route)):
            conflict = detect_possible_conflict(self, i)
            if conflict:
                return conflict
            x, y = self.route[i]
            self.env.tile_map[x][y].timestamp[i +
                                              self.env.time + 1].append(self.id)
        return None

    def shift_route(self, i):
        if i <= 0:
            print(i)
            return self.edit_route(0, [self.position])
        return self.edit_route(i, [self.route[i-1]])

    def edit_route(self, i, steps):
        self.route = self.route[0:i] + steps + self.route[i:]

    def skip_to(self, t):
        delta = t - self.time
        if delta > 0:
            if len(self.route) >= delta:
                self.log += self.route[0:delta]
                self.position = self.route[delta - 1]
                self.route = self.route[delta:]
                if len(self.route) > 1:
                    self.direction = (
                        self.route[0][0] - self.route[1][0], self.route[0][1] - self.route[1][1])
                else:
                    self.direction = (0, 0)
            else:
                if self.route:
                    self.position = self.route[-1]
                    self.log += self.route
                    self.route = []
                else:
                    self.position = self.home
                    self.log.append(self.position)
                self.direction = (0, 0)
            self.time = t
