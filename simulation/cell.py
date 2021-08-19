from collections import defaultdict


class Cell:
    def __init__(self, tile):
        self.tile = tile
        self.timestamp = defaultdict(list)
