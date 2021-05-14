import pygame
import random
from configuration import *
from environment import *
from task import *
from agent import Agent

pygame.init()
screen = pygame.display.set_mode((screenWidth, screenHeight))
done = False

clock = pygame.time.Clock()

def drawSquare(creen, size, x, y, col):
  pygame.draw.rect(screen, col, pygame.Rect(y * size + 1, x * size + 1, size - 1, size - 1))

def draw(Matrix):
    for y in range(nCols):
        for x in range(nRows):
          if Matrix[x][y] == 0:
            drawSquare(screen, size, x, y, [255, 255, 255])
          elif Matrix[x][y] == 4:
            drawSquare(screen, size, x, y, [255, 255, 0])
          else:
            col = [0, 0, 0]
            col[Matrix[x][y]-1]=255
            drawSquare(screen, size, x, y, col)
  
def nextState(agentsList):
  for agent in agentsList:
    agent.move()



a1 = Agent((4,4))
a2 = Agent((13,25))
a3 = Agent((24,40))
agentsList = [a1, a2, a3]

draw(griglia)

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
    nextState(agentsList)
    draw(griglia)
    pygame.display.flip()
    clock.tick(fps)


pygame.quit()
