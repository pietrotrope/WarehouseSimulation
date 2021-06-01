from enum import Enum


class Tile(Enum):
    WALKABLE = 0
    ROBOT = 1
    POD = 2
    POD_TAKEN = 3
    PICKING_STATION = 4
    VISION = 5


tileColor = {
    0: [255, 255, 255],
    1: [0, 0, 0],
    2: [0, 0, 255],
    3: [255, 0, 0],
    4: [0, 255, 0],
    5: [124, 193, 207]
}
