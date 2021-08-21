from simulation.tile import Tile
from .direction import Direction
import random
import time


def find_jump(x, y):
    return abs(x[0] - y[1]) + abs(x[1] - y[1]) >= 1


class Agent:

    def __init__(self, agent_id, position, env, route=None, direction=Direction.DOWN, task_handler=None):
        self.view = None
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
        self.swap_phase = [0, self.id]

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

            route_to_ps = self.env.routes[id_pod].copy()
            if route_to_pod[-1] != route_to_ps[0]:
                start = self.env.key_to_raster(route_to_ps[0])[0]
                end = self.env.key_to_raster(route_to_pod[-1])[0]
                movement = tuple(map(lambda i, j: i - j, start, end))
                if self.env.raster_map[tuple(map(lambda i, j: i + j, end, (0, movement[1])))] == Tile.WALKABLE.value:
                    route_to_ps.insert(0,
                                       self.env.raster_to_graph[tuple(map(lambda i, j: i + j,
                                                                          end, (0, movement[1])))])
                else:
                    route_to_ps.insert(0, self.env.raster_to_graph[tuple(map(lambda i, j: i + j,
                                                                             end, (movement[0], 0)))])
                route_to_ps.insert(0, route_to_pod[-1])
            route = [*route, *route_to_ps.copy()]
            route_to_ps.reverse()
            route = [*route, *route_to_ps]
            self.route = [self.env.key_to_raster(cell)[0] for cell in route]
            return False

    def shift_route(self, i):
        if i <= 0:
            return self.edit_route(0, [self.position])
        return self.edit_route(i, [self.route[i - 1]])

    def edit_route(self, i, steps):
        self.route = self.route[0:i] + steps + self.route[i:]

    def skip_to(self, delta):
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

    def detect_collision(self, i):
        # return collision_type, time, agent, other_agent
        x, y = self.route[i]

        agents = self.env.tile_map[x][y].timestamp[i + self.env.time]
        if len(agents) > 0 and agents[0] != self.id:
            other_agent = self.env.agents[agents[0]]
            # se ho raggiunto questa porzione di codice c'è al momento un agente dove voglio andare
            # devo controllare se vuole spostarsi dove sono io, stare fermo dove voglio andare io,
            # o andarsene, cosi da agire di conseguenza

            if self.swap_phase[0] > 0:
                if other_agent.id != self.id and other_agent.id != self.swap_phase[1]:
                    return 1, i, other_agent.id, -1
            else:
                if len(other_agent.route) > i:
                    # l'altro agente si muoverà
                    if i > 0:
                        if other_agent.route[i] == self.route[i - 1]:
                            # controllo il caso in cui voglia venire dove sono io e quindi dobbiamo swappare
                            return 0, i, self.id, other_agent.id
                        if other_agent.route[i] == other_agent.route[i - 1]:
                            # controllo se sta fermo e quindi devo stare fermo anche io
                            return 1, i, self.id, -1
                    else:
                        if other_agent.route[i] == self.position:
                            # controllo il caso in cui voglia venire dove sono io e quindi dobbiamo swappare
                            return 0, i, self.id, other_agent.id
                        if other_agent.route[i] == other_agent.position:
                            # controllo se sta fermo e quindi devo stare fermo anche io
                            return 1, i, self.id, -1

                    if other_agent.swap_phase[0] != 0:
                        return 1, i, self.id, -1

                    new_agents = self.env.tile_map[x][y].timestamp[i +
                                                                self.env.time + 1]
                    if new_agents and new_agents[0] != self.id:
                        return 1, i, self.id, -1
                else:
                    # l'agente starà fermo qui, quindi attendo che finisca cosi prende una route
                    return 1, i, self.id, -1
        # al tempo attuale non c'è nessuno, vedo se quindi c'è qualcuno al tempo in cui voglio andarci
        agents = self.env.tile_map[x][y].timestamp[i + self.env.time + 1]
        # se c'è qualcuno, controllo se io ero già qui o no. in caso attendo un turno
        if len(agents) > 0 and agents[0] != self.id:
            other_agent = self.env.agents[agents[0]]

            if self.swap_phase[0] > 0:
                if other_agent.id != self.id and other_agent.id != self.swap_phase[1]:
                    print(self.env.time)
                    return 1, i, other_agent.id, -1
            else:
                if i > 0:
                    if self.route[i] == self.route[i - 1]:
                        return 1, i, other_agent.id, -1
                    else:
                        return 1, i, self.id, -1
                else:
                    if self.route[i] == self.position:
                        return 1, i, other_agent.id, -1
                    else:
                        return 1, i, self.id, -1
        return None
