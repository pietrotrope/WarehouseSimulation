import numpy as np

from simulation.graph.node import Node


class Graph:

    def __init__(self, num_nodes=0):
        self.num_nodes = num_nodes
        self.num_edges = 0
        self.nodes = np.array([Node(i) for i in range(num_nodes)])
        self.adj = np.zeros((num_nodes, num_nodes), dtype=bool)

    def is_edge_defined(self, src, dest):
        return self.adj[src][dest]

    def add_edge(self, src, dest):
        if not self.is_edge_defined(src, dest):
            self.adj[src, dest] = True
            self.nodes[src].adj.append(self.nodes[dest])

        if not self.is_edge_defined(dest, src):
            if src != dest:
                self.adj[dest, src] = True
                self.nodes[dest].adj.append(self.nodes[src])

    def get_node(self, key):
        return self.nodes[key]
