import os
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
        print('Got a connection')
        a = self.rfile.readline()
        msg = json.loads(a)
        if msg['req'] == 'watch':
            agent_id = msg['id']
            direction = Direction(msg['content'])
            pos = self.server.env.agents[agent_id]['Position']
            node = self.server.env.graph.get_node(self.server.env.raster_to_graph[pos])
            field_of_view = [[], [], []]
            for n in node.adj:
                if pos + movement[direction] == n.coord:
                    if n.type == Tile.WALKABLE or n.type == Tile.PICKING_STATION:
                        for nn in n.adj:
                            for nnn in nn.adj:
                                if nnn not in field_of_view:
                                    field_of_view[2].append(nnn)

                            if nn not in field_of_view:
                                field_of_view[1].append(nn)

                    if n not in field_of_view:
                        field_of_view[0].append(n)

            res = {'res': field_of_view}
            self.wfile.write(bytes(json.dumps(res) + '\n', 'utf-8'))
            return
        elif msg['req'] == 'move':
            direction = Direction(msg['content'])
            agent_id = msg['id']
            node = self.server.env.graph.get_node(self.server.env.raster_to_graph[
                                                      self.server.env.agents[agent_id]['Position']])
            node.agent_id = None
            self.server.env.update_map(coord=self.server.env.agents[agent_id]['Position'], tile=Tile.WALKABLE)
            self.server.env.agents[agent_id]['Position'] = tuple(map(lambda i, j: i + j,
                                                                     self.server.env.agents[agent_id]['Position'],
                                                                     movement[direction]))
            self.server.env.update_map(coord=self.server.env.agents[agent_id]['Position'], tile=Tile.ROBOT)
            node = self.server.env.graph.get_node(self.server.env.raster_to_graph[
                                                      self.server.env.agents[agent_id]['Position']])
            node.agent_id = agent_id
            self.wfile.write(bytes(json.dumps({'res': True}) + '\n', 'utf-8'))
            return
        elif msg['req'] == 'pick_pod':
            direction = Direction(msg['content'])
            agent_id = msg['id']
            pod_position = self.server.env.agents[agent_id]['Position'] + movement[direction]
            pod_node = self.server.env.graph.get_node(pod_position)
            if pod_node.type == Tile.POD:
                pod_node.agent_id = agent_id
                self.server.env.update_map(coord=pod_position, tile=Tile.POD_TAKEN)
            self.wfile.write(bytes(json.dumps({'res': True}) + '\n', 'utf-8'))
            return
        elif msg['req'] == 'leave_pod':
            direction = Direction(msg['content'])
            agent_id = msg['id']
            pod_position = self.server.env.agents[agent_id]['Position'] + movement[direction]
            pod_node = self.server.env.graph.get_node(pod_position)
            if pod_node.type == Tile.POD_TAKEN and pod_node.agent_id == agent_id:
                pod_node.agent_id = None
                self.server.env.update_map(coord=pod_position, tile=Tile.POD)
            self.wfile.write(bytes(json.dumps({'res': True}) + '\n', 'utf-8'))
            return
        elif msg['req'] == 'shutdown':
            self.server.shutdown()
            os.remove('/tmp/environment')
        # Maybe get task?

    def finish(self) -> None:
        pass
