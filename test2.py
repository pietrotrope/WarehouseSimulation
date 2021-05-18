from rendering import screen
from simulation.environment import Environment
from simulation.graph import node
from simulation.tile import Tile
import math
from astar.astar import astar, computeAstarRoutes
from rendering.screen import Screen, CommunicationSocket
import time
import json

env = Environment()

"""
start = None
end = None

for node in env.graph.nodes:
    if node.type == Tile.PICKING_STATION:
        start = node
    if end == None and node.type == Tile.POD:
        end = node

ids = astar(env, start, end)


scr = Screen(15)
envMap = env.raster_map
for SingleId in ids:
    x, y = env.key_to_raster(SingleId)[0]
    envMap[x][y]=3

scr.commSocket.matrix = envMap
scr.run()
"""
start = time.time()
dic = computeAstarRoutes(env)
with open("astarRoutes.json", "w") as fp:
    json.dump(dic, fp)
print(time.time()-start)
print("seconds to compute all the routes")


    
