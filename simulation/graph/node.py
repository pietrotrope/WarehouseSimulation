from simulation.tile import Tile


class Node:

    def __init__(self, identifier=None, coord=None, adj=None, agent_id=None, tile=Tile.WALKABLE):
        if adj is None:
            adj = []
        self.adj = adj
        self.id = identifier
        self.coord = coord
        self.type = tile
        self.agent_id = agent_id

    def change_type(self, tile):
        self.type = tile
