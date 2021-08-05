import queue
import numpy as np
import random


class TaskHandler:
    def __init__(self, env, n):
        self.env = env
        self.n = n
        self.scheduling = None
        if self.env.scheduling is not None:
            self.scheduling = self.env.scheduling
        self.task_pool = [0] * self.n
        # set task_pool
        for i in range(1, self.n+1):
            indices = np.where(self.task_pool == 2)
            x_index = random.randint(0, len(indices[0]) - 1)
            y_index = random.randint(0, len(indices[1]) - 1)
            x_pos = indices[0][x_index]
            y_pos = indices[1][y_index]
            self.task_pool[i] = {i: (x_pos, y_pos)}

    def get_task(self, robot_id):
        if self.scheduling is not None:
            selected_task = self.scheduling[robot_id].pop(0)
            return self.task_pool[selected_task]
        else:
            pass
        pass
