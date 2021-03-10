"""
GA.py
Purpose: implements a genetic algorithm that generates levels that are optimized
to encourage a specific series of events.
Author: Michael Probst
"""
import csv
import timeit
import random
from os import listdir
from os.path import isfile, join
from itertools import combinations
from scavenger_env import ScavengerEnv
from astar_agent import AstarAgent

OUTPUT_DIR = "resources/output/"
TIME_CUTOFF = 10
MUTATION_PROB = 0.1

class GA():
    def __init__(self, sequence, num_generations, verbose=False):
        self.current_generation = []        # array of level strings currently being evalutated
        self.sequence = sequence
        self.verbose = verbose
        training_path = "resources/training"
        self.tiles = [ ('-', 10), ('F', 1), ('3', 1), ('E', 1) ]
        for i in range(len(sequence)):
            for j in range(len(self.tiles)):
                if sequence[i] == self.tiles[j][0]:
                    self.tiles[j] = (self.tiles[j][0], self.tiles[j][1] + 1)
                elif sequence[i] == 'X':
                    self.tiles[2] = (self.tiles[2][0], self.tiles[2][1] + 1)
                    break
        print(f'\nTile mutation probabilities:')
        total_weight = sum(weight for _, weight in self.tiles)
        for tile in self.tiles:
            print(f'P(\'{tile[0]}\')={(tile[1]/total_weight):.2f}')

        self.current_generation = self.get_generation_files(training_path)
        self.permutations = []
        for length in range(len(self.sequence), 0, -1):
            for perm in self.get_permutations(self.sequence, length):
                #print(f'{perm[0]} gets {perm[1]} points')
                self.permutations.append(perm)

        # Generate levels
        outfile = "resources/output/results.csv"
        with open(outfile, 'w', newline = '') as csvfile:
            writer = csv.writer(csvfile, delimiter = ',')
            for i in range(num_generations):
                gen_time = timeit.default_timer()
                print(f'\nGENERATION {i}')
                fit_val = self.train()
                writer.writerow([i, fit_val])
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
        env = ScavengerEnv(level, False)
        agent = AstarAgent(30, env)
        move_count = 0

        start_time = timeit.default_timer()
        move_time = start_time
        while (not env.done and move_count < 50):
            move = agent.suggest_move(env)
            env.move(move)
            if timeit.default_timer() - start_time > TIME_CUTOFF:
                #print("Aborting due to time constraint")
                break

        return env.events

    # gets permutations of a sequence based on how long the permutations should be
    # returns a list of (sequence, points)
    def get_permutations(self, sequence, length):
        perms = []
        points = []
        result = []
        for positions in combinations(range(len(sequence)), length):
            p = []
            score = length
            for i in positions:
                p.append(sequence[i])
                    # assign points for correct events and additional points for proper ordering
                if (i + 1) in positions:
                    score += 1
            perm = (p, score)
            if perm not in perms:
                perms.append(perm)
        # Sort based score, ensures best fit is counted if it exists
        perms = sorted(perms, reverse=True, key=lambda tup: tup[1])
        return perms

    # This fitness gets the sequence if it appears at all. Not halted by unfound events
    def fitness(self, events):
        if len(events) == 0:
            return 0

        if events[len(events)-1] == 'L':
            return 0

        # determine the longest matching sequence
        # start with length of the desired sequence
        fit = 0
        max_fit = len(self.sequence) * 2 - 1
        for length in range(len(self.sequence), 0, -1):
            # if fitness is nonzero, the longest sequence has been found
            if fit > 0:
                break

            perms = self.get_permutations(events, length)
            # prevent two of the same sequences adding to the score when they
            # have the same sequence, but differ in points
            used = []   # list of sequeces that have been used to add score
            for goal, gscore in self.permutations:
                for perm, pscore in perms:
                    if goal == perm and perm not in used:
                        score = gscore
                        if pscore < score:
                            score = pscore
                        fit += score
                        used.append(perm)
                        #print(f'{perm} earns {score} points')
                        break

        # if agent triggered excess events, penalize
        if len(events) > len(self.sequence):
            fit -= (0.5 * (len(events) - len(self.sequence))) #consider lowering this
        if fit < 0:
            fit = 0
        fit /= max_fit

        # see which events occured too many times and reduce prob
        excess_events = events.copy()
        seq = self.sequence.copy()
        prev_len = 0
        while len(seq) > 0 and len(seq) != prev_len:
            prev_len = len(seq)
            for s in seq:
                if s in excess_events:
                    excess_events.remove(s)
                    seq.remove(s)
                    break

        for event in excess_events:
            for i in range(len(self.tiles)):
                if self.tiles[i][0] == event:
                    new_prob = self.tiles[i][1] - 0.1
                    if new_prob < 0.1:
                        new_prob = 0.1
                    self.tiles[i] = ( self.tiles[i][0], new_prob )

        # see which events didnt occur enough and make them more likely
        diff_events = self.sequence.copy()
        seq = events.copy()
        prev_len = 0
        while len(seq) > 0 and len(seq) != prev_len:
            prev_len = len(seq)
            for s in seq:
                if s in diff_events:
                    diff_events.remove(s)
                    seq.remove(s)
                    break

        for event in diff_events:
            for i in range(len(self.tiles)):
                if self.tiles[i][0] == event:
                    new_prob = self.tiles[i][1] + 0.1
                    self.tiles[i] = ( self.tiles[i][0], new_prob )

        return fit

    # return an item at random based on a weighted probablity.
    def get_weighted_random(self, item):
        total_prob = sum(weight for _, weight in item)
        rand = random.uniform(0, total_prob)

        for i in range(len(item)):
            if rand < item[i][1]:
                return item[i]
            else:
                rand -= item[i][1]

        return item[0]

    # takes 2 levels, slices them at a random point, and swaps them. Returns both levels
    def crossover(self, evaluations):
        level1 = self.get_weighted_random(evaluations)
        evaluations.remove(level1)
        level2 = self.get_weighted_random(evaluations)
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
                if random.random() < MUTATION_PROB:

                    #tile = self.get_weighted_random(self.tiles)[0]

                    # reduce chances of tile turning into itself
                    tiles = self.tiles.copy()
                    for t in tiles:
                        if t[0] == level[i]:
                            t = ( t[0], t[1]/2 )
                            break
                    tile = self.get_weighted_random(tiles)[0]
                    """
                    # when a tile is picked, reduce its probability a little
                    for t in range(len(self.tiles)):
                        modifier = 0.1
                        if self.tiles[t][0] == '-':
                            modifier = 0.35
                        if self.tiles[t][0] in self.sequence:
                            modifier += 0.1
                        if self.tiles[t][0] == tile:
                            modifier = -0.25
                        new_weight = self.tiles[t][1] + modifier
                        if new_weight < 0:
                            new_weight = 0.1
                        self.tiles[t] = (self.tiles[t][0], new_weight)
                    """
                    # print(f'mutate {level[i]} into {tile}')
                    mutated += tile
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
            #print(f'level {level_count}')
            print(f'compare {self.sequence} to {events}. {(fitness * 100):.2f}% fit')
            #print(f'{level}')
            evaluations.append( (level, fitness) )
            level_count += 1
            avg_fit += fitness

        avg_fit /= (level_count-1)

        total_weight = sum(weight for _, weight in self.tiles)
        mut_prob_string = ""
        for t in self.tiles:
            mut_prob_string += f'P(\'{t[0]}\') = {(t[1]/total_weight):.2f}, '

        print(f'EVAL AVG FITNESS = {avg_fit*100:.2f}% mutation probs: {mut_prob_string}')
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
        return avg_fit

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
