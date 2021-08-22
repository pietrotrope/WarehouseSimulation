from os import posix_fadvise
import sys
import queue
import numpy as np
import random
import copy
from random import randrange


class TaskHandler:
    def __init__(self, env, n):
        self.env = env
        self.n = n
        self.scheduling = None
        self.assigned_tasks = [-1 for _ in range(self.env.agent_number)]
        self.picking_times = {}
        if self.env.scheduling is not None:
            self.scheduling = self.env.scheduling
        self.pods = env.get_pods()
        self.task_pool = {}
        self.initial_task_pool = {}
        for i in range(n):
            self.task_pool[i + 1] = random.choice(self.pods)

    def new_task_pool(self, n):
        self.n = n
        self.scheduling = None
        self.assigned_tasks = [-1 for _ in range(self.env.agent_number)]
        self.picking_times = {}
        if self.env.scheduling is not None:
            self.scheduling = self.env.scheduling
        self.task_pool = {}
        for i in range(n):
            self.task_pool[i + 1] = random.choice(self.pods)
        self.initial_task_pool = copy.copy(self.task_pool)

    def get_task(self, robot_id):
        if self.scheduling is not None:
            if self.scheduling == "Greedy0":
                return self._greedy_approach_0(robot_id)
            elif self.scheduling == "Greedy1":
                return self._greedy_approach_1(robot_id)
            else:
                if self.scheduling[robot_id] == []:
                    return None
                else:
                    selected_task = self.scheduling[robot_id].pop(0)
                    return self.task_pool[selected_task]

        else:
            if self.task_pool:
                task_id = list(self.task_pool)[0]
                task = self.task_pool[task_id]
                del self.task_pool[task_id]
                return task
            else:
                return None

    def _greedy_approach_0(self, robot_id):
        if self.task_pool:
            indexes = list(self.task_pool.keys())
            new_task = [indexes[0], -1]
            id_robot = str(self.env.raster_to_graph[self.env.agents[robot_id].position])
            id_pod = str(self.env.raster_to_graph[self.task_pool[indexes[0]]])
            new_task[1] = len(self.env.routes[id_robot][id_pod])

            for possible_task in indexes:
                id_pod = str(
                    self.env.raster_to_graph[self.task_pool[possible_task]])
                task_len = len(self.env.routes[id_robot][id_pod])
                if task_len < new_task[1]:
                    new_task[0] = possible_task
                    new_task[1] = task_len
            
            selected_task = self.task_pool[new_task[0]]
            del self.task_pool[new_task[0]]
            return selected_task
        else:
            return None
    
    def _greedy_approach_1(self, robot_id):
        if self.assigned_tasks[robot_id] != -1:
            del self.picking_times[self.assigned_tasks[robot_id]]
            del self.task_pool[self.assigned_tasks[robot_id]]   
            self.assigned_tasks[robot_id] = -1
        if self.task_pool:
            indexes = list(self.task_pool.keys())
            new_task = [-1, sys.maxsize]
            id_robot = str(self.env.raster_to_graph[self.env.agents[robot_id].position])

            other_robot_id = -1
            ver = False
            for possible_task in indexes:
                id_pod = str(
                    self.env.raster_to_graph[self.task_pool[possible_task]])
                task_len = len(self.env.routes[id_robot][id_pod])

                if possible_task in self.picking_times and (self.picking_times[possible_task][1] == robot_id or self.picking_times[possible_task][0] - self.env.time <= task_len or self.picking_times[possible_task][0] - self.env.time <= 0):
                    continue

                if task_len < new_task[1]:
                    new_task[0] = possible_task
                    new_task[1] = task_len

                    if possible_task in self.picking_times:
                        other_robot_id = self.picking_times[possible_task][1]
                        ver = True
                    else:
                        ver = False
            if new_task[0] != -1:

                if new_task[0] in self.picking_times:
                    self.picking_times[new_task[0]][0] = new_task[1] + self.env.time
                    self.picking_times[new_task[0]][1] = robot_id                        
                else:
                    self.picking_times[new_task[0]] = [new_task[1] + self.env.time, robot_id]
                self.assigned_tasks[robot_id] = new_task[0]

                if ver and other_robot_id != -1:
                    self.env.agents[other_robot_id].task = None
                    self.assigned_tasks[other_robot_id] = -1
                    self.env.agents[other_robot_id].get_task()
                    
                selected_task = self.task_pool[new_task[0]]
                return selected_task
        return None

