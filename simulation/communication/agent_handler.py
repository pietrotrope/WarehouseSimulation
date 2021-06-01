import os
import socketserver
import json
from typing import Tuple, Callable

from simulation.agent.direction import Direction
from simulation.tile import Tile

movement = {
    Direction.UP: (-1, 0),
    Direction.DOWN: (1, 0),
    Direction.LEFT: (0, -1),
    Direction.RIGHT: (0, 1)
}


class CommunicationServer(socketserver.BaseServer):
    def __init__(self,
                 server_address: Tuple[str, int],
                 RequestHandlerClass: Callable[..., socketserver.StreamRequestHandler],
                 env):
        super().__init__(server_address, RequestHandlerClass)
        self.env = env


class AgentHandler(socketserver.StreamRequestHandler):

    def watch(self, msg: dict) -> None:
        agent_id = msg['id']
        direction = Direction(msg['content'])
        pos = self.server.env.agents[agent_id]['Position']
        node = self.server.env.graph.get_node(self.server.env.raster_to_graph[pos])
        field_of_view = [[], [], []]
        next_block = tuple(map(lambda i, j: i + j, pos, movement[direction]))

        for n in node.adj:
            if next_block == n.coord[0]:
                if n.type == Tile.WALKABLE or n.type == Tile.PICKING_STATION:
                    if n.coord not in [item for sublist in field_of_view for item in sublist]:
                        self.server.env.update_map(key=n.id, tile=Tile.VISION)
                        field_of_view[0].append(n.coord)
                    for nn in n.adj:
                        if nn.type == Tile.WALKABLE or nn.type == Tile.PICKING_STATION:
                            if nn.coord not in [item for sublist in field_of_view for item in sublist]:
                                self.server.env.update_map(key=nn.id, tile=Tile.VISION)
                                field_of_view[1].append(nn.coord)
                            for nnn in nn.adj:
                                if nnn.type == Tile.WALKABLE or nnn.type == Tile.PICKING_STATION:
                                    self.server.env.update_map(key=nnn.id, tile=Tile.VISION)
                                    field_of_view[2].append(nnn.coord)

        res = {'res': field_of_view}
        self.wfile.write(bytes(json.dumps(res) + '\n', 'utf-8'))

    def move(self, msg: dict) -> None:
        direction = Direction(msg['content'])
        agent_id = msg['id']
        pos = self.server.env.agents[agent_id]['Position']
        view_range = self.server.env.raster_map[pos[0]-4:pos[0]+4, pos[1]-4:pos[1]+4]
        start_index = [pos[0]-4, pos[0]+4]
        end_index = [pos[1]-4, pos[1]+4]
        for i in range(start_index[0], end_index[0]):
            for j in range(start_index[1], end_index[1]):
                self.server.env.update_map(coord=(i, j), type=Tile.WALKABLE)

        node = self.server.env.graph.get_node(self.server.env.raster_to_graph[pos])
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
        self.wfile.flush()

    def pick_pod(self, msg: dict) -> None:
        direction = Direction(msg['content'])
        agent_id = msg['id']
        pod_position = tuple(map(lambda i, j: i + j, self.server.env.agents[agent_id]['Position'], movement[direction]))
        pod_node = self.server.env.graph.get_node(self.server.env.raster_to_graph[pod_position])
        if pod_node.type == Tile.POD:
            pod_node.agent_id = agent_id
            self.server.env.update_map(coord=pod_position, tile=Tile.POD_TAKEN)
        self.wfile.write(bytes(json.dumps({'res': True}) + '\n', 'utf-8'))
        self.wfile.flush()

    def leave_pod(self, msg: dict) -> None:
        direction = Direction(msg['content'])
        agent_id = msg['id']
        pod_position = tuple(map(lambda i, j: i + j, self.server.env.agents[agent_id]['Position'], movement[direction]))
        pod_node = self.server.env.graph.get_node(self.server.env.raster_to_graph[pod_position])
        if pod_node.type == Tile.POD_TAKEN and pod_node.agent_id == agent_id:
            pod_node.agent_id = None
            self.server.env.update_map(coord=pod_position, tile=Tile.POD)
        self.wfile.write(bytes(json.dumps({'res': True}) + '\n', 'utf-8'))

    def shutdown(self, msg: dict) -> None:
        self.server.shutdown()
        os.remove('/tmp/environment')

    def handle(self) -> None:
        a = self.rfile.readline()
        msg = json.loads(a)
        action = getattr(self, msg['req'])
        action(msg)
        return
        # Maybe get task?

    def finish(self) -> None:
        pass
