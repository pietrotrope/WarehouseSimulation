from simulation.environment import Environment
from simulation.graph import node
from simulation.tile import Tile
import math


def distance(env, start_node, goal):
    x1, y1 = env.graph_to_raster[start_node.id][0]
    print(goal.id)
    print(env.graph_to_raster[goal.id])
    x2, y2 = env.graph_to_raster[goal.id][0]
    return math.sqrt(abs(x1-x2)) + math.sqrt(abs(y1-y2))


def reconstruct_path(came_from, current_node):
    if current_node in came_from:
        p = reconstruct_path(came_from, came_from[current_node])
        return (p + [current_node])
    else:
        return []


def astar(env, start_node, goal):
    g_score = {}
    h_score = {}
    f_score = {}

    closedset = []
    openset = [start_node.id]
    g_score[start_node.id] = 0
    came_from = {}
    h_score[start_node.id] = distance(env, start_node, goal)
    f_score[start_node.id] = h_score[start_node.id]

    while openset != []:
        x = openset[0]
        for node_id in openset:
            if f_score[node_id] < f_score[x]:
                x = node_id
        if x == goal.id:
            return reconstruct_path(came_from, goal.id)
        openset.remove(x)
        closedset.append(x)
        for y in env.graph.get_node(x).adj:
            if y.id in closedset:
                continue
            came_from[y.id] = x
            g_score[y.id] = g_score[x] + 1
            h_score[y.id] = distance(env, env.graph.get_node(x), y)
            f_score[y.id] = g_score[y.id] + h_score[y.id]

            for open_node in openset:
                if y.id == open_node and g_score[y.id] > g_score[open_node]:
                    continue

            openset.append(y.id)
    return []


env = Environment()


start = None
end = None

for node in env.graph.nodes:
    if start == None and node.type == Tile.PICKING_STATION:
        start = node
    if end == None and node.type == Tile.POD:
        end = node

ids = astar(env, start, end)

for SingleId in ids:
    print(env.graph_to_raster[SingleId])


"""

astarRoutes = {}
for node in env.graph.nodes:
    if node.tile == Tile.POD:
        for node2 in env.graph.nodes:
            if node2.tile == Tile.PICKING_STATION:
                res = astar(node, node2)
                if node.id in astarRoutes:
                    if len(res) < len(astarRoutes[node.id]):
                        astarRoutes[node.id] = res
                else:
                    astarRoutes[node.id] = res
    if node.tile == Tile.WALKABLE:
        for node2 in env.graph.nodes:
            if node2.tile == Tile.POD:
                res = astar(node, node2)
                if node.id in astarRoutes:
                    astarRoutes[node.id][node2.id] = res
                else:
                    astarRoutes[node.id] = {node2.id:res}

"""