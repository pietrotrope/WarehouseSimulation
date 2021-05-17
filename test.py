from simulation.environment import Environment
import pygame
from simulation.tile import Tile, tileColor
import random
from rendering.screen import Screen

env = Environment()
envMap = env.raster_map
scren = Screen(envMap, 20, 1000, 580)

done = False
while not done:
    scren.draw()
    pygame.display.flip()
    envMap[random.randrange(len(envMap))][random.randrange(len(envMap[0]))] = 2

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
