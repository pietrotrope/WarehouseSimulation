import multiprocessing
import queue
from .direction import Direction

movement = {
    Direction.UP: (0, 1),
    Direction.DOWN: (0, -1),
    Direction.LEFT: (-1, 0),
    Direction.RIGHT: (1, 0)
}


class Agent:

    def __init__(self, agent_id, position, route, env, direction=Direction.DOWN, task_handler=None):
        self.id = agent_id
        self.position = position
        self.direction = direction
        self.route = route
        self.env = env
        self.task_handler = task_handler
        self.task = None

    def get_task(self):
        self.task = self.task_handler.get_task(self.id)

    def get_priority(self, pos):
        # TODO: return number of remaining steps from current position to destination
        pass

    def declare_route(self):
        conflict = None
        for i in range(len(self.route)):
            x, y = self.route[i]
            if self.env.raster_map[x][y].timestamp[i + self.env.time]:
                self.env.raster_map[x][y].timestamp[i + self.env.time].append(self.id)
            else:
                self.env.raster_map[x][y].timestamp[i + self.env.time] = [self.id]

            if len(self.env.raster_map[x][y].timestamp[i + self.env.time]) > 1 and conflict is None:
                conflict = (i + self.env.time, (x, y))

        return conflict

    def shift_route(self):
        pass

    def skip_to(self, t):
        pass
