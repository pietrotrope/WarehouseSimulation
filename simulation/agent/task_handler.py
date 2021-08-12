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
            self.task_pool[i+1] = random.choice(self.pods)
        
    
    def new_task_pool(self,n):
        self.n = n
        self.scheduling = None
        if self.env.scheduling is not None:
            self.scheduling = self.env.scheduling
        self.task_pool = {}
        for i in range(n):
            self.task_pool[i+1] = random.choice(self.pods)

    def get_task(self, robot_id):
        if self.scheduling is not None:
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
