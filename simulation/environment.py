from random import Random, random
import sys

import pandas as pd
import numpy as np
import csv
import json
from collections import defaultdict

from simulation.agent.agent import Agent, detect_conflicts
from simulation.agent.task_handler import TaskHandler
from simulation.cell import Cell
from simulation.tile import Tile
from simulation.graph.graph import Graph


class Environment:

    def __init__(self, map_path=None, cfg_path='../config.yaml', task_number=50, agent_number=8, scheduling=None,
                 save=False, run=True):
        self.scheduling = scheduling
        self.raster_map = None
        self.tile_map = None
        self.map_shape = ()
        self.graph = None
        self.agents = {}
        self.raster_to_graph = {}
        self.__load_map(map_path)
        self.__gen_graph()
        self.task_handler = TaskHandler(self, task_number)
        self.__spawn_agents(cfg_path)
        self.time = 0
        self.task_pool = {}
        self.task_number = task_number
        self.agent_number = agent_number
        self.save = save

        if self.graph is None or self.raster_map is None:
            raise Exception("Error while Initializing environment")

        with open('astar/astarRoutes.json', 'r') as f:
            self.routes = json.load(f)
        if run:
            self.run()

    def new_simulation(self, task_number=50, run=True):
        self.time = 0
        self.task_handler = TaskHandler(self, task_number)
        for agent in self.agents:
            agent.position = agent.home
            agent.task = None
            agent.route = []
            agent.time = 0
            agent.log = [agent.position]
            agent.task_handler = self.task_handler
        for x in range(len(self.tile_map)):
            for y in range(len(self.tile_map[x])):
                self.tile_map[x][y].timestamp = defaultdict(list)
        if run:
            self.run()

    def key_to_raster(self, key):
        return self.graph.get_node(key).coord

    def __get_picking_stations_number(self):
        picking_stations_columns = np.count_nonzero(
            self.raster_map == 4, axis=0)
        picking_stations_columns = " {} ".format(
            " ".join(map(str, picking_stations_columns)))
        picking_stations_columns = [
            [int(y) for y in x.split()] for x in picking_stations_columns.split('0')]
        picking_stations_columns = [
            x for x in picking_stations_columns if x != []]
        return len(picking_stations_columns)

    def get_pods(self):
        pods = [(i, j)
                for i, line in enumerate(self.raster_map)
                for j, cell in enumerate(line)
                if cell == Tile.POD.value]
        return pods

    def update_map(self, coord=None, key=None, tile=Tile.WALKABLE):
        if coord is not None:
            node = self.graph.get_node(self.raster_to_graph[coord])
            node.type = tile
            self.raster_map[coord[0]][coord[1]] = tile.value
            self.tile_map[coord[0]][coord[1]].tile = tile
        if key is not None:
            node = self.graph.get_node(key)
            node.type = tile
            x, y = self.key_to_raster(key)[0]
            self.raster_map[x][y] = tile.value

    def __load_map(self, map_path):
        map_path = 'map.csv' if map_path is None else map_path
        self.raster_map = np.array(pd.read_csv(map_path, header=None))
        self.map_shape = self.raster_map.shape
        self.__gen_tile_map()

    def __gen_graph(self):
        picking_station_number = self.__get_picking_stations_number()

        graph_nodes = self.map_shape[0] * self.map_shape[1] - \
                      (np.count_nonzero(self.raster_map == 4) -
                       picking_station_number)
        self.graph = Graph(graph_nodes)

        picking_stations = [[] for _ in range(picking_station_number)]
        upper_station = [(0, 0) for _ in range(picking_station_number)]
        count = -1
        agent_count = 0

        for i in range(self.map_shape[0]):
            current_picking_station: int = -1
            for j in range(self.map_shape[1]):
                if self.raster_map[i][j] == 4:
                    if self.raster_map[i - 1][j] == self.raster_map[i][j - 1] == 0:
                        current_picking_station += 1
                        count += 1
                        upper_station[current_picking_station] = (i, j)
                        node = self.graph.get_node(count)
                        node.coord = [(i, j)]
                        node.type = Tile(self.raster_map[i][j])
                        picking_stations[current_picking_station].append(
                            (i, j))
                        self.raster_to_graph[(i, j)] = count
                    elif self.raster_map[i][j - 1] == 0:
                        current_picking_station += 1
                    self.raster_to_graph[(
                        i, j)] = self.raster_to_graph[upper_station[current_picking_station]]
                    picking_stations[current_picking_station].append((i, j))
                else:
                    if self.raster_map[i][j] == 1:
                        self.agents[agent_count] = (i, j)
                        agent_count += 1
                    count += 1
                    node = self.graph.get_node(count)
                    node.coord = [(i, j)]
                    node.type = Tile(self.raster_map[i][j])
                    self.raster_to_graph[(i, j)] = count

                node = self.raster_to_graph[(i, j)]
                if j != 0:
                    self.graph.add_edge(node, self.raster_to_graph[(i, j - 1)])
                if i != 0:
                    self.graph.add_edge(node, self.raster_to_graph[(i - 1, j)])

        for picking_station in picking_stations:
            node = self.graph.get_node(self.raster_to_graph[picking_station[0]])
            node.coord = picking_station

    def __gen_tile_map(self):
        self.tile_map = np.zeros_like(self.raster_map).tolist()
        self.tile_map = [[Cell(Tile(cell)) for j, cell in enumerate(row)] for i, row in enumerate(self.raster_map)]

    def __spawn_agents(self, cfg_path):
        positions = self.agents
        self.agents = [Agent(i, positions[i], self, task_handler=self.task_handler) for i in range(len(positions))]

    def run(self):
        conflicts = set()
        task_ends = [0 for _ in range(self.agent_number)]
        done = [False for _ in range(self.agent_number)]
        while True:
            for i, agent in enumerate(self.agents):
                if not agent.route:
                    done[i] = agent.get_task()
                    if done[i]:
                        agent.position = agent.home
                    conflicts = conflicts.union(agent.declare_route())
                task_ends[i] = self.time + \
                               len(agent.route) if not done[i] else sys.maxsize
            if conflicts:
                conflict_time = min(conflicts, key=lambda t: t[0])[0]
                if conflict_time > min(task_ends):
                    self.time = min(task_ends)
                    for agent in self.agents:
                        agent.skip_to(self.time)
                    continue

                self.time = conflict_time - 1
                for agent in self.agents:
                    agent.skip_to(self.time)

                while conflict_time in list(map(lambda x: x[0], conflicts)):
                    first_conflict = min(conflicts, key=lambda t: t[0])
                    conflicts = conflicts.union(self.solve_conflict(first_conflict))
                    conflicts.remove(first_conflict)
            else:
                self.time = min(task_ends)
                for agent in self.agents:
                    agent.skip_to(self.time)

            if done.count(True) == len(done):
                if self.save:
                    self.save_data()
                break

    def save_data(self):
        res = [agent.log for agent in self.agents]
        with open("./out.csv", "w") as f:
            wr = csv.writer(f)
            wr.writerows(res)

    def solve_conflict(self, conflict):
        time, pos, agent, flag = conflict
        new_conflicts = set()

        # TODO Problema assegnazione task contemporanea stessa cella

        #if flag:
            #new_conflicts = new_conflicts.union(self.agents[agent].shift_route(1, True))

        """
        if len(priorities) == 2:
            priority_agent = max(priorities)[1]
            for agent in agents:
                if agent is not priority_agent and len(self.agents[agent].route) > 0:
                    tmp_pos = self.agents[agent].position
                    if time in self.tile_map[tmp_pos[0]][tmp_pos[1]].timestamp:
                        overlap_path_agents = self.tile_map[tmp_pos[0]
                                                            ][tmp_pos[1]].timestamp[time]

                        new_conflicts = new_conflicts.union(self.agents[agent].shift_route(
                            2, priority_agent in overlap_path_agents))
                    else:
                        new_conflicts = new_conflicts.union(self.agents[agent].shift_route(
                            2, False))


        elif len(priorities) > 2:
            priorities.sort(reverse=True)
            for i, agent in enumerate(priorities):
                if i > 0 and len(self.agents[agent[1]].route) > 0:
                    x, y = self.agents[agent[1]].route[0]
                    if time in self.tile_map[x][y].timestamp:
                        overlap_path_agents = self.tile_map[x][y].timestamp[time]
                        new_conflicts = new_conflicts.union(self.agents[
                            agent[1]].shift_route(i + 1, overlap_path_agents))
        """
        return new_conflicts
