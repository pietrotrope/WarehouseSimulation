import simulation
import sys

import pandas as pd
import numpy as np
import csv
import json
import copy

from itertools import count
from simulation.agent.agent import Agent
from simulation.agent.task_handler import TaskHandler
from simulation.cell import Cell
from simulation.tile import Tile
from simulation.graph.graph import Graph

import time


class Environment:

    def __init__(self, map_path=None, cfg_path='../config.yaml', task_number=100, agent_number=8, scheduling=None,
                 save=False, run=True, simulation_name=""):
        self.simulation_name = simulation_name
        self.scheduling = scheduling
        self.raster_map = None
        self.tile_map = None
        self.map_shape = ()
        self.graph = None
        self.agents = {}
        self.agent_number = agent_number
        self.raster_to_graph = {}
        self.__load_map(map_path)
        self.__gen_graph()
        self.pods = self._get_pods()
        self.task_handler = TaskHandler(self, task_number)
        self.__spawn_agents(cfg_path)
        self.time = 0
        self.task_pool = {}
        self.task_number = task_number
        self.save = save

        if self.graph is None or self.raster_map is None:
            raise Exception("Error while Initializing environment")

        with open('astar/astarRoutes.json', 'r') as f:
            self.routes = json.load(f)
        if run:
            self.run()

    def ga_entrypoint(self, task_number, scheduling):
        return self.new_simulation(task_number, run=True, save=False, scheduling=scheduling)

    def new_simulation(self, task_number=100, run=True, save=False, scheduling=None, new_task_pool=False, simulation_name=None):
        if simulation_name != None:
            self.simulation_name = simulation_name
        self.time = 0
        self.scheduling = scheduling
        self.task_number = task_number
        if new_task_pool:
            self.task_handler.new_task_pool(task_number)
        else:
            self.task_handler.same_task_pool(task_number)

        self.save = save
        for agent in self.agents:
            agent.position = agent.home
            agent.task = None
            agent.route = []
            agent.time = 0
            agent.log = [agent.position]
            agent.task_handler = self.task_handler
        for x in range(self.map_shape[0]):
            for y in range(self.map_shape[1]):
                self.tile_map[x][y].timestamp.clear()
        if run:
            return self.run()

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

    def _get_pods(self):
        pods = []
        for i, line in enumerate(self.raster_map):
            for j, cell in enumerate(line):
                if cell == Tile.POD.value:
                    pods.append((i, j))
        return pods

    def get_pods(self):
        return self.pods

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
                      (np.count_nonzero(self.raster_map == 4) - picking_station_number)
        self.graph = Graph(graph_nodes)

        picking_stations = [[] for _ in range(picking_station_number)]
        upper_station = [(0, 0) for _ in range(picking_station_number)]
        count = -1
        agent_count = 0

        for i in range(self.map_shape[0]):
            current_picking_station = -1
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
            node = self.graph.get_node(
                self.raster_to_graph[picking_station[0]])
            node.coord = picking_station

    def __gen_tile_map(self):
        self.tile_map = [[Cell(Tile(cell)) for cell in row] for row in self.raster_map]

    def __spawn_agents(self, cfg_path):
        positions = self.agents
        self.agents = []

        for i in range(len(positions)):
            agent = Agent(i, positions[i], self,
                          task_handler=self.task_handler)

            self.agents.append(agent)

    def task_ending_time(self, agent):
        return self.time + len(agent.route)

    def make_step(self, to_time, pos=0):
        moves = []
        swap_phases = []
        for i in range(pos, to_time):
            moves.clear()
            swap_phases.clear()
            for agent in self.agents:
                if agent.task is not None:
                    collision = agent.detect_collision(i)
                    if collision:
                        for agent1, x1, y1, t in moves:
                            self.tile_map[x1][y1].timestamp[t].remove(agent1.id)
                        for ag in swap_phases:
                            ag[0].swap_phase[0] += 1
                            ag[0].swap_phase[1] = ag[1]
                        return collision
                    else:
                        if agent.swap_phase[0] > 0:
                            agent.swap_phase[0] -= 1
                            swap_phases.append((agent, agent.swap_phase[1]))
                            if agent.swap_phase[0] == 0:
                                agent.swap_phase[1] = agent.id

                    x, y = agent.route[i]
                    i_plus_time_plus_one = i + self.time + 1
                    self.tile_map[x][y].timestamp[i_plus_time_plus_one].append(agent.id)
                    moves.append((agent, x, y, i_plus_time_plus_one))
        return None

    def run(self):
        task_ending_times = [sys.maxsize for _ in range(self.agent_number)]
        done = [False for _ in range(self.agent_number)]


        for simulation_time in count(0):
            # Assign tasks
            for agent in self.agents:
                if not agent.route:
                    done[agent.id] = agent.get_task()
                    if done[agent.id]:
                        agent.position = agent.home
                        task_ending_times[agent.id] = sys.maxsize
                        agent.task = None
                    else:
                        for update_agent in self.agents:
                            task_ending_times[update_agent.id] = self.task_ending_time(update_agent)

            if self.simulation_ended(done):
                if self.save:
                    self.save_data()
                return self.compute_metrics()

            collision = self.make_step(min(task_ending_times) - self.time)
            while collision:
                self.avoid_collision(collision)

                if collision[3] != -1:
                    task_ending_times[collision[3]] = self.task_ending_time(self.agents[collision[3]])

                task_ending_times[collision[2]] = self.task_ending_time(self.agents[collision[2]])

                collision = self.make_step(min(task_ending_times) - self.time, collision[1])

            self.update_simulation_time(min(task_ending_times))

    def simulation_ended(self, done):
        return done.count(True) == len(done)

    def update_simulation_time(self, new_time):
        for agent in self.agents:
            agent.skip_to(new_time - self.time)
        self.time = new_time

    def compute_metrics(self):
        res = [agent.log for agent in self.agents]

        TTC = 0
        res_lengths = []
        for r in res:
            res_lengths.append(len(r))
            TTC += len(r)

        BU = min(res_lengths) / max(res_lengths)
        TT = max(res_lengths)

        return TT, TTC, BU

    def save_data(self):
        res = []
        for agent in self.agents:
            res.append(agent.log)
        with open(self.simulation_name + "_out.csv", "w") as f:
            wr = csv.writer(f)
            wr.writerows(res)

        ttc = 0
        res_lengths = []
        for r in res:
            res_lengths.append(len(r))
            ttc += len(r)

        bu = min(res_lengths) / max(res_lengths)

        with open(self.simulation_name + '_metrics.txt', 'w') as f:
            f.write('Total Time:\n')
            f.write(str(max(res_lengths)))
            f.write("\nTotal Travel Cost:\n")
            f.write(str(ttc))
            f.write("\nBalancing Utilization:\n")
            f.write(str(bu))

    def avoid_collision(self, collision):
        collision_type, time, agent, other_agent = collision
        agent1 = self.agents[agent]
        agent1.shift_route(time)
        if collision_type == 0:
            agent2 = self.agents[other_agent]
            agent1.swap_phase = [2, agent2.id]
            agent2.shift_route(time)
            agent2.swap_phase = [2, agent1.id]
