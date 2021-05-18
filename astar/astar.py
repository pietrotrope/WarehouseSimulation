from simulation.tile import Tile
import math
import multiprocessing as mp


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
            return reconstruct_path(came_from, goal.id)[:-1]

        openset.remove(x)

        for y in env.graph.get_node(x).adj:
            if y.type == Tile.WALKABLE:
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
            dic[node.id] = res


def _singleAstarWP(dic, env, node, node2):
    res = astar(env, node, node2)
    if node.id in dic:
        dic[node.id][node2.id] = res
    else:
        dic[node.id] = {node2.id: res}


def computeAstarRoutes(env):
    manager = mp.Manager()
    job = []
    astarRoutes = manager.dict()
    for node in env.graph.nodes:
        if node.type == Tile.POD:
            for node2 in env.graph.nodes:
                if node2.type == Tile.PICKING_STATION:
                    job.append(mp.Process(target=_singleAstarPP,
                                          args=(astarRoutes, env, node, node2)))
        if node.type == Tile.WALKABLE or node.type == Tile.ROBOT:
            for node2 in env.graph.nodes:
                if node2.type == Tile.POD:
                    job.append(mp.Process(target=_singleAstarWP,
                                          args=(astarRoutes, env, node, node2)))
    tot = len(job)
    perc = 0
    while(job != []):
        tmp = []
        x = 0
        while(job != [] and x < 10):
            tmp.append(job.pop(0))
            x += 1
        _ = [p.start() for p in tmp]
        _ = [p.join() for p in tmp]
        percTmp = round((tot-len(job))/tot, 2)
        if percTmp != perc:
            print(str(percTmp)+"%")
            perc = percTmp
    print(dict(astarRoutes))
    return dict(astarRoutes)
