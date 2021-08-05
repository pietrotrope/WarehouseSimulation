from numpy.lib.function_base import append
from simulation.tile import Tile
import math
import multiprocessing as mp

manager = mp.Manager()


def average_point(listOfPoints):
    x = 0
    y = 0
    for point in listOfPoints:
        x += point[0]
        y += point[1]
    tot = len(listOfPoints)
    return (x/tot, y/tot)


def distance(env, start_node, goal):
    x1, y1 = average_point(env.key_to_raster(start_node.id))
    x2, y2 = average_point(env.key_to_raster(goal.id))
    return math.sqrt(abs(x1-x2)) + math.sqrt(abs(y1-y2))


def reconstruct_path(came_from, current_node):
    totalPath = []
    came_from_keys = came_from.keys()
    while current_node in came_from_keys:
        current_node = came_from[current_node]
        totalPath.append(current_node)
    return totalPath


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

        if x == goal.id:
            path = reconstruct_path(came_from, goal.id)[:-1]
            path.reverse()
            return path

        openset.remove(x)

        for y in env.graph.get_node(x).adj:
            if (y.type == Tile.WALKABLE or y.type == Tile.ROBOT or y.id == goal.id):
                if y.id not in g_score:
                    g_score[y.id] = math.inf

                tentative_g_score = g_score[x] + 1
                if tentative_g_score < g_score[y.id]:
                    came_from[y.id] = x
                    g_score[y.id] = tentative_g_score
                    f_score[y.id] = g_score[y.id] + distance(env, y, goal)
                    if y.id not in openset:
                        openset.append(y.id)
    return []


def _singleAstarPP(dic, env, node, node2):
    res = astar(env, node, node2)
    if node.id in dic:
        if len(res) < len(dic[node.id]):
            dic[node.id] = res
    else:
        subDic = manager.dict()
        subDic[node2.id] = res
        dic[node.id] = subDic


def _singleAstarWP(dic, env, node, node2):
    res = []
    if node.id in dic:
        if node2.id not in dic[node.id]:
            res = astar(env, node, node2)
            dic[node.id][node2.id] = res
    else:
        res = astar(env, node, node2)
        subDic = manager.dict()
        subDic[node2.id] = res
        dic[node.id] = subDic
    if res != []:
        for i in range(len(res)-1):
            nodeid = res[i]
            if nodeid in dic:
                dic[nodeid][node2.id] = res[i+1:]
            else:
                subDic = manager.dict()
                subDic[node2.id] = res[i+1:]
                dic[nodeid] = subDic


def computeAstarRoutes(env):
    job = []
    astarRoutes = manager.dict()

    pods = []
    walkables = []
    picking_stations = []

    for node in env.graph.nodes:
        if node.type == Tile.POD:
            pods.append(node)
        elif node.type == Tile.PICKING_STATION:
            picking_stations.append(node)
        else:
            walkables.append(node)
    
    for node in walkables:
        for node2 in pods:
            job.append((astarRoutes, env, node, node2))
    for node in picking_stations:
        for node2 in pods:
            job.append((astarRoutes, env, node, node2))
    for node in pods:
        for neighbour in node.adj:
            if neighbour.type == Tile.WALKABLE:
                for picking_station in picking_stations:
                    job.append((astarRoutes, env, neighbour, picking_station))
    """
    for node in env.graph.nodes:
        if node.type == Tile.POD:
            for node2 in env.graph.nodes:
                if node2.type == Tile.PICKING_STATION:
                    job.append((astarRoutes, env, node, node2))
        if node.type == Tile.WALKABLE or node.type == Tile.ROBOT:
            for node2 in env.graph.nodes:
                if node2.type == Tile.POD:
                    job.append((astarRoutes, env, node, node2))
    """
    tot = len(job)
    perc = 0
    while(job != []):
        tmp = []
        x = 0
        while(job != [] and len(tmp) < 10):
            newJob = job.pop(0)
            done = False
            if newJob[2].id in astarRoutes:
                if newJob[3].id in astarRoutes[newJob[2].id]:
                    done = True
            if not done:
                if newJob[2].type == Tile.POD:
                    tmp.append(mp.Process(target=_singleAstarPP, args=newJob))
                else:
                    tmp.append(mp.Process(target=_singleAstarWP, args=newJob))

        _ = [p.start() for p in tmp]
        _ = [p.join() for p in tmp]

        percTmp = round((tot-len(job))/tot, 2)*100
        if percTmp != perc:
            print(str(percTmp)+"%")
            perc = percTmp
    return dict(astarRoutes)
