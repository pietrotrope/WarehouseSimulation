import queue


class TaskHandler:
    def __init__(self, env, task_pool):
        self.env = env
        self.task_pool = tasl_pool
        self.scheduling = None
        if self.env.scheduling is not None:
            self.scheduling = self.env.scheduling

    def get_task(self, robot_id):
        if self.scheduling is not None:
            selected_task = self.scheduling[robot_id].pop(0)
            return self.task_pool[selected_task]
        else:
            pass
        pass
