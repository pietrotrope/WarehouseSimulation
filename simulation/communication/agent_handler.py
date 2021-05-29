import socketserver
import json
from typing import Tuple, Callable

from simulation.agent.direction import Direction
from simulation.tile import Tile

movement = {
    Direction.UP: (0, 1),
    Direction.DOWN: (0, -1),
    Direction.LEFT: (-1, 0),
    Direction.RIGHT: (1, 0)
}

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
        if msg['req'] == 'watch':
            agent_id = msg['id']
            pos = self.server.env.agents[agent_id]['Position']
            node = self.server.env.graph.get_node(self.server.env.raster_to_graph[pos])
            view_range = []
            for n in node.adj:
                if n.type == Tile.WALKABLE or n.type == Tile.PICKING_STATION:
                    for nn in n.adj:
                        if nn not in view_range:
                            view_range.append(nn)

                    if n not in view_range:
                        view_range.append(n)
            json.dump(view_range, self.wfile)
            return
        elif msg['req'] == 'move':
            dir = Direction(msg['content'])
            agent_id = msg['id']
            self.server.env.update_map(coord=self.server.env.agents[agent_id]['Position'], tile=Tile.WALKABLE)
            self.server.env.agents[agent_id]['Position'] += movement[dir]
            self.server.env.update_map(coord=self.server.env.agents[agent_id]['Position'], tile=Tile.ROBOT)
        elif msg['req'] == 'pick_pod':
            # TODO: Set picked pod as taken
            pass
        elif msg['req'] == 'leave_pod':
            # TODO: Set agent pod as free
            pass
        # Maybe get task?

    def finish(self) -> None:
        pass
