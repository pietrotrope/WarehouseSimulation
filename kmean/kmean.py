from numpy.lib.shape_base import tile
from simulation.environment import Environment
from simulation.tile import Tile
import random
from sklearn.cluster import KMeans


import numpy as np
import matplotlib.pyplot as plt

env = Environment()

pods = []
for node in env.graph.nodes:
    if node.type == Tile.POD:
        pods.append(node)


for pod in pods:
    point = env.graph_to_raster[pod.id][0]
    plt.scatter(point[1], point[0])
plt.show()

tasks = {}
for i in range(500):
    tasks[i]= [pods[random.randrange(len(pods))]]

positions = []
for i in range(len(tasks)):
    positions.append(env.graph_to_raster[tasks[i][0].id][0])


kmeans = KMeans(n_clusters=2, random_state=0).fit(positions).labels_

clusters = {}
for i in range(len(positions)):
    if kmeans[i] in clusters:
        clusters[kmeans[i]].append(positions[i])
    else:
        clusters[kmeans[i]] = [positions[i]]

#print(clusters)





colors=["#0000FF", "#00FF00", "#FF0066"]

plt.xlim(0,50)
plt.ylim(0,28)

for cluster in clusters:
    color = colors.pop()
    for point in clusters[cluster]:
        plt.scatter(point[1], point[0], c=color)
plt.show()