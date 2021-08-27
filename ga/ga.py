from numpy import random, asarray, arange, ndarray, cumsum, concatenate, array
from pandas import DataFrame

from tqdm import trange, tqdm


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

    # n: task number
    # m: bot number
    def __init__(self, seed, simulation, popsize=100, maxepoc=100000, pcrossover=0.95, pmutation=0.1, pselection=0.2,
                 n=50, m=8):
        self.cache = {}
        self.popsize = popsize
        self.maxepoc = maxepoc
        self.pcrossover = pcrossover
        self.pmutation = pmutation
        self.pselection = pselection
        self.n = n
        self.m = m
        self.baseIndividual = arange(1, n + m)
        self.initialPopulation = self.__generatepopulation(seed)
        self.simulation = simulation

    def __fitness(self, chromosome):
        scheduling = self.chromosome_to_schedule(chromosome)
        key = str(scheduling)
        n = self.n
        m = self.m
        if key not in self.cache.keys():
            TT, TTC, BU = self.simulation(task_number=n, scheduling=scheduling, save=False, run=True)
            maxtest = max([len(scheduling[i]) for i in range(m)])
            Fx = maxtest / TT + n / TTC + BU
            self.cache[key] = (Fx, TT, TTC, BU)
            return Fx, TT, TTC, BU
        return self.cache[key]

    # chromosome_to_schedule maps a chromosome to a list of task ids (assigns task ids to the m robots)
    def chromosome_to_schedule(self, chromosome):
        if isinstance(chromosome, ndarray):
            chromosome = chromosome.tolist()
        n = self.n
        m = self.m
        m_minus_one = m - 1
        len_chromosome = len(chromosome)
        divisionpoints = list(range(n + 1, n + m, 1))
        last = 0
        k = 0
        schedule = [0] * m
        for i in range(len_chromosome):
            if chromosome[i] in divisionpoints:
                schedule[k] = chromosome[last:i]
                k += 1
                last = i + 1
            if k == m_minus_one:
                break
        schedule[k] = chromosome[last:]
        return schedule

    def __generatepopulation(self, seed):
        random.seed(seed)
        popsize = self.popsize
        return asarray([random.permutation(self.baseIndividual) for i in range(popsize)])

    # population here must be a popsize x (n+m) dataframe, where the last column represents the fitness value
    def __selection(self, population):
        n = self.n
        m = self.m
        popsize = self.popsize
        Fx_col = n + m - 1
        population = population.sort_values(Fx_col, ascending=False, ignore_index=True)
        t = int(popsize * self.pselection - 1)
        t_plus_one = t + 1
        elite = population.iloc[0:t_plus_one, 0:Fx_col]
        remaining = population.iloc[t_plus_one:, :]
        sumfitness = sum(remaining.loc[:, Fx_col])
        probabilities = [remaining.loc[i, Fx_col] / sumfitness for i in range(t_plus_one, popsize)]
        cumsums = cumsum(probabilities)
        len_remaining = len(remaining)
        len_cumsums = len(cumsums)
        selectedremaining = [0] * len_remaining
        remaining = remaining.iloc[:, 0:Fx_col]
        for i in range(len_remaining):
            r = random.rand()
            for j in range(len_cumsums):
                if r <= cumsums[j]:
                    selectedremaining[i] = j
                    break
        notelite = remaining.iloc[selectedremaining, 0:Fx_col]
        return (elite.append(notelite)).to_numpy()

    # parent1, parent2: np array
    def crossover_pair(self, parent1, parent2):
        chromlen = self.n + self.m - 1
        half = chromlen // 2
        a1 = random.randint(low=0, high=half)
        a2 = random.randint(low=half, high=chromlen)
        a2_plus_one = a2 + 1
        len_block = a2_plus_one - a1
        a2_minus_a1 = a2 - a1

        off1 = [0] * chromlen
        off2 = [0] * chromlen

        off1[0:len_block] = parent2[a1:a2_plus_one]
        off2[0:len_block] = parent1[a1:a2_plus_one]

        block1, block2 = off1[0:len_block], off2[0:len_block]

        k1 = 1
        k2 = 1
        for i in range(chromlen):
            if parent1[i] not in block1:
                off1[a2_minus_a1 + k1] = parent1[i]
                k1 += 1
            if parent2[i] not in block2:
                off2[a2_minus_a1 + k2] = parent2[i]
                k2 += 1

        return off1, off2

    # population: np array
    def crossover(self, population):
        len_population = len(population)
        newpopulation = [0] * len_population
        for i in range(0, len_population, 2):
            i_plus_one = i + 1
            newpopulation[i], newpopulation[i_plus_one] = self.crossover_pair(population[i, :],
                                                                              population[i_plus_one, :])
        return array(newpopulation)

    # population here is a len(elite) x (n+m-1) np array
    def mutation(self, population):
        chromlen = len(population[0])
        len_population = len(population)
        pmutation = self.pmutation
        for i in range(len_population):
            if random.rand() < pmutation:
                pos1 = random.randint(chromlen)
                pos2 = random.randint(chromlen)
                population[i, pos1], population[i, pos2] = population[i, pos2], population[i, pos1]
        return population

    def run(self):
        # eval the initial population
        fitness_and_metrics = None
        n = self.n
        m = self.m
        pcrossover = self.pcrossover
        pselection = self.pselection
        popsize = self.popsize
        maxepoc = self.maxepoc
        initialPopulation = self.initialPopulation

        fitness_and_metrics = asarray(list(map(self.__fitness, initialPopulation)))

        Fx_col = n + m - 1
        Fx_col_plus_one = Fx_col + 1
        Fx_col_plus_two = Fx_col + 2
        Fx_col_plus_three = Fx_col + 3
        df = DataFrame(initialPopulation)
        df[Fx_col] = fitness_and_metrics[:, 0]
        df[Fx_col_plus_one] = fitness_and_metrics[:, 1]
        df[Fx_col_plus_two] = fitness_and_metrics[:, 2]
        df[Fx_col_plus_three] = fitness_and_metrics[:, 3]

        # initial = df

        tmp = min(maxepoc, 1000)

        t = int(popsize * pselection - 1)
        t_plus_one = t + 1

        for i in tqdm(range(0, tmp), leave=False):
            # print("Generation: " + str(i))

            selected = self.__selection(df)

            elite = selected[0:t_plus_one]
            tmpcrossed = selected[t_plus_one:]
            if random.rand() < pcrossover:
                tmpcrossed = self.crossover(tmpcrossed)
            mutated = self.mutation(tmpcrossed)

            offspring = concatenate((elite, mutated))

            fitness_and_metrics = asarray(list(map(self.__fitness, offspring)))

            df = DataFrame(offspring)
            df[Fx_col] = fitness_and_metrics[:, 0]
            df[Fx_col_plus_one] = fitness_and_metrics[:, 1]
            df[Fx_col_plus_two] = fitness_and_metrics[:, 2]
            df[Fx_col_plus_three] = fitness_and_metrics[:, 3]

        if maxepoc >= 1000:
            self.pmutation = 0.5
            for i in tqdm(range(1000, 1500), leave=False):
                # print("Generation: " + str(i))

                selected = self.__selection(df)
                elite = selected[0:t_plus_one]
                tmpcrossed = selected[t_plus_one:]
                if random.rand() < pcrossover:
                    tmpcrossed = self.crossover(tmpcrossed)
                mutated = self.mutation(tmpcrossed)

                offspring = concatenate((elite, mutated))

                fitness_and_metrics = asarray(list(map(self.__fitness, offspring)))

                df = DataFrame(offspring)
                df[Fx_col] = fitness_and_metrics[:, 0]
                df[Fx_col_plus_one] = fitness_and_metrics[:, 1]
                df[Fx_col_plus_two] = fitness_and_metrics[:, 2]
                df[Fx_col_plus_three] = fitness_and_metrics[:, 3]

            current_best_Fx = max(df.loc[:, Fx_col])
            last_improvement_gen = -1

            for i in tqdm(range(1500, maxepoc), leave=False):
                # print("Generation: " + str(i))

                selected = self.__selection(df)
                elite = selected[0:t_plus_one]
                tmpcrossed = selected[t_plus_one:]
                if random.rand() < pcrossover:
                    tmpcrossed = self.crossover(tmpcrossed)
                mutated = self.mutation(tmpcrossed)

                offspring = concatenate((elite, mutated))

                fitness_and_metrics = asarray(list(map(self.__fitness, offspring)))

                df = DataFrame(offspring)
                df[Fx_col] = fitness_and_metrics[:, 0]
                df[Fx_col_plus_one] = fitness_and_metrics[:, 1]
                df[Fx_col_plus_two] = fitness_and_metrics[:, 2]
                df[Fx_col_plus_three] = fitness_and_metrics[:, 3]
                new_best_Fx = max(df.loc[:, Fx_col])
                imp = (new_best_Fx - current_best_Fx) / current_best_Fx
                # print("Fx % improvement: " + str(imp))
                # self.improvements.append(imp)
                if imp > 0.001:
                    last_improvement_gen = i
                    current_best_Fx = new_best_Fx
                if i - last_improvement_gen > 200:
                    best_individual = df.loc[df[Fx_col] == current_best_Fx].iloc[0]
                    return best_individual

        best_individual = df.loc[df[Fx_col] == current_best_Fx].iloc[0]
        return best_individual
