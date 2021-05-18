from simulation.environment import Environment
from simulation.graph import node
from simulation.tile import Tile
import math

def average_point(listOfPoints):
    x = 0
    y = 0
    for point in listOfPoints:
        x += point[0]
        y += point[1]
    x = x/len(listOfPoints)
    y = y/len(listOfPoints)
    return (x, y)

def distance(env, start_node, goal):
    p1 = env.key_to_raster(start_node.id)
    p2 = env.key_to_raster(goal.id)
    x1, y1 = average_point(p1)
    x2, y2 = average_point(p2)
    return math.sqrt(abs(x1-x2)) + math.sqrt(abs(y1-y2))


def reconstruct_path(came_from, current_node):
    if current_node in came_from:
        p = reconstruct_path(came_from, came_from[current_node])
        return (p + [current_node])
    else:
        return []


def astar(env, start_node, goal):
    g_score = {}
    f_score = {}

    came_from = {}
    
    openset = [start_node.id]
    g_score[start_node.id] = 0
    f_score[start_node.id] = distance(env, start_node, goal)

    while openset != []:
        x = openset[0]
        for node_id in openset:
            if f_score[node_id] < f_score[x]:
                x = node_id
        

        if goal in env.graph.get_node(x).adj:
            came_from[goal.id] = x
            return reconstruct_path(came_from, goal.id)

        openset.remove(x)

        for y in env.graph.get_node(x).adj:
            if y.type == Tile.WALKABLE:
                if y.id not in g_score:
                    g_score[y.id]=math.inf

                tentative_g_score = g_score[x] + 1
                if tentative_g_score < g_score[y.id]:
                    came_from[y.id] = x
                    g_score[y.id] = tentative_g_score
                    f_score[y.id] = g_score[y.id] + distance(env, y, goal)
                    if y.id not in openset:
                        openset.append(y.id)           

    return []


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
