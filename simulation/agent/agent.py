from simulation.tile import Tile
from .direction import Direction
import random
import time


def find_jump(x, y):
    if abs(x[0] - y[1]) + abs(x[1] - y[1]) >= 1:
        return True
    return False


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
        self.time = 0
        self.has_to_wait = False

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
                    route_to_ps.insert(0,  self.env.raster_to_graph[tuple(map(lambda i, j: i + j,
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

    def move(self):
        if not self.route:
            return
        old_pos = self.position
        try:
            self.position = self.route.pop(0)
            self.direction = Direction(tuple(map(lambda i, j: i - j, self.position, old_pos)))
        except:
            pass
        # self.env.update_map(coord=old_pos, tile=Tile.WALKABLE)
        # self.env.update_map(coord=self.position, tile=Tile.ROBOT)

    def watch(self):
        direction = self.direction
        pos = self.position
        node = self.env.graph.get_node(self.env.raster_to_graph[pos])

        field_of_view = [[], [], []]
        next_block = tuple(map(lambda i, j: i + j, pos, direction.value))

        for n in node.adj:
            if next_block == n.coord[0]:
                if n.type != Tile.POD and n.type != Tile.POD_TAKEN:
                    if n.coord not in [item for sublist in field_of_view for item in sublist]:
                        if n.type == Tile.ROBOT:
                            field_of_view[0].append({'coord': n.coord, 'agent_id': n.agent_id})
                    for nn in n.adj:
                        if nn.type != Tile.POD and nn.type != Tile.POD_TAKEN:
                            if nn.coord not in [item for sublist in field_of_view for item in sublist]:
                                if nn.type == Tile.ROBOT:
                                    field_of_view[1].append({'coord': nn.coord, 'agent_id': nn.agent_id})
                            for nnn in nn.adj:
                                if nnn.type != Tile.POD and nnn.type != Tile.POD_TAKEN:
                                    if nnn.type == Tile.ROBOT:
                                        field_of_view[2].append({'coord': nnn.coord, 'agent_id': nnn.agent_id})

        if not [item for sublist in field_of_view for item in sublist]:
            field_of_view = []

        self.view = field_of_view
