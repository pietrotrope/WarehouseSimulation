from simulation.tile import Tile
from .direction import Direction
import random
import time


def detect_possible_conflict(agent, i):
    x, y = agent.route[i]

    if (i + agent.env.time + 1) in agent.env.tile_map[x][y].timestamp:
        if len(agent.env.tile_map[x][y].timestamp[i + agent.env.time + 1]) != 0:
            other_agent = agent.env.agents[agent.env.tile_map[x][y].timestamp[i +
                                                                              agent.env.time + 1][0]]
            if i>0 and len(other_agent.route)>i+1 and other_agent.route[i+1] == agent.route[i-1]:
                return (i+agent.env.time, agent.id, 1, 0)        
            return (i+agent.env.time, agent.id, 0, 0)

    for other_agent in agent.env.tile_map[x][y].timestamp[i + agent.env.time + 2]:
        if agent.id != other_agent and i>0:
            if agent.env.agents[other_agent].route[i+1] == agent.route[i]:
                return (i+agent.env.time, agent.id, 1, 1)
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

    def declare_route(self, pos=0):
        for i in range(pos, len(self.route)):
            conflict = detect_possible_conflict(self, i)
            if conflict:

                return conflict
            x, y = self.route[i]
            self.env.tile_map[x][y].timestamp[i +
                                              self.env.time + 1].append(self.id)

        return None

    def shift_route(self, i, shift, bad_conflict):
        to_add = []
        if bad_conflict:
            
            direction=(0,0)
            if i>0 and i<len(self.route):          
                direction = (abs(self.route[i-1][0]-self.route[i][0]),
                            abs(self.route[i-1][1]-self.route[i][1]))

            if direction[0] == 0 and direction[1] != 0:  # go up or down
                new_i = i
                while new_i > 0:
                    pos = self.route[new_i-1]
                    tmap = self.env.tile_map
                    if pos[1]-1 >= 0 and not tmap[pos[0]][pos[1]-1].timestamp[new_i + self.env.time] and tmap[pos[0]][pos[1]-1].tile == Tile.WALKABLE:
                        to_add = [(pos[0], pos[1]-1)
                                  for _ in range(shift + i - new_i)] + [pos]
                        return self.edit_route(new_i-1, to_add)
                    elif pos[1]+1 < self.env.map_shape[1] and not tmap[pos[0]][pos[1]+1].timestamp[new_i + self.env.time] and tmap[pos[0]][pos[1]+1].tile == Tile.WALKABLE:
                        to_add = [(pos[0], pos[1]+1)
                                  for _ in range(shift + i - new_i)] + [pos]
                        return self.edit_route(new_i-1, to_add)
                    else:
                        new_i -= 1
            elif direction[0] != 0 and direction[1] == 0:
                new_i = i
                while new_i > 0:
                    pos = self.route[new_i-1]
                    tmap = self.env.tile_map
                    if pos[0]-1 >= 0 and not tmap[pos[0]-1][pos[1]].timestamp[new_i + self.env.time] and tmap[pos[0]-1][pos[1]].tile == Tile.WALKABLE:
                        to_add = [(pos[0]-1, pos[1])
                                  for _ in range(shift + i - new_i)] + [pos]
                        return self.edit_route(new_i -1, to_add)
                    elif pos[0]+1 < self.env.map_shape[0] and not tmap[pos[0]+1][pos[1]].timestamp[new_i + self.env.time] and tmap[pos[0]+1][pos[1]].tile == Tile.WALKABLE:
                        to_add = [(pos[0]+1, pos[1])
                                  for _ in range(shift + i - new_i)] + [pos]
                        return self.edit_route(new_i -1, to_add)
                    else:
                        new_i -= 1
            else:
                new_i = i
                while new_i > 0:
                    pos = self.route[new_i-1 -self.env.time]
                    tmap = self.env.tile_map
                    if pos[1]-1 >= 0 and not tmap[pos[0]][pos[1]-1].timestamp[new_i + self.env.time] and tmap[pos[0]][pos[1]-1].tile == Tile.WALKABLE:
                        to_add = [(pos[0], pos[1]-1)
                                  for _ in range(shift + i - new_i)] + [pos]
                        return self.edit_route(new_i-1, to_add)
                    elif pos[1]+1 < self.env.map_shape[1] and not tmap[pos[0]][pos[1]+1].timestamp[new_i + self.env.time] and tmap[pos[0]][pos[1]+1].tile == Tile.WALKABLE:
                        to_add = [(pos[0], pos[1]+1)
                                  for _ in range(shift + i - new_i)] + [pos]
                        return self.edit_route(new_i-1, to_add)
                    elif pos[0]-1 >= 0 and not tmap[pos[0]-1][pos[1]].timestamp[new_i + self.env.time] and tmap[pos[0]-1][pos[1]].tile == Tile.WALKABLE:
                        to_add = [(pos[0]-1, pos[1])
                                  for _ in range(shift + i - new_i)] + [pos]
                        return self.edit_route(new_i -1, to_add)
                    elif pos[0]+1 < self.env.map_shape[0] and not tmap[pos[0]+1][pos[1]].timestamp[new_i + self.env.time] and tmap[pos[0]+1][pos[1]].tile == Tile.WALKABLE:
                        to_add = [(pos[0]+1, pos[1])
                                  for _ in range(shift + i - new_i)] + [pos]
                        return self.edit_route(new_i -1, to_add)
                    else:
                        new_i -= 1
        else:
            j = 1
            while i-j >= 0 and self.route[i-j-self.env.time] == self.route[i-self.env.time]:
                j += 1
            to_add = [self.route[i-j-self.env.time] for _ in range(shift+j-1)]
            return self.edit_route(i-j-self.env.time, to_add)

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
