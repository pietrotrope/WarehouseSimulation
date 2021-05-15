import pandas as pd
import numpy as np
from simulation.graph.graph import Graph


class Environment:

    def __init__(self):
        raster_map = np.array(pd.read_csv('map.csv', header=None))
        self.map_shape = raster_map.shape
        picking_stations_columns = np.count_nonzero(raster_map == 4, axis=0)
        picking_stations_columns = " {} ".format(" ".join(map(str, picking_stations_columns)))
        picking_stations_columns = " {} ".format(" ".join(map(str, picking_stations_columns)))
        picking_stations_columns = [[int(y) for y in x.split()] for x in picking_stations_columns.split('0')]
        picking_stations_columns = [x for x in picking_stations_columns if x != []]
        picking_station_number = len(picking_stations_columns)

        graph_nodes = self.map_shape[0] * self.map_shape[1] - np.count_nonzero(raster_map == 4) + picking_station_number

        self.graph = Graph(graph_nodes)

        i = j = 0
        picking_station = (0, 0)

        for true_i in range(self.map_shape[0]):
            for true_j in range(self.map_shape[1]):
                if raster_map[true_i][true_j] == 4:
                    if raster_map[true_i-1][true_j] == raster_map[true_i][true_j-1] == 0:
                        picking_station = (true_i, true_j)
                        self.add_edge((true_i, true_j), (true_i, true_j - 1))
                        j += 1
                    if raster_map[true_i-1][true_j] == 4:
                        if raster_map[true_i][true_j - 1] == 0:
                            self.add_edge(picking_station, (true_i, j - 1))
                        if raster_map[true_i][true_j + 1] == 0:
                            self.add_edge(picking_station, (true_i, j + 1))
                        self.add_edge(picking_station, (true_i + 1, j))
                    elif raster_map[true_i][true_j-1] == 4:
                        self.add_edge(picking_station, (picking_station[0] - 1, j))
                        if raster_map[true_i][true_j+1] == 0:
                            self.add_edge(picking_station, (picking_station[0], j))
                    continue

                node = self.graph.get_node(i*self.map_shape[0]+j)
                node.change_type(raster_map[i][j])
                if raster_map[i][j] == 0 or raster_map[i][j] == 1:
                    if i == j == 0:
                        self.add_edge((i, j), (i, j+1))
                    elif j == 0:
                        self.add_edge((i, j), (i, j+1))
                        self.add_edge((i, j), (i+1, j))
                        self.add_edge((i, j), (i-1, j))
                    elif i == 0:
                        self.add_edge((i, j), (i, j+1))
                        self.add_edge((i, j), (i, j-1))
                        self.add_edge((i, j), (i+1, j))
                    else:
                        self.add_edge((i, j), (i, j+1))
                        self.add_edge((i, j), (i, j-1))
                        self.add_edge((i, j), (i-1, j))
                        self.add_edge((i, j), (i+1, j))
            j += 1
        i += 1

    def add_edge(self, src, dest):
        self.graph.add_edge(self.raster_to_key(src), self.raster_to_key(dest))

    def raster_to_key(self, coord):
        return coord[0] * self.map_shape[0] + coord[1]