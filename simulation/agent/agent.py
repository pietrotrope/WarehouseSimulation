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
            id_robot = str(self.env.raster_to_graph[self.position])
            id_pod = str(self.env.raster_to_graph[task])
            route_to_pod = self.env.routes[id_robot][id_pod]
            if not route_to_pod:
                route_to_pod = [self.env.raster_to_graph[self.position]]
            route = route_to_pod

            route_to_ps = self.env.routes[id_pod].copy()
            if route_to_pod[-1] != route_to_ps[0]:
                start = self.env.key_to_raster(route_to_ps[0])[0]
                end = self.env.key_to_raster(route_to_pod[-1])[0]
                movement = tuple(map(lambda i, j: i - j, start, end))
                if self.env.raster_map[tuple(map(lambda i, j: i + j, end, (0, movement[1])))] == Tile.WALKABLE.value:
                    route_to_ps.insert(0,
                                       self.env.raster_to_graph[tuple(map(lambda i, j: i + j, end, (0, movement[1])))])
                else:
                    route_to_ps.insert(0,
                                       self.env.raster_to_graph[tuple(map(lambda i, j: i + j, end, (movement[0], 0)))])
                route_to_ps.insert(0, route_to_pod[-1])
            route = [*route, *route_to_ps.copy()]
            route_to_ps.reverse()
            route = [*route, *route_to_ps]
            self.route = [self.env.key_to_raster(cell)[0] for cell in route]
            return False

    def shift_route(self, i):
        if i <= 0:
            self.route.insert(0, self.position)
        else:
            self.route.insert(i, self.route[i - 1])

    def skip_to(self, delta):
        if delta > 0:
            if len(self.route) >= delta:
                self.log = [*(self.log), *(self.route[0:delta])]
                self.position = self.route[delta - 1]
                del self.route[:delta]
            else:
                if self.route:
                    self.position = self.route[-1]
                    self.log = [*(self.log), *(self.route)]
                    self.route.clear()
                else:
                    self.position = self.home
                    self.log.append(self.position)

    def detect_collision(self, i):
        # return collision_type, time, agent, other_agent
        x, y = self.route[i]
        i_plus_env_time, i_minus_one, other_agent = i + self.env.time, i-1, None
        agents, new_agents, route_i_minus_one, ver2 = self.env.tile_map[x][y].timestamp[i_plus_env_time], self.env.tile_map[x][y].timestamp[i_plus_env_time + 1], self.route[i_minus_one], self.swap_phase[0] <= 0
        ver, ver3 = new_agents and new_agents[0] != self.id, agents and agents[0] != self.id and ver2
        if ver3:
            other_agent = self.env.agents[agents[0]]
        
        if (not ver and not ver3):
            return None

        if ver3 and len(other_agent.route) > i and ((i>0 and other_agent.route[i] == route_i_minus_one) or (i<=0 and other_agent.route[i] == self.position)):
            return 0, i, self.id, agents[0]
        
        if ver:
            if ver2:
                return 1, i, self.id, -1
            else:
                return 1, i, new_agents[0], -1   
        
        if ver3 and ((len(other_agent.route)<=i) or (i>0 and other_agent.route[i] == other_agent.route[i_minus_one]) or (i<=0 and other_agent.route[i] == other_agent.position) or(other_agent.swap_phase[0] != 0) or ver):
            return 1, i, self.id, -1

        return None
    