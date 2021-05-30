import json
import multiprocessing
import os
import threading
import socket
import socketserver
from direction import Direction
from queue import Queue

from simulation.communication.agent_communication import AgentCommunicationHandler


movement = {
    Direction.UP: (0, 1),
    Direction.DOWN: (0, -1),
    Direction.LEFT: (-1, 0),
    Direction.RIGHT: (1, 0)
}


class Agent(multiprocessing.Process):

    def __init__(self, agent_id, position, direction=Direction.DOWN):
        self.id = agent_id
        self.position = position
        self.direction = direction
        self.has_pod = False
        with open('astar/astarRoutes.json', 'r') as f:
            self.routes = json.load(f)
        self.rx_queue = Queue()
        if not os.path.exists('/tmp/agents'):
            os.mkdir('/tmp/agents')
        server = socketserver.ThreadingUnixStreamServer('/tmp/agents/{}'.format(self.id), AgentCommunicationHandler)
        server.rx_queue = self.rx_queue
        self.srv = threading.Thread(target=server.serve_forever, args=(), daemon=True)
        self.srv.start()
        self.vision = None
        super().__init__()

    @staticmethod
    def __communicate_to_env(req):
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.connect('/tmp/environment')
            msg = json.dumps(req)
            sock.sendall(bytes(msg + '\n', 'utf-8'))
            buf = b''
            while True:
                res = sock.recv(1024)
                if not res:
                    break
                buf += res
            res = json.loads(res.decode())
            sock.close()
        return res

    @staticmethod
    def talk_to(agent_id, msg):
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.connect('/tmp/agents/{}'.format(agent_id))
            msg = json.dumps(msg)
            sock.sendall(bytes(msg + '\n', 'utf-8'))
            sock.close()

    def watch(self):
        req = {'req': 'watch', 'id': str(self.id),'content': str(self.direction.value)}
        res = self.__communicate_to_env(req)
        self.vision = res['res']

    def move(self):
        req = {'req': 'move', 'id': str(self.id), 'content': str(self.direction.value)}
        self.__communicate_to_env(req)
        self.position += movement[self.direction]

    def pick_pod(self):
        req = {'req': 'pick_pod', 'id': str(self.id), 'content': str(self.direction.value)}
        self.__communicate_to_env(req)
        self.has_pod = True

    def leave_pod(self):
        req = {'req': 'leave_pod', 'id': str(self.id), 'content': str(self.direction.value)}
        self.__communicate_to_env(req)
        self.has_pod = False

    def run(self):
        pass