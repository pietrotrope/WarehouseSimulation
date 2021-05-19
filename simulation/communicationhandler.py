import socketserver
import json
from typing import Tuple, Callable
import numpy as np


class CommunicationServer(socketserver.BaseServer):
    def __init__(self,
                 server_address: Tuple[str, int],
                 RequestHandlerClass: Callable[..., socketserver.BaseRequestHandler],
                 raster_map):
        super().__init__(server_address, RequestHandlerClass)
        self.raster_map = raster_map


class CommunicationHandler(socketserver.BaseRequestHandler):

    def handle(self) -> None:
        while True:
            data = self.request.recv(1024)
            data = data.decode()
            if data.strip() == 'map':
                raster_map = self.server.raster_map
                raster_map = raster_map.tolist()
                json_map = json.dumps(raster_map)
                json_map = json_map.encode()
                self.request.sendall(json_map)
                return
            if data.strip() == 'bye':
                return

    def finish(self) -> None:
        pass
