from ga import GA
import time


def fitness(schedule):
    TT = max([sum(schedule[i]) for i in range(len(schedule))]) + 1
    TTC = min([sum(schedule[i]) for i in range(len(schedule))]) + 1
    BU = sum([sum(schedule[i]) for i in range(len(schedule))]) / 10 + 1
    return TT, TTC, BU


def main():
    t = time.time()
    ga = GA(0, fitness, popsize=100, maxepoc=100, n=50, m=8)
    initial, last = ga.run()
    elapsed = time.time() - t
    print("Initial population|Fx")
    print(initial)
    print("Last population|Fx")
    print(last)
    print("Elapsed " + str(elapsed))


if __name__ == "__main__":
    main()
