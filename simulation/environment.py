import json
import os
import socket

import yaml
import socketserver

import pandas as pd
import numpy as np
import threading

from simulation.agent.agent import Agent
from simulation.tile import Tile
from simulation.graph.graph import Graph
from multiprocessing import set_start_method
from threading import Lock
set_start_method("fork")


class Environment:

    def __init__(self, map_path=None, cfg_path='../config.yaml'):
        self.raster_map = None
        self.map_shape = ()
        self.graph = None
        self.agents = {}
        self.raster_to_graph = {}
        self.lock = Lock()
        self.__id = 0
        self.__load_map(map_path)
        self.__gen_graph()
        self.__spawn_agents(cfg_path)

        if self.graph is None or self.raster_map is None:
            raise Exception("Error while Initializing environment")

    def key_to_raster(self, key):
        return self.graph.get_node(key).coord

    def __get_picking_stations_number(self):
        picking_stations_columns = np.count_nonzero(self.raster_map == 4, axis=0)
        picking_stations_columns = " {} ".format(" ".join(map(str, picking_stations_columns)))
        picking_stations_columns = [[int(y) for y in x.split()] for x in picking_stations_columns.split('0')]
        picking_stations_columns = [x for x in picking_stations_columns if x != []]
        return len(picking_stations_columns)

    def update_map(self, coord=None, key=None, tile=Tile.WALKABLE):
        with self.lock:
            if coord is not None:
                node = self.graph.get_node(self.raster_to_graph[coord])
                node.type = tile
                self.raster_map[coord[0]][coord[1]] = tile.value
            if key is not None:
                node = self.graph.get_node(key)
                node.type = tile
                x, y = self.key_to_raster(key)[0]
                self.raster_map[x][y] = tile.value

    def __load_map(self, map_path):
        map_path = 'map.csv' if map_path is None else map_path
        self.raster_map = np.array(pd.read_csv(map_path, header=None))
        self.map_shape = self.raster_map.shape

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
                        picking_stations[current_picking_station].append((i, j))
                        self.raster_to_graph[(i, j)] = count
                    elif self.raster_map[i][j - 1] == 0:
                        current_picking_station += 1
                    self.raster_to_graph[(i, j)] = self.raster_to_graph[upper_station[current_picking_station]]
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

    def __spawn_agents(self, cfg_path):
        # TODO: Implement agent spawn
        pass
