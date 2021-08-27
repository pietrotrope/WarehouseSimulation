import sys
from collections import defaultdict
import csv
import json
from itertools import count
from numpy import asarray
from simulation.agent.task_handler import TaskHandler
from simulation.tile import Tile


class Environment:

    def __init__(self, task_number=100, agent_number=8, scheduling="Random",
                 save=False, simulation_name="", routes=None, raster_map=None,
                 graph=None, raster_to_graph={}, graph_to_raster={}, agents_positions=[], task_handler=None,
                 seed=0):
        self.seed = seed
        self.simulation_name = simulation_name
        self.scheduling = scheduling
        self.agent_number = agent_number
        self.save = save
        self.raster_map = raster_map
        self.map_shape = self.raster_map.shape
        self.graph = graph
        self.timestamp = asarray([[defaultdict(list) for _ in row] for row in self.raster_map])

        # self.timestamp = np.asarray([[defaultdict(list)] * self.map_shape[1]] * self.map_shape[0])

        self.raster_to_graph = raster_to_graph if raster_to_graph is not None else {}
        self.graph_to_raster = graph_to_raster if graph_to_raster is not None else {}
        self.agents = [{
            "id": i,
            "position": agents_positions[i],
            "home": agents_positions[i],
            "route": [],
            "task": None,
            "log": [agents_positions[i]],
            "swap_phase": [0, i]
        } for i in range(self.agent_number)]
        self.moves = []
        self.time = 0
        self.task_ending_times = [sys.maxsize] * agent_number
        self.done = [False] * agent_number
        self.pods = [(i, j) for i, line in enumerate(self.raster_map) for j, cell in enumerate(line) if
                     cell == Tile.POD.value]

        self.task_handler = TaskHandler(self, task_number) if task_handler is None else task_handler

        if routes is None:
            with open('astar/astarRoutes.json', 'r') as f:
                self.routes = json.load(f)
        else:
            self.routes = routes

    def new_simulation(self, task_number=100, run=True, save=False, scheduling="Random", new_task_pool=False,
                       simulation_name=None):
        if simulation_name is not None:
            self.simulation_name = simulation_name
        self.time = 0
        self.scheduling = scheduling
        if new_task_pool:
            self.task_handler.new_task_pool(task_number)
        else:
            self.task_handler.same_task_pool(task_number)
        self.save = save
        for agent in self.agents:
            agent["position"] = agent["home"]
            agent["log"].clear()
            agent["log"].append(agent["position"])

        clear = dict.clear
        [clear(tsp) for ls in self.timestamp for tsp in ls]

        if run:
            return self.run()

    def make_step(self, task_ending_times, iterator):
        moves, agents_list = self.moves, self.agents
        i, i_plus_env_time = 0, self.time
        i_plus_time_plus_one, i_minus_one = i_plus_env_time + 1, i - 1
        clear, insert, append, timestamp = list.clear, list.insert, list.append, self.timestamp

        while i_plus_env_time < min(task_ending_times):
            clear(moves)
            collision = None
            for agent_id, agent in iterator:
                x, y = agent["route"][i]
                x_y_times =timestamp[x][y]
                agents, new_agents, route_i_minus_one, ver2 = x_y_times[i_plus_env_time], x_y_times[
                    i_plus_time_plus_one], agent["route"][i_minus_one], agent["swap_phase"][0] <= 0
                ver, ver3 = new_agents and new_agents[0] != agent_id, agents and agents[0] != agent_id and ver2

                if ver3:
                    other_agent = agents_list[agents[0]]
                    agent2_route_greater_i = len(other_agent["route"]) > i
                    if agent2_route_greater_i:
                        other_agent_route_i = other_agent["route"][i]
                        if i:
                            if other_agent_route_i == route_i_minus_one:
                                collision = 0, agent_id, agents[0]
                            else:
                                if ver or other_agent_route_i == other_agent["route"][i_minus_one] or \
                                    other_agent["swap_phase"][0]:
                                    collision = 1, agent_id, -1
                        else:
                            if other_agent_route_i == agent["position"]:
                                collision = 0, agent_id, agents[0]
                            else:
                                if ver or other_agent_route_i == other_agent["position"] or other_agent["swap_phase"][0]:
                                    collision = 1, agent_id, -1
                    else:
                        collision = 1, agent_id, -1
                else:
                    if ver:
                        if ver2:
                            collision = 1, agent_id, -1
                        else:
                            collision = 1, new_agents[0], -1

                if collision:
                    for ver, x1, y1, ag, otag in moves:
                        clear(timestamp[x1][y1][i_plus_time_plus_one])
                        if ver:
                            ag["swap_phase"][0] += 1
                            ag["swap_phase"][1] = otag

                    collision_type, agent, other_agent = collision
                    agent1 = agents_list[agent]
                    agent1["route"].insert(i, agent1["route"][i_minus_one]) if i else agent1[
                        "route"].insert(0, agent1["position"])
                    task_ending_times[agent] = self.time + len(agent1["route"])
                    if not collision_type:
                        agent2 = agents_list[other_agent]
                        agent1["swap_phase"] = [2, agent2["id"]]
                        insert(agent2["route"], i, agent2["route"][i_minus_one]) if i else insert(
                            agent2["route"], 0, agent2["position"])
                        agent2["swap_phase"] = [2, agent1["id"]]
                        task_ending_times[other_agent] = self.time + len(agent2["route"])                          

                    break
                else:
                    append(x_y_times[i_plus_time_plus_one], agent_id)
                    if agent["swap_phase"][0]:
                        agent["swap_phase"][0] -= 1
                        append(moves, (True, x, y, agent, agent["swap_phase"][1]))
                        if not agent["swap_phase"][0]:
                            agent["swap_phase"][1] = agent_id
                    else:
                        append(moves, (False, x, y, -1, -1))
            if not collision:
                i_minus_one = i
                i += 1
                i_plus_env_time = i + self.time
                i_plus_time_plus_one = i_plus_env_time + 1

    def run(self):
        agents = self.agents
        agent_number = self.agent_number
        graph_to_raster = self.graph_to_raster
        raster_to_graph = self.raster_to_graph
        task_ending_times = [sys.maxsize] * agent_number
        done = [False] * agent_number
        clear = list.clear
        insert = list.insert
        append = list.append
        extend = list.extend
        self.active_agents = {}
        active_agents = self.active_agents
        iterator = active_agents.items()
        for i in agents:
            active_agents[i["id"]] = i

        for _ in count(0):
            # Assign tasks
            curtime = self.time
            ver = False
            for agent in agents:
                if not agent["route"] and not done[agent["id"]]:
                    task = self.task_handler.get_task(agent["id"])
                    if task is None:
                        done[agent["id"]] = True
                        agent["position"] = agent["home"]
                        task_ending_times[agent["id"]] = sys.maxsize
                        agent["task"] = None
                        append(agent["log"], agent["position"])
                        del active_agents[agent["id"]]
                    else:
                        agent["task"] = task
                        id_robot = str(raster_to_graph[agent["position"]])
                        id_pod = str(raster_to_graph[task])
                        route_to_pod = self.routes[id_robot][id_pod]
                        if not route_to_pod:
                            route_to_pod = [raster_to_graph[agent["position"]]]
                        route = route_to_pod
                        route_to_ps = self.routes[id_pod].copy()
                        if route_to_pod[-1] != route_to_ps[0]:
                            start = graph_to_raster[route_to_ps[0]][0]
                            end = graph_to_raster[route_to_pod[-1]][0]
                            movement = tuple(map(lambda i, j: i - j, start, end))
                            if self.raster_map[
                                tuple(map(lambda i, j: i + j, end, (0, movement[1])))] == Tile.WALKABLE.value:
                                insert(route_to_ps, 0,
                                                   raster_to_graph[
                                                       tuple(map(lambda i, j: i + j, end, (0, movement[1])))])
                            else:
                                insert(route_to_ps,0,
                                                   raster_to_graph[
                                                       tuple(map(lambda i, j: i + j, end, (movement[0], 0)))])
                            insert(route_to_ps, 0, route_to_pod[-1])
                        route = [*route, *route_to_ps.copy()]
                        route_to_ps.reverse()
                        route = [*route, *route_to_ps]
                        clear(agent["route"])
                        extend(agent["route"], [graph_to_raster[cell][0] for cell in route])
                        ver = True

            if ver:
                for update_agent_id, update_agent in iterator:
                    if not done[update_agent["id"]]:
                        task_ending_times[update_agent_id] = curtime + len(update_agent["route"])
            else:
                if done.count(True) == len(done):
                    if self.save:
                        self.save_data()
                    res = [len(agent["log"]) for agent in agents]
                    TTC = sum(res)
                    BU, TT = min(res) / max(res), max(res)
                    return TT, TTC, BU

            self.make_step(task_ending_times, iterator)

            new_time = min(task_ending_times)
            delta = new_time - curtime
            for _ , agent in iterator:
                route = agent["route"]
                if len(route) >= delta:
                    agent["log"] = [*(agent["log"]), *(agent["route"][0:delta])]
                    agent["position"] = route[delta - 1]
                    del route[:delta]
            self.time = new_time

    def save_data(self):
        res = []
        for agent in self.agents:
            res.append(agent["log"])
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

    def get_task(self, agent):
        task = self.task_handler.get_task(agent["id"])
        if task is None:
            return True
        else:
            agent["task"] = task
            graph_to_raster = self.graph_to_raster
            raster_to_graph = self.raster_to_graph
            id_robot = str(raster_to_graph[agent["position"]])
            id_pod = str(raster_to_graph[task])
            route_to_pod = self.routes[id_robot][id_pod]
            if not route_to_pod:
                route_to_pod = [raster_to_graph[agent["position"]]]
            route = route_to_pod

            route_to_ps = self.routes[id_pod].copy()
            if route_to_pod[-1] != route_to_ps[0]:
                start = graph_to_raster[route_to_ps[0]][0]
                end = graph_to_raster[route_to_pod[-1]][0]
                movement = tuple(map(lambda i, j: i - j, start, end))
                if self.raster_map[tuple(map(lambda i, j: i + j, end, (0, movement[1])))] == Tile.WALKABLE.value:
                    route_to_ps.insert(0,
                                       raster_to_graph[tuple(map(lambda i, j: i + j, end, (0, movement[1])))])
                else:
                    route_to_ps.insert(0,
                                       raster_to_graph[tuple(map(lambda i, j: i + j, end, (movement[0], 0)))])
                route_to_ps.insert(0, route_to_pod[-1])
            route = [*route, *route_to_ps.copy()]
            route_to_ps.reverse()
            route = [*route, *route_to_ps]
            agent["route"] = [graph_to_raster[cell][0] for cell in route]
            return False
