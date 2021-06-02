import json
import multiprocessing
import os
import threading
import socket
import socketserver
import time
from multiprocessing import Queue

from .direction import Direction

from simulation.communication.agent_communication import AgentCommunicationHandler


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
        with open('astar/astarRoutes.json', 'r') as f:
            self.routes = json.load(f)
        self.conflicts = Queue()
        if not os.path.exists('/tmp/agents'):
            os.mkdir('/tmp/agents')
        server = socketserver.ThreadingUnixStreamServer('/tmp/agents/{}'.format(self.id), AgentCommunicationHandler)
        server.conflicts = self.conflicts
        server.agent_id = self.id
        self.srv = threading.Thread(target=server.serve_forever, args=(), daemon=True)
        self.srv.start()
        self.vision = None
        super().__init__()

    @staticmethod
    def __communicate_to_env(req):
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.connect('/tmp/environment')
            msg = json.dumps(req)
            sock.sendall(msg.encode() + b'\n')
            buf = b''
            while True:
                res = sock.recv(1024)
                if not res:
                    break
                buf += res
            res = json.loads(buf.decode())
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
        req = {'req': 'watch', 'id': str(self.id), 'content': str(self.direction.value)}
        res = self.__communicate_to_env(req)
        self.vision = res['res']

    def move(self):
        req = {'req': 'move', 'id': str(self.id), 'content': str(self.direction.value)}
        self.__communicate_to_env(req)
        self.position = tuple(map(lambda i, j: i + j, self.position, movement[self.direction]))

    def pick_pod(self):
        req = {'req': 'pick_pod', 'id': str(self.id), 'content': str(self.direction.value)}
        self.__communicate_to_env(req)
        self.has_pod = True

    def leave_pod(self):
        req = {'req': 'leave_pod', 'id': str(self.id), 'content': str(self.direction.value)}
        self.__communicate_to_env(req)
        self.has_pod = False

    def run(self):
        while True:
            if self.conflicts.empty():
                # TODO: Fetch messages from self.rx_queue
                # TODO: Do actions based on self.rx_queue messages
                # TODO: If has_task and has_pod move towards picking_station
                time.sleep(1.0/self.tps)
            else:
                pass

    def __exit__(self):
        self.talk_to(self.id, json.dumps({'req': 'shutdown'}))
