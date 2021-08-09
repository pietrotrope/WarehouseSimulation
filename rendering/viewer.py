from ast import literal_eval
from numpy.lib.histograms import _histogram_bin_edges_dispatcher
import pygame
from pygame.constants import K_LEFT, K_RIGHT
from simulation.tile import tileColor
import numpy as np
import pandas as pd
from csv import reader
import time


class Screen:

    def __init__(self, tile_size, screen_width=800, screen_height=600):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.done = False
        self.tileSize = tile_size
        self.map = np.array(pd.read_csv('map.csv', header=None))
        self.history = []
        with open('out.csv', 'r') as read_obj:
            csv_reader = reader(read_obj)
            for row in csv_reader:
                self.history.append(row)
        self.clock = pygame.time.Clock()

    def draw_square_(self, x, y, col):
        pygame.draw.rect(self.screen,
                         col,
                         pygame.Rect(y * self.tileSize + 1,
                                     x * self.tileSize + 1,
                                     self.tileSize - 1,
                                     self.tileSize - 1))

    def draw(self):
        self.update_map(-1, -1)
        for x in range(len(self.map)):
            for y in range(len(self.map[0])):
                self.draw_square_(x, y, tileColor[self.map[x][y]])

    def draw_frame(self):
        self.draw()
        pygame.display.flip()

    def update_map(self, before, after):
        for agent in self.history:
            if len(agent) > after and len(agent) > before and before >= 0 and after >= 0:
                pos = literal_eval(agent[before])
                self.map[pos[0]][pos[1]] = 0
                pos2 = literal_eval(agent[after])
                self.map[pos2[0]][pos2[1]] = 1
    def run(self):
        i = -1
        tmp = -1
        while not self.done:
            self.clock.tick(100)
            self.draw_frame()
            if tmp!=i:
                print(i)
                tmp = i

            keys = pygame.key.get_pressed()
            if keys[K_LEFT]:
                if i > 0:
                    self.update_map(i, i-1)
                    i = i-1
                    time.sleep(0.05)
            if keys[K_RIGHT]:
                last = time.time()
                self.update_map(i, i+1)
                i = i+1
                time.sleep(0.05)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
        pygame.quit()


if __name__ == '__main__':
    s = Screen(16)
    s.run()
