import pandas as pd
import numpy as np
from simulation.tile import Tile
from simulation.graph.graph import Graph


class Environment:

    def __init__(self):
        self.raster_map = None
        self.map_shape = None
        self.graph = None
        self.__load_map()
        self.__gen_graph()

        if self.graph is None or self.raster_map is None:
            raise Exception("Error while Initializing environment")

    def __add_edge(self, src, dest):
        self.graph.add_edge(self.raster_to_key(src), self.raster_to_key(dest))

    def raster_to_key(self, coord):
        return coord[0] * self.map_shape[0] + coord[1]

    def get_picking_stations_number(self):
        picking_stations_columns = np.count_nonzero(self.raster_map == 4, axis=0)
        picking_stations_columns = " {} ".format(" ".join(map(str, picking_stations_columns)))
        picking_stations_columns = " {} ".format(" ".join(map(str, picking_stations_columns)))
        picking_stations_columns = [[int(y) for y in x.split()] for x in picking_stations_columns.split('0')]
        picking_stations_columns = [x for x in picking_stations_columns if x != []]
        return len(picking_stations_columns)

    def __load_map(self):
        self.raster_map = np.array(pd.read_csv('map.csv', header=None))
        self.map_shape = self.raster_map.shape

    def __gen_graph(self):
        graph_nodes = self.map_shape[0] *\
                      self.map_shape[1] -\
                      np.count_nonzero(self.raster_map == 4) +\
                      self.get_picking_stations_number()
        self.graph = Graph(graph_nodes)

        i = j = 0
        picking_station = (0, 0)

        for true_i in range(self.map_shape[0]):
            for true_j in range(self.map_shape[1]):
                if self.raster_map[true_i][true_j] == 4:
                    if self.raster_map[true_i - 1][true_j] == self.raster_map[true_i][true_j - 1] == 0:
                        picking_station = (true_i, true_j)
                        node = self.graph.get_node(self.raster_to_key(picking_station))
                        node.change_type(Tile(self.raster_map[true_i][true_j]))
                        self.__add_edge((true_i, true_j), (true_i, true_j - 1))
                        j += 1
                    if self.raster_map[true_i - 1][true_j] == 4:
                        if self.raster_map[true_i][true_j - 1] == 0:
                            self.__add_edge(picking_station, (true_i, j - 1))
                        if self.raster_map[true_i][true_j + 1] == 0:
                            self.__add_edge(picking_station, (true_i, j + 1))
                        self.__add_edge(picking_station, (true_i + 1, j))
                    elif self.raster_map[true_i][true_j - 1] == 4:
                        self.__add_edge(picking_station, (picking_station[0] - 1, j))
                        if self.raster_map[true_i][true_j + 1] == 0:
                            self.__add_edge(picking_station, (picking_station[0], j))
                    continue

                node = self.graph.get_node(self.raster_to_key((i, j)))
                node.change_type(Tile(self.raster_map[i][j]))
                if self.raster_map[i][j] == 0 or self.raster_map[i][j] == 1:
                    self.__add_edge((i, j), (i, j + 1))
                    self.__add_edge((i, j), (i + 1, j))
                    if j != 0:
                        self.__add_edge((i, j), (i, j - 1))
                    if i != 0:
                        self.__add_edge((i, j), (i - 1, j))
            j += 1
        i += 1
