import pandas as pd
import numpy as np
from simulation.tile import Tile
from simulation.graph.graph import Graph


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

        picking_station = (0, 0)

        count = -1

        for i in range(self.map_shape[0]):
            for j in range(self.map_shape[1]):
                if self.raster_map[i][j] == 4:
                    if self.raster_map[i - 1][j] == self.raster_map[i][j - 1] == 0:
                        count += 1
                        node = self.graph.get_node(count)
                        node.coord = (i, j)
                        node.type = Tile(self.raster_map[i][j])
                    self.raster_to_graph[(i, j)] = count
                else:
                    count += 1
                    node = self.graph.get_node(count)
                    node.coord = (i, j)
                    node.type = Tile(self.raster_map[i][j])
                    self.raster_to_graph[(i, j)] = count
                node = self.raster_to_graph[(i, j)]
                if j != 0:
                    self.graph.add_edge(node, self.raster_to_graph[(i, j - 1)])
                if i != 0:
                    self.graph.add_edge(node, self.raster_to_graph[(i - 1, j)])



        '''
        i = j = 0
        picking_station = (0, 0)

        for true_i in range(self.map_shape[0]):
            for true_j, node in range(self.map_shape[1]), self.graph.nodes:
                if self.raster_map[true_i][true_j] == 4:
                    # Found a picking station
                    if self.raster_map[true_i - 1][true_j] == self.raster_map[true_i][true_j - 1] == 0:
                        count += 1
                        # If this is the first block of the picking station
                        picking_station = (i, j)
                        node = self.graph.get_node(self.raster_to_key(picking_station))
                        node.change_type(Tile(self.raster_map[true_i][true_j]))
                        self.__add_edge(picking_station, (i, j - 1))

                        picking_station_blocks = [picking_station]

                        tmp_i = true_i
                        tmp_j = true_j + 1

                        self.raster_map[true_i][true_j] = -1

                        while self.raster_map[tmp_i][tmp_j] == 4:
                            while self.raster_map[tmp_i][tmp_j] == 4:
                                self.__add_edge(picking_station, (picking_station[0] - 1, j))
                                if self.raster_map[tmp_i][tmp_j + 1] == 0:
                                    self.__add_edge(picking_station, (picking_station[0], j))
                                if self.raster_map[tmp_i - 1][tmp_j] == -1:
                                    self.__add_edge(picking_station, (picking_station[0] + 1, j))
                                    if self.raster_map[tmp_i][tmp_j + 1] == 0:
                                        self.__add_edge(picking_station, (picking_station[0], j))
                                self.raster_map[tmp_i][tmp_j] = -1
                                picking_station_blocks.append((tmp_i, tmp_j))
                                tmp_j += 1
                            tmp_i += 1
                            tmp_j = true_j

                        self.graph_to_raster[self.raster_to_key((i, j))] = picking_station_blocks
                        j = (j + 1) % self.map_shape[1]
                elif self.raster_map[true_i][true_j] == -1:
                    pass
                else:
                    count += 1
                    print('{}: {}, {}, {}'.format(self.raster_to_key((i, j)),
                                                  [(i, j)],
                                                  [(true_i, true_j)],
                                                  Tile(self.raster_map[true_i][true_j])))
                    self.graph_to_raster[self.raster_to_key((i, j))] = [(true_i, true_j)]
                    node = self.graph.get_node(self.raster_to_key((i, j)))
                    node.change_type(Tile(self.raster_map[true_i][true_j]))
                    if self.raster_map[i][j] == 0 or self.raster_map[i][j] == 1:
                        self.__add_edge((i, j), (i, j + 1))
                        self.__add_edge((i, j), (i + 1, j))
                        if j != 0:
                            self.__add_edge((i, j), (i, j - 1))
                        if i != 0:
                            self.__add_edge((i, j), (i - 1, j))

                    j = (j + 1) % self.map_shape[1]
            if j == 0:
                i += 1
        self.raster_map[self.raster_map == -1] = 4'''
