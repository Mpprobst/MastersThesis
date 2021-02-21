"""
GA.py
Purpose: implements a genetic algorithm that generates levels that are optimized
to encourage a specific series of events.
Author: Michael Probst
"""
import timeit
from os import listdir
from os.path import isfile, join
from scavenger_env import ScavengerEnv
from astar_agent import AstarAgent

class GA():
    def __init__(self, sequence, verbose=False):
        self.current_generation = []        # array of level strings currently being evalutated
        self.sequence = sequence
        self.verbose = verbose
        training_path = "resources/training"
        files = [file for file in listdir(training_path) if isfile(join(training_path, file))]
        for file in files:
            #print(f'loading in {file}')
            f = open(training_path + "/" + file, "r")
            level_string = ""
            for line in f:
                level_string += line
            self.current_generation.append(level_string)
        self.train()


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
            #print(f'time to calculate move: {timeit.default_timer() - move_time}')
            move_time = timeit.default_timer()
            if self.verbose:
                print("")

        if self.verbose:
            print(f'GAME OVER. Player {"Win" if env.player_points > 0 else "Lose"} with {env.player_points} points.\nGame Events: {env.events} total gameplay time = {(timeit.default_timer() - start_time)}')
        return env.events

    # This fitness gets the sequence if it appears at all. Not halted by unfound events
    def fitness(self, events):
        goal_index = 0
        fit = 0
        for i in range(len(events)):
            #print(f'compare {self.sequence[goal_index]} to {events[i]} ')
            if self.sequence[goal_index] == events[i]:
                #print('hit')
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

    # go though all levels in the current generation and evaluate them
    def train(self):
        evaluations = []
        total_prob = 0
        for level in self.current_generation:
            events = self.eval_level(level)
            fitness = self.fitness(events)
            total_prob += fitness
            evaluations.append( (level, fitness) )

        # TODO: use weighted probability to choose 2 levels to compile into another
