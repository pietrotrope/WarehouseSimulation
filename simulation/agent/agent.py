import json
import multiprocessing
import os
import threading
import socket
import socketserver
from queue import Queue

from simulation.agent.agent_communication import CommunicationHandler


def talk_to(agent_id, msg):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.connect('/tmp/agents/{}'.format(agent_id))
        msg = json.dumps(msg)
        sock.sendall(bytes(msg+'\n', 'utf-8'))
        sock.close()


class Agent(multiprocessing.Process):

    def __init__(self, agent_id, position):
        self.id = agent_id
        self.position = position
        with open('astar/astarRoutes.json', 'r') as f:
            self.routes = json.load(f)
        self.rx_queue = Queue()
        if not os.path.exists('/tmp/agents'):
            os.mkdir('/tmp/agents')
        server = socketserver.ThreadingUnixStreamServer('/tmp/agents/{}'.format(self.id), CommunicationHandler)
        server.rx_queue = self.rx_queue
        self.srv = threading.Thread(target=server.serve_forever, args=(), daemon=True)
        self.srv.start()
        super().__init__()
