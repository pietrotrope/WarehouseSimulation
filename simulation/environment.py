import json
import os
import socket

import yaml
import socketserver

import pandas as pd
import numpy as np

from simulation.agent.agent import Agent
from simulation.communication.agent_handler import AgentHandler
from simulation.tile import Tile
from simulation.graph.graph import Graph
from simulation.communication.enviroment_server import EnvironmentToScreenServer
import multiprocessing as mp
import threading


class Environment:

    def __init__(self, map_path=None, cfg_path='../config.yaml'):
        self.raster_map = None
        self.map_shape = ()
        self.graph = None
        self.agents = {}
        self.raster_to_graph = {}
        self.__id = 0
        self.__load_map(map_path)
        self.__gen_graph()
        self.__spawn_agents(cfg_path)

        if self.graph is None or self.raster_map is None:
            raise Exception("Error while Initializing environment")

        try:
            server = socketserver.ThreadingTCPServer(('0.0.0.0', 50666), EnvironmentToScreenServer)
            server.raster_map = self.raster_map

            self.srv = threading.Thread(target=server.serve_forever, args=(), daemon=True)
            self.srv.start()

            agent_server = socketserver.ThreadingUnixStreamServer('/tmp/environment', AgentHandler)
            agent_server.env = self

            self.agent_handler = threading.Thread(target=agent_server.serve_forever, args=(), daemon=True)
            self.agent_handler.start()
        except OSError:
            self.shutdown()
            for agent in self.agents.keys():
                os.remove('/tmp/agents/{}'.format(agent))

    def key_to_raster(self, key):
        return self.graph.get_node(key).coord

    def __get_picking_stations_number(self):
        picking_stations_columns = np.count_nonzero(self.raster_map == 4, axis=0)
        picking_stations_columns = " {} ".format(" ".join(map(str, picking_stations_columns)))
        picking_stations_columns = " {} ".format(" ".join(map(str, picking_stations_columns)))
        picking_stations_columns = [[int(y) for y in x.split()] for x in picking_stations_columns.split('0')]
        picking_stations_columns = [x for x in picking_stations_columns if x != []]
        return len(picking_stations_columns)

    def update_map(self, coord=None, key=None, tile=Tile.WALKABLE):
        if coord is not None:
            node = self.graph.get_node(self.raster_to_graph[coord])
            node.type = tile
            self.raster_map[coord[0]][coord[1]] = tile.value
        if key is not None:
            node = self.graph.get_node(key)
            node.type = tile
            x, y = self.key_to_raster(key)
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

        picking_stations = [[] for i in range(picking_station_number)]
        upper_station = [[] for i in range(picking_station_number)]
        count = -1
        agent_count = 0

        for i in range(self.map_shape[0]):
            current_picking_station = -1
            for j in range(self.map_shape[1]):
                if self.raster_map[i][j] == 4:
                    if self.raster_map[i - 1][j] == self.raster_map[i][j - 1] == 0:
                        current_picking_station = current_picking_station + 1
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
        positions = self.agents
        print(positions)
        self.agents = {}

        for i in range(len(positions)):
            agent = Agent(i, positions[i])

            self.agents[i] = {'Agent': agent,
                              'Position': agent.position}
            agent.start()

    def shutdown(self):
        if os.path.exists('/tmp/environment'):
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.connect('/tmp/environment')
                msg = json.dumps({'req': 'shutdown'})
                sock.sendall(bytes(msg + '\n', 'utf-8'))
                sock.close()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(('localhost', 50666))
            sock.sendall(b'shutdown')
            sock.close()

        for agent in self.agents.keys():
            if os.path.exists('/tmp/agents/{}'.format(agent)):
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                    sock.connect('/tmp/agents/{}'.format(agent))
                    msg = json.dumps({'req': 'shutdown'})
                    sock.sendall(bytes(msg + '\n', 'utf-8'))
                    sock.close()
            self.agents[agent]['Agent'].terminate()
