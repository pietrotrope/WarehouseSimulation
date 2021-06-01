import os
import socketserver
import json
from typing import Tuple, Callable
import numpy as np


class AgentCommunicationServer(socketserver.BaseServer):
    def __init__(self,
                 server_address: Tuple[str, int],
                 RequestHandlerClass: Callable[..., socketserver.StreamRequestHandler],
                 conflicts, agent_id):
        super().__init__(server_address, RequestHandlerClass)
        self.conflicts = conflicts
        self.agent_id = agent_id


class AgentCommunicationHandler(socketserver.StreamRequestHandler):

    def handle(self) -> None:
        a = self.rfile.readline()
        msg = json.loads(a)
        if msg['req'] == 'shutdown':
            self.server.shutdown()
            os.remove('/tmp/agents/{}'.format(self.server.agent_id))
        self.server.conflicts.put(msg['req'])

    def finish(self) -> None:
        pass
