import pandas as pd
import numpy as np
from simulation.graph.graph import Graph


class Environment:

    def __init__(self):
        raster_map = np.array(pd.read_csv('map.csv', header=None))
        map_shape = raster_map.shape
        picking_stations_columns = np.count_nonzero(raster_map == 4, axis=0)
        picking_stations_columns = " {} ".format(" ".join(map(str, picking_stations_columns)))
        picking_stations_columns = " {} ".format(" ".join(map(str, picking_stations_columns)))
        picking_stations_columns = [[int(y) for y in x.split()] for x in picking_stations_columns.split('0')]
        picking_stations_columns = [x for x in picking_stations_columns if x != []]
        picking_station_number = len(picking_stations_columns)

        graph_nodes = map_shape[0] * map_shape[1] - np.count_nonzero(raster_map == 4) + picking_station_number

        self.graph = Graph(graph_nodes)

        for i in range(map_shape[0]):
            for j in range(map_shape[1]):
                if raster_map[i][j] == 4 and (raster_map[i-1][j] == 4 or raster_map[i][j-1] == 4):
                    continue
                node = self.graph.get_node(i*map_shape[0]+j)
                node.change_type(raster_map[i][j])
                if raster_map[i][j] == 0 or raster_map[i][j] == 1:
                    if i == j == 0:
                        self.graph.add_edge(i*map_shape[0]+j, i*map_shape[0]+(j+1))
                    elif j == 0:
                        self.graph.add_edge(i * map_shape[0] + j, i * map_shape[0] + (j + 1))
                        self.graph.add_edge(i * map_shape[0] + j, (i+1) * map_shape[0] + j)
                        self.graph.add_edge(i * map_shape[0] + j, (i-1) * map_shape[0] + j)
                    elif i == 0:
                        self.graph.add_edge(i * map_shape[0] + j, i * map_shape[0] + (j + 1))
                        self.graph.add_edge(i * map_shape[0] + j, i * map_shape[0] + (j - 1))
                        self.graph.add_edge(i * map_shape[0] + j, (i + 1) * map_shape[0] + j)
                    else:
                        self.graph.add_edge(i * map_shape[0] + j, i * map_shape[0] + (j + 1))
                        self.graph.add_edge(i * map_shape[0] + j, i * map_shape[0] + (j - 1))
                        self.graph.add_edge(i * map_shape[0] + j, (i + 1) * map_shape[0] + j)
                        self.graph.add_edge(i * map_shape[0] + j, (i - 1) * map_shape[0] + j)
