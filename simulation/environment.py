import sys
from collections import defaultdict
import csv
import json

from itertools import count
from simulation.agent.agent import Agent
from simulation.agent.task_handler import TaskHandler
from simulation.tile import Tile


class Environment:

    def __init__(self, task_number=100, agent_number=8, scheduling="Random",
                 save=False, simulation_name="", routes = None, raster_map = None,
                 graph = None, raster_to_graph = {}, graph_to_raster = {}, agents_positions = [], task_hanlder = None):
        self.simulation_name = simulation_name
        self.scheduling = scheduling
        self.agent_number = agent_number
        self.save = save
        self.raster_map = raster_map
        self.map_shape = self.raster_map.shape
        self.graph = graph
        self.timestamp = [[defaultdict(list) for _ in row] for row in self.raster_map]
        self.raster_to_graph = raster_to_graph
        self.graph_to_raster = graph_to_raster
        self.agents = []
        self.moves = []    
        self.time = 0
        self.task_ending_times = [sys.maxsize]*agent_number
        self.done = [False]*agent_number    
        self.pods = []

        for i, line in enumerate(self.raster_map):
            for j, cell in enumerate(line):
                if cell == Tile.POD.value:
                    self.pods.append((i, j))

        if task_hanlder is None:
            self.task_handler = TaskHandler(self, task_number)
        else:
            self.task_handler = task_hanlder
        
        for i in range(self.agent_number):
            agent = Agent(i, agents_positions[i], self, task_handler=self.task_handler)
            self.agents.append(agent)

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
            agent.position = agent.home
            agent.time = 0
            agent.log.clear()
            agent.log.append(agent.position)
        

        for x in range(self.map_shape[0]):
            for y in range(self.map_shape[1]):
                self.timestamp[x][y].clear()

        if run:
            return self.run()

    def make_step(self, to_time, pos=0):
        moves = self.moves
        for i in range(pos, to_time):
            moves.clear()
            for agent in self.agents:
                if agent.task:
                    agent_id = agent.id
                    collision = agent.detect_collision(i)
                    if collision:
                        for ver, x1, y1, t, ag, otag in moves:
                            self.timestamp[x1][y1][t].clear()
                            if ver:
                                ag.swap_phase[0] += 1
                                ag.swap_phase[1] = otag
                        return collision
                    else:
                        x, y = agent.route[i]
                        i_plus_time_plus_one = i + self.time + 1
                        self.timestamp[x][y][i_plus_time_plus_one].append(agent_id)

                        if agent.swap_phase[0]:
                            agent.swap_phase[0] -= 1
                            moves.append((True, x, y, i_plus_time_plus_one, agent, agent.swap_phase[1]))
                            if not agent.swap_phase[0]:
                                agent.swap_phase[1] = agent_id
                        else:
                            moves.append((False, x, y, i_plus_time_plus_one,-1, -1))

        return None

    def run(self):
        task_ending_times = self.task_ending_times
        done = self.done
        agents = self.agents
        for i in range(self.agent_number):
            task_ending_times[i] = sys.maxsize
            done[i] = False

        for _ in count(0):
            # Assign tasks
            ver = False
            for agent in agents:
                if not agent.route:
                    done[agent.id] = agent.get_task()
                    if done[agent.id]:
                        agent.position = agent.home
                        task_ending_times[agent.id] = sys.maxsize
                        agent.task = None
                    else:
                        ver = True

            if done.count(True) == len(done):
                if self.save:
                    self.save_data()  
                res = [len(agent.log) for agent in agents]
                TTC = sum(res)
                BU, TT = min(res) / max(res), max(res)
                return TT, TTC, BU

            if ver:
                for update_agent in agents:
                    if not done[update_agent.id]:
                        task_ending_times[update_agent.id] = self.time + len(update_agent.route)

            collision = self.make_step(min(task_ending_times) - self.time)
            while collision:
                
                collision_type, time, agent, other_agent = collision
                agent1 = agents[agent]
                agent1.shift_route(time)
                if not collision_type:
                    agent2 = agents[other_agent]
                    agent1.swap_phase = [2, agent2.id]
                    agent2.shift_route(time)
                    agent2.swap_phase = [2, agent1.id]
                    
                if collision[3] != -1:
                    task_ending_times[collision[3]] = self.time + len(agents[collision[3]].route)
                task_ending_times[collision[2]] = self.time + len(agents[collision[2]].route)
                collision = self.make_step(min(task_ending_times) - self.time, collision[1])

            new_time = min(task_ending_times)
            delta = new_time - self.time
            for agent in agents:
                agent.skip_to(delta)
            self.time = new_time


    def save_data(self):
        res = []
        for agent in self.agents:
            res.append(agent.log)
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

