from simulation.environment import Environment
import pygame
from simulation.tile import Tile, tileColor
import random

class Screen:

    def __init__(self, matrix, tileSize, screenWidth = 800, screenHeight = 600):
        pygame.init()
        self.screen = pygame.display.set_mode((screenWidth, screenHeight))
        self.done = False
        self.matrix = matrix
        self.tileSize = tileSize
        print(len(matrix))
        print(len(matrix[0]))

        clock = pygame.time.Clock()

    def drawSquare(self, x, y, col):
        pygame.draw.rect(self.screen,
                         col,
                         pygame.Rect(y * self.tileSize + 1,
                                     x * self.tileSize + 1,
                                     self.tileSize - 1,
                                     self.tileSize - 1))

    def draw(self):
        for x in range(len(self.matrix)):
            for y in range(len(self.matrix[0])):
                self.drawSquare(x, y, tileColor[self.matrix[x][y]])
