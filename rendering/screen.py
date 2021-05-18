from simulation.environment import Environment
import pygame
from simulation.tile import Tile, tileColor
import random

class Screen:

    def __init__(self, tileSize, screenWidth = 800, screenHeight = 600):
        pygame.init()
        self.screen = pygame.display.set_mode((screenWidth, screenHeight))
        self.done = False
        self.tileSize = tileSize
        self.commSocket = CommunicationSocket()
        clock = pygame.time.Clock()

    def drawSquare(self, x, y, col):
        pygame.draw.rect(self.screen,
                         col,
                         pygame.Rect(y * self.tileSize + 1,
                                     x * self.tileSize + 1,
                                     self.tileSize - 1,
                                     self.tileSize - 1))

    def draw(self):
        matrix = self.commSocket.get_matrix()
        for x in range(len(matrix)):
            for y in range(len(matrix[0])):
                self.drawSquare(x, y, tileColor[matrix[x][y]])

    def showFrame(self):
            self.draw()
            pygame.display.flip()
    
    def run(self):
        while not self.done:
            self.showFrame()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
        pygame.quit()


class CommunicationSocket:
    def __init__(self) -> None:
        pass
    
    def get_matrix(self):
        return [[0, 0, 1], [0, 1, 2]]
    
