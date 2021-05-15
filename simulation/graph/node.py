from simulation.tile import Tile


class Node:

    def __init__(self, identifier=None, adj=None, tile=Tile.WALKABLE):
        if adj is None:
            adj = []
        self.adj = adj
        self.id = identifier
        self.type = tile

    def change_type(self, tile):
        self.type = tile
