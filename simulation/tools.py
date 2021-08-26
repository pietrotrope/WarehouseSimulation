import numpy as np
from pandas import read_csv
from simulation.graph.graph import Graph
from simulation.tile import Tile


def get_raster_map(map_path):
        map_path = 'map.csv' if map_path is None else map_path
        return np.array(read_csv(map_path, header=None))

def gen_graph_to_raster(graph):
    graph_to_raster = {}
    for node in graph.nodes:
        graph_to_raster[node.id] = graph.nodes[node.id].coord
    return graph_to_raster


def gen_graph(raster_map):
    map_shape = raster_map.shape
    picking_stations_columns = np.count_nonzero(
            raster_map == 4, axis=0)
    picking_stations_columns = " {} ".format(
            " ".join(map(str, picking_stations_columns)))
    picking_stations_columns = [
            [int(y) for y in x.split()] for x in picking_stations_columns.split('0')]
    picking_stations_columns = [
            x for x in picking_stations_columns if x != []]
    
    picking_station_number = len(picking_stations_columns)

    graph_nodes = map_shape[0] * map_shape[1] - \
                    (np.count_nonzero(raster_map == 4) - picking_station_number)
    graph = Graph(graph_nodes)
    raster_to_graph = {}
    agents_positions = []

    picking_stations = [[] for _ in range(picking_station_number)]
    upper_station = [(0, 0) for _ in range(picking_station_number)]
    count = -1

    for i in range(map_shape[0]):
        current_picking_station = -1
        for j in range(map_shape[1]):
            if raster_map[i][j] == 4:
                if raster_map[i - 1][j] == raster_map[i][j - 1] == 0:
                    current_picking_station += 1
                    count += 1
                    upper_station[current_picking_station] = (i, j)
                    node = graph.get_node(count)
                    node.coord = [(i, j)]
                    node.type = Tile(raster_map[i][j])
                    picking_stations[current_picking_station].append(
                        (i, j))
                    raster_to_graph[(i, j)] = count
                elif raster_map[i][j - 1] == 0:
                    current_picking_station += 1
                raster_to_graph[(
                    i, j)] = raster_to_graph[upper_station[current_picking_station]]
                picking_stations[current_picking_station].append((i, j))
            else:
                if raster_map[i][j] == 1:
                    agents_positions.append((i,j))
                count += 1
                node = graph.get_node(count)
                node.coord = [(i, j)]
                node.type = Tile(raster_map[i][j])
                raster_to_graph[(i, j)] = count

            node = raster_to_graph[(i, j)]
            if j:
                graph.add_edge(node, raster_to_graph[(i, j - 1)])
            if i:
                graph.add_edge(node, raster_to_graph[(i - 1, j)])

    for picking_station in picking_stations:
        node = graph.get_node(
            raster_to_graph[picking_station[0]])
        node.coord = picking_station
    
    return graph, raster_to_graph, agents_positions


    
