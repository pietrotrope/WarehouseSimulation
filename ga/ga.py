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

    #n: task number
    #m: bot number
    def __init__(self, seed, simulation, popsize=100, maxepoc=100000, pcrossover=0.95, pmutation=0.1, pselection=0.2,
                 n=50,
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
        self.simulation = simulation

    def __fitness(self, chromosome):
        scheduling = self.chromosome_to_schedule(chromosome)
        TT, TTC, BU = self.simulation(task_number=self.n, scheduling=scheduling)
        maxtest = max([len(scheduling[i]) for i in range(self.m)])
        totaltest = self.n
        Fx = maxtest / TT + totaltest / TTC + BU

        return Fx, TT, TTC, BU

    # chromosome_to_schedule maps a chromosome to a list of task ids (assigns task ids to the m robots)
    def chromosome_to_schedule(self, chromosome):
        if isinstance(chromosome, np.ndarray):
            chromosome = chromosome.tolist()
        divisionpoints = list(range(self.n + 1, self.n + self.m, 1))
        last = 0
        k = 0
        schedule = [0] * self.m
        for i in range(len(chromosome)):
            if chromosome[i] in divisionpoints:
                schedule[k] = chromosome[last:i]
                k += 1
                last = i + 1
            if k == self.m - 1:
                break
        schedule[k] = chromosome[last:]
        return schedule

    def __generatepopulation(self, seed):
        np.random.seed(seed)
        return np.asarray([np.random.permutation(self.baseIndividual) for i in range(self.popsize)])

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

        k1 = 1
        k2 = 1
        for i in range(chromlen):
            if parent1[i] not in off1[0:(a2 - a1 + 1)]:
                off1[a2 - a1 + k1] = parent1[i]
                k1 += 1
            if parent2[i] not in off2[0:(a2 - a1 + 1)]:
                off2[a2 - a1 + k2] = parent2[i]
                k2 += 1

        return off1, off2

    # population: np array
    def crossover(self, population):
        newpopulation = [0] * len(population)
        for i in range(0, len(population), 2):
            off1, off2 = self.crossover_pair(population[i, :], population[i + 1, :])
            newpopulation[i] = off1
            newpopulation[i + 1] = off2
        return np.array(newpopulation)

    # population here is a len(elite) x (n+m-1) np array
    def mutation(self, population):
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
        fitness_and_metrics = np.asarray(list(map(self.__fitness, self.initialPopulation)))
        Fx = fitness_and_metrics[:, 0]
        TT = fitness_and_metrics[:, 1]
        TTC = fitness_and_metrics[:, 2]
        BU = fitness_and_metrics[:, 3]

        lastcol = self.n + self.m - 1
        df = pd.DataFrame(self.initialPopulation)
        df[lastcol] = Fx
        df[lastcol + 1] = TT
        df[lastcol + 2] = TTC
        df[lastcol + 3] = BU
        #initial = df

        for i in range(0, self.maxepoc):
            print("Generation: "+str(i))
            if i >= 1000:
                self.pmutation = 0.5

            selected = self.__selection(df)
            t = int(self.popsize * self.pselection - 1)
            elite = selected[0:t + 1]
            tmpcrossed = selected[t + 1:]
            if np.random.rand() < self.pcrossover:
                tmpcrossed = self.crossover(tmpcrossed)
            mutated = self.mutation(tmpcrossed)

            offspring = np.concatenate((elite, mutated))
            fitness_and_metrics = np.asarray(list(map(self.__fitness, offspring)))
            Fx = fitness_and_metrics[:, 0]
            TT = fitness_and_metrics[:, 1]
            TTC = fitness_and_metrics[:, 2]
            BU = fitness_and_metrics[:, 3]
            df = pd.DataFrame(offspring)
            df[lastcol] = Fx
            df[lastcol + 1] = TT
            df[lastcol + 2] = TTC
            df[lastcol + 3] = BU
        return df
