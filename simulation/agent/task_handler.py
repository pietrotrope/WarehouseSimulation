import queue
import numpy as np
import random
from random import randrange


class TaskHandler:
    def __init__(self, env, n):
        self.env = env
        self.n = n
        self.scheduling = None
        if self.env.scheduling is not None:
            self.scheduling = self.env.scheduling
        self.pods = env.get_pods()
        self.task_pool = {}
        for i in range(n):
            self.task_pool[i + 1] = random.choice(self.pods)

    def new_task_pool(self, n):
        self.n = n
        self.scheduling = None
        if self.env.scheduling is not None:
            self.scheduling = self.env.scheduling
        self.task_pool = {}
        for i in range(n):
            self.task_pool[i + 1] = random.choice(self.pods)

    def get_task(self, robot_id):
        if self.scheduling is not None:
            if self.scheduling == "Greedy0":
                return self._greedy_approach_0(robot_id)
            else:
                if not self.scheduling[robot_id]:
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

