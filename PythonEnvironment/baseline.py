"""
baseline.py
Author: Michael Probst
Purpose: gets the fitness of a bunch of random levels
"""
import csv
import sys
import timeit
from os import listdir
from os.path import isfile, join
from itertools import combinations
from scavenger_env import ScavengerEnv
from astar_agent import AstarAgent

# gets permutations of a sequence based on how long the permutations should be
# returns a list of (sequence, points)
def get_permutations(sequence, length):
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

def eval_level(level):
    env = ScavengerEnv(level, False)
    agent = AstarAgent(30, env)
    move_count = 0

    start_time = timeit.default_timer()
    move_time = start_time
    while (not env.done and move_count < 50):
        move = agent.suggest_move(env)
        env.move(move)
        if timeit.default_timer() - start_time > TIME_CUTOFF:
            break

    return env.events

# This fitness gets the sequence if it appears at all. Not halted by unfound events
def fitness(events):
    if len(events) == 0:
        return 0

    if events[len(events)-1] == 'L':
        return 0

    # determine the longest matching sequence
    # start with length of the desired sequence
    fit = 0
    max_fit = len(sequence) * 2 - 1
    for length in range(len(sequence), 0, -1):
        # if fitness is nonzero, the longest sequence has been found
        if fit > 0:
            break

        perms = get_permutations(events, length)
        # prevent two of the same sequences adding to the score when they
        # have the same sequence, but differ in points
        used = []   # list of sequeces that have been used to add score
        for goal, gscore in permutations:
            for perm, pscore in perms:
                if goal == perm and perm not in used:
                    score = gscore
                    if pscore < score:
                        score = pscore
                    used.append(perm)
                    fit += score

                    #print(f'{perm} earns {score} points')
                    break

    # if agent triggered excess events, penalize
    if fit > max_fit:
        fit = max_fit
        if events != sequence:
            fit -= 0.25 * max_fit
    if len(events) > len(sequence):
        fit -= (0.5 * (len(events) - len(sequence))) #consider lowering this
    if fit < 0:
        fit = 0
    fit /= max_fit

    return fit

"""
----------------------MAIN-----------------------
"""

TRAINING_DIR = "resources/baseline"
TIME_CUTOFF = 10
outfile = f'{TRAINING_DIR}/_{sys.argv[1]}_baseline.csv'
sequence = list(sys.argv[1])
print(sequence)
permutations = []
for length in range(len(sequence), 0, -1):
    for perm in get_permutations(sequence, length):
        #print(f'{perm[0]} gets {perm[1]} points')
        permutations.append(perm)

# get all files in the trainig dir
files = [file for file in listdir(TRAINING_DIR)]
levels = []
for file in files:
    if not file.endswith(".txt"):
        continue
    f = open(TRAINING_DIR + "/" + file, "r")
    level_string = ""
    for line in f:
        level_string += line
    levels.append(level_string)

with open(outfile, 'w', newline = '') as csvfile:
    writer = csv.writer(csvfile, delimiter = ',')
    level_count = 0
    avg_fit = 0
    for i in range(len(levels)):
        if i % 100 == 0:
            print(f'level {i}')
        level = levels[i]
        events = eval_level(level)
        fit_val = fitness(events)
        #print(f'compare {sequence} to {events}. {(fit_val * 100):.2f}% fit')
        writer.writerow([fit_val])

        # levels with 0 fitness are impossible and should be removed from evaluation
        if fit_val > 0:
            level_count += 1
            avg_fit += fit_val

    avg_fit /= (level_count-1)
    print(f'total avg fit: {(avg_fit*100):.2f}%')
