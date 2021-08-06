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
            self.task_pool[i+1] = self.new_task(self.pods)

    @staticmethod
    def new_task(pods):
        random_index = randrange(len(pods))
        task = pods[random_index]
        return task

    def gen_schedule(self):
        self.scheduling = [[]]*len(self.env.agents)
        for i in range(len(self.env.agents)):
            for j in range(10):
                self.scheduling[i].append(self.new_task(self.pods))

    def get_task(self, robot_id):
        if self.scheduling is not None:
            if not self.scheduling[robot_id]:
                return None
            else:
                selected_task = self.scheduling[robot_id].pop(0)
            return self.task_pool[selected_task]
            
        else:
            if not self.scheduling[robot_id]:
                return None
            else:
                selected_task = self.scheduling[robot_id].pop(0)
            return self.task_pool[selected_task]
        pass
