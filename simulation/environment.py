import pandas as pd
import numpy as np

from simulation.agent.agent import Agent
from simulation.agent.task_handler import TaskHandler
from simulation.cell import Cell
from simulation.tile import Tile
from simulation.graph.graph import Graph
from multiprocessing import set_start_method

set_start_method("fork")


class Environment:

    def __init__(self, map_path=None, cfg_path='../config.yaml', task_number=50, agent_number=8, scheduling=None, save=False):
        self.scheduling = [] if scheduling is None else scheduling
        self.raster_map = None
        self.tile_map = None
        self.map_shape = ()
        self.graph = None
        self.agents = {}
        self.raster_to_graph = {}
        self.__id = 0
        self.__load_map(map_path)
        self.__gen_graph()
        self.__spawn_agents(cfg_path)
        self.time = 0
        self.task_pool = {}
        self.task_number = task_number
        self.agent_number = agent_number
        self.save = save

        if self.graph is None or self.raster_map is None:
            raise Exception("Error while Initializing environment")

        self.task_handler = self.task_handler(self, task_number)

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
        pods = []
        for i, line in enumerate(self.raster_map):
            for j, cell in enumerate(line):
                if cell == Tile.POD.value:
                    pods.append((i, j))
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
            node = self.graph.get_node(
                self.raster_to_graph[picking_station[0]])
            node.coord = picking_station

    def __gen_tile_map(self):
        self.tile_map = np.zeros_like(self.raster_map)
        for i, row in enumerate(self.raster_map):
            for j, cell in enumerate(row):
                self.tile_map[i][j] = Cell(Tile(cell))

    def __spawn_agents(self, cfg_path):
        positions = self.agents
        self.agents = []

        for i in range(len(positions)):
            agent = Agent(i, positions[i], self)

            self.agents.append(agent)

    def run(self):
        conflicts = []
        task_ends = []
        done = [False for _ in range(len(self.agents))]
        while True:
            for i, agent in enumerate(self.agents):
                if not agent.route:
                    done[i] = agent.get_task()
                    conflicts = conflicts + agent.declare_route()
                task_ends.append(self.time + len(agent.route))

            if min(conflicts)[0] > min(task_ends):
                self.time = min(task_ends)
                task_ends.remove(self.time)
                for agent in self.agents:
                    agent.skip_to(self.time)
                continue

            if conflicts:
                conflict_time = min(conflicts)[0]

                self.time = conflict_time - 1
                for agent in self.agents:
                    agent.skip_to(self.time)

                while conflict_time in list(map(lambda x: x[0], conflicts)):
                    first_conflict = min(conflicts)
                    if first_conflict[0] == conflict_time:
                        conflicts = conflicts + \
                            self.solve_conflict(first_conflict)
                        conflicts.remove(first_conflict)
                continue

            if done.count(True) == len(done):
                if self.save:
                    self.save_data()
                break
            pass

    def save_data(self):

        pass

    def solve_conflict(self, conflict):
        time, pos = conflict
        agents = self.tile_map[pos].timestamp[time]

        new_agents=[]
        for agent in agents:
            going_to= self.tile_map[agent.route[time-self.time+1]]
            for other_agent in going_to[time-self.time]:
                if other_agent.route[time-self.time+1] == pos:
                    new_agents.append(other_agent)

        #TODO Risolvi i conflitti dei new_agents (agenti che hanno il secondo tipo di conflitto spostandosi nella cella segnata dal conflitto)

        priorities = []
        for agent in agents:
            priorities.append((self.agents[agent].get_priority(), agent))

        new_conflicts = []

        if len(priorities) == 2:
            priority_agent = max(priorities)[1]
            for agent in agents:
                if agent is not priority_agent:
                    overlap_path_agents = self.tile_map[self.agents[agent].route[0]
                                                        ].timestamp[time + 1]

                    new_conflicts = new_conflicts + self.agents[agent].shift_route(
                        2, overlap_path_agents.contains(priority_agent))

        elif len(priorities) > 2:
            priorities.sort(reverse=True)
            for i, agent in enumerate(priorities):
                overlap_path_agents = self.tile_map[self.agents[agent].route[0]
                                                    ].timestamp[time + 1]
                new_conflicts = new_conflicts + self.agents[agent].shift_route(
                    i+1, bool(set(agents).intersection(set(overlap_path_agents))))

        return new_conflicts
