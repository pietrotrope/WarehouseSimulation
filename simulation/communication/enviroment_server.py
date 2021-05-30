import socketserver
import json
from typing import Tuple, Callable
import numpy as np
import logging


class EnvironmentServer(socketserver.BaseServer):
    def __init__(self,
                 server_address: Tuple[str, int],
                 RequestHandlerClass: Callable[..., socketserver.BaseRequestHandler],
                 raster_map):
        self.raster_map = raster_map
        logging.info('Environment server listening at {}:{}'.format(server_address[0], server_address[1]))
        super().__init__(server_address, RequestHandlerClass)


class EnvironmentToScreenServer(socketserver.BaseRequestHandler):

    def handle(self) -> None:
        data = self.request.recv(1024)
        data = data.decode()
        if data.strip() == 'map':
            raster_map = self.server.raster_map
            raster_map = raster_map.tolist()
            json_map = json.dumps(raster_map)
            json_map = json_map.encode()
            self.request.sendall(json_map)
            return
        if data.strip == 'shutdown':
            self.server.shutdown()

    def finish(self) -> None:
        pass
