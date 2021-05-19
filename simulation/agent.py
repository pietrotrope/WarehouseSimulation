import json
import threading


class Agent(threading.Thread):

    def __init__(self, id, position):
        super().__init__()
        self.id = id
        self.position = position
        with open('astar/astarRoutes.json', 'r') as f:
            self.routes = json.load(f)

