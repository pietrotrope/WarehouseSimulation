import pygame
from simulation.tile import Tile, tileColor
import socket
import json
import numpy as np


class Screen:

    def __init__(self, tile_size, screen_width=800, screen_height=600, host='localhost', port=50666):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.done = False
        self.tileSize = tile_size
        self.map = None
        self.host = host
        self.port = port
        self.clock = pygame.time.Clock()

    def draw_square_(self, x, y, col):
        pygame.draw.rect(self.screen,
                         col,
                         pygame.Rect(y * self.tileSize + 1,
                                     x * self.tileSize + 1,
                                     self.tileSize - 1,
                                     self.tileSize - 1))

    def draw(self):
        self.update_map()
        for x in range(len(self.map)):
            for y in range(len(self.map[0])):
                self.draw_square_(x, y, tileColor[self.map[x][y]])

    def draw_frame(self):
        self.draw()
        pygame.display.flip()

    def update_map(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.host, self.port))
            sock.sendall(b'map')
            buf = b''
            while True:
                resp = sock.recv(1024)
                if not resp:
                    break
                buf += resp

            data = buf.decode()
            raster_map = np.array(json.loads(data))
            sock.close()
        self.map = raster_map

    def run(self):
        while not self.done:
            self.clock.tick(30)
            self.draw_frame()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
        pygame.quit()


if __name__ == '__main__':
    s = Screen(16)
    s.run()
