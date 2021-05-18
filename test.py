from simulation.environment import Environment
import pygame
from simulation.tile import Tile, tileColor
import random
from rendering.screen import Screen
import time

env = Environment()
envMap = env.raster_map
scren = Screen(envMap, 20, 1000, 580)
scren.showFrame()
for i in range(len(envMap)):
    for j in range(len(envMap)):
        envMap[i][j] = 2
        scren.showFrame()
        time.sleep(0.5)
        print("changed")

