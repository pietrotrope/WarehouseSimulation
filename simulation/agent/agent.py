
import multiprocessing
from .direction import Direction

movement = {
    Direction.UP: (0, 1),
    Direction.DOWN: (0, -1),
    Direction.LEFT: (-1, 0),
    Direction.RIGHT: (1, 0)
}


class Agent(multiprocessing.Process):

    def __init__(self, agent_id, position, direction=Direction.DOWN, tps=30):
        self.id = agent_id
        self.position = position
        self.direction = direction
        self.tps = tps
        self.has_pod = False
        pass
