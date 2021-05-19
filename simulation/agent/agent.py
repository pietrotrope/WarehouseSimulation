import json
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


class Agent(threading.Thread):

    def __init__(self, agent_id, position):
        super().__init__()
        self.id = id
        self.position = position
        with open('astar/astarRoutes.json', 'r') as f:
            self.routes = json.load(f)
        self.rx_queue = Queue()
        server = socketserver.ThreadingUnixStreamServer('/tmp/agents/{}'.format(id), CommunicationHandler)
        server.rx_queue = self.rx_queue
