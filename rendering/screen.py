import pygame
from simulation.tile import Tile, tileColor
import socket
import json
import numpy as np
import random

HOST, PORT = 'localhost', 50666

class Screen:

    def __init__(self, tileSize, screenWidth=800, screenHeight=600):
        pygame.init()
        self.screen = pygame.display.set_mode((screenWidth, screenHeight))
        self.done = False
        self.tileSize = tileSize
        self.map = None
        self.clock = pygame.time.Clock()

    def drawSquare(self, x, y, col):
        pygame.draw.rect(self.screen,
                         col,
                         pygame.Rect(y * self.tileSize + 1,
                                     x * self.tileSize + 1,
                                     self.tileSize - 1,
                                     self.tileSize - 1))

    def draw(self):
        self.get_map()
        for x in range(len(self.map)):
            for y in range(len(self.map[0])):
                self.drawSquare(x, y, tileColor[self.map[x][y]])

    def showFrame(self):
        self.draw()
        pygame.display.flip()

    def get_map(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))
            sock.sendall(b'map')
            resp = sock.recv(8192)
            resp = resp.decode()
            raster_map = np.array(json.loads(resp))
            sock.sendall(b'bye')
            sock.close()
        self.map = raster_map

    def run(self):
        while not self.done:
            self.clock.tick(30)
            self.showFrame()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
        pygame.quit()
