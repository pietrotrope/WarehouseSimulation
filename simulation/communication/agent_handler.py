import socketserver
import json
from typing import Tuple, Callable


class CommunicationServer(socketserver.BaseServer):
    def __init__(self,
                 server_address: Tuple[str, int],
                 RequestHandlerClass: Callable[..., socketserver.StreamRequestHandler],
                 env):
        super().__init__(server_address, RequestHandlerClass)
        self.env = env


class AgentHandler(socketserver.StreamRequestHandler):

    def handle(self) -> None:
        msg = json.load(self.rfile)
        if msg['req'] == 'get_graph':
            # TODO: return only nodes close to the agent
            pass
        elif msg['req'] == 'move':
            # TODO: Update map with new agent position
            pass
        elif msg['req'] == 'pick_pod':
            # TODO: Set picked pod as taken
            pass
        elif msg['req'] == 'leave_pod':
            # TODO: Set agent pod as free
            pass
        # Maybe get task?

    def finish(self) -> None:
        pass
