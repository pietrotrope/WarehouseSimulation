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
        lastcol = self.n + self.m - 1
        population = population.sort_values(lastcol, ascending=False, ignore_index=True)
        t = int(self.popsize * self.pselection - 1)
        elite = population.iloc[0:t + 1, 0:lastcol]
        remaining = population.iloc[t + 1:, :]
        sumfitness = sum(remaining.loc[:, lastcol])
        probabilities = [remaining.loc[i, lastcol] / sumfitness for i in range(t + 1, self.popsize)]
        cumsum = np.cumsum(probabilities)
        selectedremaining = [0] * len(remaining)
        remaining = remaining.iloc[:, 0:lastcol]
        for i in range(len(remaining)):
            r = np.random.rand()
            for j in range(len(cumsum)):
                if r <= cumsum[j]:
                    selectedremaining[i] = j
                    break
        notelite = remaining.iloc[selectedremaining, 0:lastcol]
        return (elite.append(notelite)).to_numpy()

    # parent1, parent2: np array
    def crossover_pair(self, parent1, parent2):
        chromlen = self.n + self.m - 1
        half = int(chromlen / 2)
        a1 = np.random.randint(low=0, high=half)
        a2 = np.random.randint(low=half, high=chromlen)

        off1 = [0] * chromlen
        off2 = [0] * chromlen

        off1[0:(a2 - a1 + 1)] = parent2[a1:a2 + 1]
        off2[0:(a2 - a1 + 1)] = parent1[a1:a2 + 1]

        k = 1
        for i in range(chromlen):
            if parent1[i] not in off1[0:(a2 - a1 + 1)]:
                off1[a2 - a1 + k] = parent1[i]
                k = k + 1
        k = 1
        for i in range(chromlen):
            if parent2[i] not in off2[0:(a2 - a1 + 1)]:
                off2[a2 - a1 + k] = parent2[i]
                k = k + 1
        return np.array([off1, off2])

    # population: np array
    def crossover(self, population):
        newpopulation = [0] * len(population)
        for i in range(0, len(population), 2):
            pair = self.crossover_pair(population[i, :], population[i + 1, :])
            newpopulation[i] = pair[0]
            newpopulation[i + 1] = pair[1]
        return np.array(newpopulation)

    # population here is a len(elite) x (n+m-1) np array
    def mutation(self, population):
        df = pd.DataFrame(population)
        chromlen = len(population[0])
        for i in range(len(population)):
            r = np.random.rand()
            if r < self.pmutation:
                pos1 = np.random.randint(chromlen)
                pos2 = np.random.randint(chromlen)
                tmp = population[i, pos1]
                population[i, pos1] = population[i, pos2]
                population[i, pos2] = tmp
        return population

    def run(self):
        # eval the initial population
        # Fx = self.fitness(self.initialPopulation)
        Fx = []
        lastcol = self.n + self.m - 1
        df = pd.DataFrame(self.initialPopulation)
        df[lastcol] = Fx

        for i in range(0, self.maxepoc):
            if i >= 1000:
                self.pmutation = 0.5

            selected = self.__selection(df)
            t = int(self.popsize * self.pselection - 1)
            elite = selected[0:t + 1]
            tmpcrossed = selected[t + 1:]
            if np.random.rand() < self.pcrossover:
                tmpcrossed = self.crossover(tmpcrossed)
            mutated = self.mutation(tmpcrossed)

            # if np.random.rand() < self.pmutation:
            # tmpmutated = self.mutation(tmpcrossed)

            offspring = np.concatenate((elite, mutated))
            # Fx = self.fitness(offspring)
            Fx = []
            df = pd.DataFrame(offspring)
            df[lastcol] = Fx
        return df
