from itertools import count
from simulation.tile import Tile

class Agent:

    def __init__(self, agent_id, position, env, route=None, task_handler=None):
        if route is None:
            route = []
        self.id = agent_id
        self.position = position
        self.home = position
        self.route = route
        self.env = env
        self.task_handler = task_handler
        self.task = None
        self.log = [position]
        self.swap_phase = [0, self.id]

    def get_task(self):
        task = self.task_handler.get_task(self.id)
        if task is None:
            return True
        else:
            self.task = task
            graph_to_raster = self.env.graph_to_raster
            raster_to_graph = self.env.raster_to_graph
            id_robot = str(raster_to_graph[self.position])
            id_pod = str(raster_to_graph[task])
            route_to_pod = self.env.routes[id_robot][id_pod]
            if not route_to_pod:
                route_to_pod = [raster_to_graph[self.position]]
            route = route_to_pod

            route_to_ps = self.env.routes[id_pod].copy()
            if route_to_pod[-1] != route_to_ps[0]:
                start = graph_to_raster[route_to_ps[0]][0]
                end = graph_to_raster[route_to_pod[-1]][0]
                movement = tuple(map(lambda i, j: i - j, start, end))
                if self.env.raster_map[tuple(map(lambda i, j: i + j, end, (0, movement[1])))] == Tile.WALKABLE.value:
                    route_to_ps.insert(0,
                                       raster_to_graph[tuple(map(lambda i, j: i + j, end, (0, movement[1])))])
                else:
                    route_to_ps.insert(0,
                                       raster_to_graph[tuple(map(lambda i, j: i + j, end, (movement[0], 0)))])
                route_to_ps.insert(0, route_to_pod[-1])
            route = [*route, *route_to_ps.copy()]
            route_to_ps.reverse()
            route = [*route, *route_to_ps]
            self.route = [graph_to_raster[cell][0] for cell in route]
            return False

    def shift_route(self, i):
        if i:
            self.route.insert(i, self.route[i - 1])          
        else:
            self.route.insert(0, self.position)
            

    def skip_to(self, delta):
        route = self.route
        if len(route) >= delta:
            self.log = [*(self.log), *(self.route[0:delta])]
            self.position = route[delta - 1]
            del route[:delta]
        else:
            self.position = self.home
            self.log.append(self.position)

    def detect_collision(self, i):
        # return collision_type, time, agent, other_agent
        a = self
        x, y = a.route[i]
        aid = a.id
        en = a.env
        i_plus_env_time, i_minus_one, timestamper = i + en.time, i-1, en.timestamp[x][y]
        agents, new_agents, route_i_minus_one, ver2 = timestamper[i_plus_env_time], timestamper[i_plus_env_time + 1], a.route[i_minus_one], a.swap_phase[0] <= 0
        ver, ver3 = new_agents and new_agents[0] != aid, agents and agents[0] != aid and ver2
        if ver3:
            other_agent = en.agents[agents[0]]
            otmi = len(other_agent.route) > i

            if  otmi:
                tbh = i>0
                oar = other_agent.route[i]
                if ((tbh and oar == route_i_minus_one) or (not tbh and oar == a.position)):
                    return 0, i, aid, agents[0]
                else:
                    if ((tbh and oar == other_agent.route[i_minus_one]) or other_agent.swap_phase[0] or (not tbh and oar == other_agent.position)):
                        return 1, i, aid, -1
            else:
                return 1, i, aid, -1
   
        else:
            if not ver:
                return None
            else:
                if ver2:
                    return 1, i, aid, -1
                else:
                    return 1, i, new_agents[0], -1


        if ver:
            return 1, i, aid, -1
        return None