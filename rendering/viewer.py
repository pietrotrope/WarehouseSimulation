from ast import literal_eval
from numpy.lib.function_base import append
from numpy.lib.histograms import _histogram_bin_edges_dispatcher
import pygame
from pygame.constants import K_LEFT, K_RIGHT
from simulation.tile import tileColor
import numpy as np
import pandas as pd
from csv import reader
import time
import random


class Screen:

    def __init__(self, tile_size, screen_width=800, screen_height=600, name="out.csv"):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.done = False
        self.tileSize = tile_size
        self.map = np.array(pd.read_csv('map.csv', header=None))
        self.history = []
        with open(name, 'r') as read_obj:
            csv_reader = reader(read_obj)
            for row in csv_reader:
                self.history.append(row)
        self.color = []
        for i in range(len(self.history)):
            self.color.append([random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255)])
        self.clock = pygame.time.Clock()

    def draw_square_(self, x, y, col):
        pygame.draw.rect(self.screen,
                         col,
                         pygame.Rect(y * self.tileSize + 1,
                                     x * self.tileSize + 1,
                                     self.tileSize - 1,
                                     self.tileSize - 1))

    def draw(self, time):
        for x in range(len(self.map)):
            for y in range(len(self.map[0])):
                if self.map[x][y] == 1:
                    for i in range(len(self.history)):
                        if len(self.history[i]) > time >= 0 and literal_eval(self.history[i][time]) == (x, y):
                            self.draw_square_(x, y, self.color[i])
                else:
                    self.draw_square_(x, y, tileColor[self.map[x][y]])

    def draw_frame(self, time):
        self.draw(time)
        pygame.display.flip()

    def update_map(self, before, after):
        for agent in self.history:
            if len(agent) > after >= 0 and len(agent) > before >= 0:
                pos = literal_eval(agent[before])
                self.map[pos[0]][pos[1]] = 0
        new_pos = []
        for agent in self.history:
            if len(agent) > after >= 0 and len(agent) > before >= 0:
                pos2 = literal_eval(agent[after])
                new_pos.append(pos2)
                self.map[pos2[0]][pos2[1]] = 1
        print(new_pos)

    def run(self):
        i = -1
        tmp = -1
        while not self.done:
            self.clock.tick(100)
            self.draw_frame(i)
            if tmp != i:
                print(i)
                tmp = i

            keys = pygame.key.get_pressed()
            if keys[K_LEFT]:
                if i > 0:
                    self.update_map(i, i - 1)
                    i = i - 1
                    time.sleep(0.05)
            if keys[K_RIGHT]:
                last = time.time()
                self.update_map(i, i + 1)
                i = i + 1
                time.sleep(0.05)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
        pygame.quit()


if __name__ == '__main__':
    s = Screen(16)
    s.run()
