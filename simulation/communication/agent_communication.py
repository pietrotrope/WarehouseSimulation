import os
import socketserver
import json
from typing import Tuple, Callable
import numpy as np


class AgentCommunicationServer(socketserver.BaseServer):
    def __init__(self,
                 server_address: Tuple[str, int],
                 RequestHandlerClass: Callable[..., socketserver.StreamRequestHandler],
                 rx_queue, agent_id):
        super().__init__(server_address, RequestHandlerClass)
        self.rx_queue = rx_queue
        self.agent_id = agent_id


class AgentCommunicationHandler(socketserver.StreamRequestHandler):

    def handle(self) -> None:
        msg = json.load(self.rfile)
        if msg['req'] == 'shutdown':
            self.server.shutdown()
            os.remove('/tmp/agents/{}'.format(self.server.agent_id))
        self.server.rx_queue.put(msg)  # Is this queue necessary? All needed communication can be handled here

    def finish(self) -> None:
        pass
