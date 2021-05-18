import numpy as np
import pandas as pd


class GA:
    n: int
    m: int
    popsize: int
    maxepoc: int

    # Variables:
    # n: number of tasks
    # m: number of robots
    # popsize: size of the population
    # maxepoc: max number of generations
    # pcrossover: crossover rate
    # pmutation: mutation rate
    # pselection: selection rate

    def __init__(self, seed, fitness, popsize=100, maxepoc=100000, pcrossover=0.95, pmutation=0.1, pselection=0.2, n=50,
                 m=8):
        self.popsize = popsize
        self.maxepoc = maxepoc
        self.pcrossover = pcrossover
        self.pmutation = pmutation
        self.pselection = pselection
        self.n = n
        self.m = m
        self.baseIndividual = np.arange(1, n + m)
        self.initialPopulation = self.__generatepopulation(seed)
        self.fitness = fitness

    def __generatepopulation(self, seed):
        np.random.seed(seed)
        return np.asarray([np.random.permutation(self.baseIndividual).tolist() for i in range(self.popsize)])

    # population here must be a popsize x (n+m) dataframe, where the last column represents the fitness value
    def __selection(self, population):
        #df[lastcol] = np.arange(tmp.popsize).tolist() how to add a column
        lastcol = self.n + self.m - 1
        #population = population[np.argsort(-population[:, lastcol + 1])]
        population = population.sort_values(lastcol+1, ascending=False, ignore_index=True)
        t = int(self.popsize * self.pselection - 1)
        elite = population.iloc[0:t+1, 0:lastcol]
        notelite = [0] * (self.popsize - t)
        remaining = population.iloc[t + 1:, :]
        sumfitness = sum(remaining.loc[:, lastcol])
        probabilities = [remaining.loc[i, lastcol] / sumfitness for i in range(t + 1, self.popsize)]
        cumsum = np.cumsum(probabilities)
        selectedremaining = [0]*len(remaining)
        remaining = remaining.iloc[:, 0:lastcol]
        for i in range(len(remaining)):
            r = np.random.rand()
            for j in range(len(cumsum)):
                if r <= cumsum[j]:
                    selectedremaining[i] = j
                    break
        notelite = remaining.iloc[selectedremaining, 0:lastcol]
        newpopulation = ((elite.append(notelite)).to_numpy())
        return newpopulation
    #def crossover(self):
    #def mutation(self):
#   def evaluate(self):

#   def run(self):

#      for i in range(0,self.maxepoc):
#         if i >= 1000:
#            self.pmutation = 0.5
