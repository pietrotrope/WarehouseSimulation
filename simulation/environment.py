import socketserver

import pandas as pd
import numpy as np
from simulation.tile import Tile
from simulation.graph.graph import Graph
from simulation.communicationhandler import CommunicationHandler
import threading


class Environment:

    def __init__(self, map_path=None):
        self.raster_map = None
        self.map_shape = None
        self.graph = None
        self.raster_to_graph = {}
        self.__id = 0
        self.__load_map(map_path)
        self.__gen_graph()

        if self.graph is None or self.raster_map is None:
            raise Exception("Error while Initializing environment")

        server = socketserver.ThreadingTCPServer(('localhost', 50666), CommunicationHandler)
        server.raster_map = self.raster_map
        srv = threading.Thread(target=server.serve_forever, args=(), daemon=True)
        srv.start()
        print('Server listening at localhost:50666')

    def key_to_raster(self, key):
        return self.graph.get_node(key).coord

    def get_picking_stations_number(self):
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
        graph_nodes = self.map_shape[0] * \
                      self.map_shape[1] - \
                      (np.count_nonzero(self.raster_map == 4) -
                       self.get_picking_stations_number())
        self.graph = Graph(graph_nodes)

        picking_stations = [[], [], []]
        upper_station = [[], [], []]
        count = -1

        for i in range(self.map_shape[0]):
            picking_station_number = -1
            for j in range(self.map_shape[1]):
                if self.raster_map[i][j] == 4:
                    if self.raster_map[i - 1][j] == self.raster_map[i][j - 1] == 0:
                        picking_station_number = picking_station_number + 1
                        count += 1
                        upper_station[picking_station_number] = (i, j)
                        node = self.graph.get_node(count)
                        node.coord = [(i, j)]
                        node.type = Tile(self.raster_map[i][j])
                        picking_stations[picking_station_number].append((i, j))
                        self.raster_to_graph[(i, j)] = count
                    elif self.raster_map[i][j - 1] == 0:
                        picking_station_number += 1
                    self.raster_to_graph[(i, j)] = self.raster_to_graph[upper_station[picking_station_number]]
                    picking_stations[picking_station_number].append((i, j))
                else:
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
