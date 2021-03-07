"""
GA.py
Purpose: implements a genetic algorithm that generates levels that are optimized
to encourage a specific series of events.
Author: Michael Probst
"""
import timeit
import random
from os import listdir
from os.path import isfile, join
from scavenger_env import ScavengerEnv
from astar_agent import AstarAgent

OUTPUT_DIR = "resources/output/"
TILES = ['3', '-', '-', '-', 'E', 'F']
TIME_CUTOFF = 15

class GA():
    def __init__(self, sequence, num_generations, verbose=False):
        self.current_generation = []        # array of level strings currently being evalutated
        self.sequence = sequence
        self.verbose = verbose
        training_path = "resources/training"
        self.current_generation = self.get_generation_files(training_path)

        for i in range(num_generations):
            gen_time = timeit.default_timer()
            print(f'\nGENERATION {i}')
            self.train()
            print(f'Generation Time: {(timeit.default_timer() - gen_time):.2f}')
        self.test_generated_levels()


    def get_generation_files(self, path):
        generation = []
        files = [file for file in listdir(path)]
        files.sort()
        for file in files:
            if not file.endswith(".txt"):
                continue
            f = open(path + "/" + file, "r")
            level_string = ""
            for line in f:
                level_string += line
            generation.append(level_string)
        return generation

    def eval_level(self, level):
        env = ScavengerEnv(level, self.verbose)
        agent = AstarAgent(30, env)
        move_count = 0

        start_time = timeit.default_timer()
        move_time = start_time
        while (not env.done and move_count < 50):
            if self.verbose:
                env.print_env()
            move = agent.suggest_move(env)
            if self.verbose:
                print(f'player move {move}')
            env.move(move)
            if self.verbose:
                print("")
            if timeit.default_timer() - start_time > TIME_CUTOFF:
                #print("Aborting due to time constraint")
                break

        #if self.verbose:
        #    print(f'GAME OVER. Player {"Win" if env.player_points > 0 else "Lose"} with {env.player_points} points.\nGame Events: {env.events} total gameplay time = {(timeit.default_timer() - start_time)}')
        return env.events

    # This fitness gets the sequence if it appears at all. Not halted by unfound events
    def fitness(self, events):
        if len(events) == 0:
            return 0
        """
        if events[len(events)-1] != 'W':
            if events[len(events)-1] != 'L':
                return 0
            return 0
        """
        goal_index = 0
        fit = 0
        for i in range(len(events)):
            if self.sequence[goal_index] == events[i]:
                fit += 1/len(self.sequence)
                goal_index += 1
                if goal_index >= len(self.sequence):
                    break

        # TODO: subtract fitness if the sequence was carried out, but there were extra events
        if goal_index == len(self.sequence):
            fit -= (0.15 * (len(events) - len(self.sequence)))
            if fit < 0.25:
                fit = 0.25

        print(f'compare {self.sequence} to {events}. {(fit * 100):.2f}% fit')

        return fit

    # return a level at random based on a weighted probablity.
    def get_random_level(self, evals):
        total_prob = sum(fit for _, fit in evals)
        rand = random.uniform(0, total_prob)
        for i in range(len(evals)):
            if evals[i][1] < rand:
                return evals[i]
            else:
                rand -= evals[i][1]

        return evals[0]

    # takes 2 levels, slices them at a random point, and swaps them. Returns both levels
    def crossover(self, evaluations):
        level1 = self.get_random_level(evaluations)
        evaluations.remove(level1)
        level2 = self.get_random_level(evaluations)
        evaluations.append(level1)
        level1 = level1[0]
        level2 = level2[0]
        # choose crossover point and swap data
        point = random.randint(0, len(level1))
        top_slice = slice(0, point, 1)
        bot_slice = slice(point, len(level1), 1)
        cross1 = level1[top_slice] + level2[bot_slice]
        cross2 = level2[top_slice] + level1[bot_slice]
        return (cross1, cross2)

    def mutate(self, level):
        mutated = ""
        for i in range(0, len(level)):
            if level[i] == '\n' or level[i] == 'S' or level[i] == 'G':
                mutated += level[i]
            else:
                if random.random() < 0.02:
                    mutated += random.choice(TILES)
                else:
                    mutated += level[i]
        return mutated

    # go though all levels in the current generation and evaluate them
    def train(self):
        evaluations = []
        level_count = 1
        avg_fit = 0
        eval_time = timeit.default_timer()
        for level in self.current_generation:
            events = self.eval_level(level)
            fitness = self.fitness(events)
            evaluations.append( (level, fitness) )
            level_count += 1
            avg_fit += fitness

        avg_fit /= level_count
        print(f'EVAL AVG FITNESS = {avg_fit*100:.2f}%')
        avg_fit = 0
        next_generation = []
        # apply crossover to levels. TODO: Should the split be skewed toward the better fit level?
        for i in range((int(len(evaluations)/2))):
            crossover = self.crossover(evaluations)
            next_generation.append(crossover[0])
            next_generation.append(crossover[1])
        #print(f'Evaluation time: {(timeit.default_timer() - eval_time):.2f}\n')
        # mutate the levels
        for i in range(len(next_generation)):
            next_generation[i] = self.mutate(next_generation[i])
        self.current_generation = next_generation

    # sort the final generation into the top 3 fitness to send to Unity
    def test_generated_levels(self):
        print("\nTESTING GENERATED LEVELS")
        avg_fit = 0
        evals = []    # (level_index, fitness)
        for i in range(len(self.current_generation)):
            gen_events = self.eval_level(self.current_generation[i])
            gen_fit = self.fitness(gen_events)
            evals.append( (i, gen_fit) )
            avg_fit += gen_fit
        avg_fit /= len(self.current_generation)
        print(f'TRAINED AVG FITNESS = {avg_fit*100:.2f}%')

        evals = sorted(evals, reverse=True, key=lambda tup: tup[1])
        # at this point, only save the top 3 files
        for i in range(0,3):
            print(f'Saving level {evals[i][0]} with fitness {(evals[i][1]*100):.2f}%')
            filename = f'{OUTPUT_DIR}generated_{i}.txt'
            file = open(filename, "w")
            file.write(self.current_generation[evals[i][0]])
            file.close()
