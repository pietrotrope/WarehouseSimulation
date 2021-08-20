from simulation.tile import Tile
from .direction import Direction
import random
import time


def find_jump(x, y):
    if abs(x[0]-y[1]) + abs(x[1]-y[1]) >= 1:
        return True
    return False


def detect_collision(agent, i):
    # return collision_type, time, agent, other_agent
    x, y = agent.route[i]

    agents = agent.env.tile_map[x][y].timestamp[i + agent.env.time]
    if len(agents) > 0 and agents[0] != agent.id:
        other_agent = agent.env.agents[agents[0]]
        # se ho raggiunto questa porzione di codice c'è al momento un agente dove voglio andare
        # devo controllare se vuole spostarsi dove sono io, stare fermo dove voglio andare io,
        # o andarsene, cosi da agire di conseguenza
        if len(other_agent.route) > i:
            # l'altro agente si muoverà
            if i > 0:
                if other_agent.route[i] == agent.route[i-1]:
                    # controllo il caso in cui voglia venire dove sono io e quindi dobbiamo swappare
                    return 0, i, agent.id, other_agent.id
                if other_agent.route[i] == other_agent.route[i-1]:
                    # controllo se sta fermo e quindi devo stare fermo anche io
                    return 1, i, agent.id, -1
            else:
                if other_agent.route[i] == agent.position:
                    # controllo il caso in cui voglia venire dove sono io e quindi dobbiamo swappare
                    return 0, i, agent.id, other_agent.id
                if other_agent.route[i] == other_agent.position:
                    # controllo se sta fermo e quindi devo stare fermo anche io
                    return 1, i, agent.id, -1
        else:
            # l'agente starà fermo qui, quindi attendo che finisca cosi prende una route
            return 1, i, agent.id, -1
    else:
        # al tempo attuale non c'è nessuno, vedo se quindi c'è qualcuno al tempo in cui voglio andarci
        agents = agent.env.tile_map[x][y].timestamp[i + agent.env.time + 1]
        # se c'è qualcuno, controllo se io ero già qui o no. in caso attendo un turno
        if len(agents) > 0 and agents[0] != agent.id:
            other_agent = agent.env.agents[agents[0]]
            if i > 0:
                if agent.route[i] == agent.route[i-1]:
                    return 1, i, other_agent.id, -1
                else:
                    return 1, i, agent.id, -1
            else:
                if agent.route[i] == agent.position:
                    return 1, i, other_agent.id, -1
                else:
                    return 1, i, agent.id, -1
    return None


def make_step(agents, to_time, pos=0):
    for i in range(pos, to_time):
        moves = []
        swap_phases = []
        for agent in agents:
            if agent.task != None:
                if agent.swap_phase == 0:
                    collision = detect_collision(agent, i)
                    if collision:
                        for agent1, x1, y1, t in moves:
                            agent1.env.tile_map[x1][y1].timestamp[t].remove(
                                agent1.id)
                        for ag in swap_phases:
                            ag.swap_phase += 1
                        return collision
                else:
                    agent.swap_phase -= 1
                    swap_phases.append(agent)

                x, y = agent.route[i]
                agent.env.tile_map[x][y].timestamp[i + agent.env.time + 1].append(agent.id)
                moves.append((agent, x, y, i + agent.env.time + 1))
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
        self.swap_phase = 0

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

    def shift_route(self, i):
        if i <= 0:
            return self.edit_route(0, [self.position])
        return self.edit_route(i, [self.route[i-1]])

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
