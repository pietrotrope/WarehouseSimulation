from simulation.environment import Environment
from simulation.graph import node
from simulation.tile import Tile
import math
from astar.astar import astar

env = Environment()


start = None
end = None

for node in env.graph.nodes:
    if start == None and node.type == Tile.PICKING_STATION:
        start = node
    if end == None and node.type == Tile.POD:
        end = node

ids = astar(env, start, end)

print(ids)
for SingleId in ids:
    print(SingleId)
