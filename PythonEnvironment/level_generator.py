"""
level_generator.py
Purpose: Use a genetic algorithm to generate levels based on a series of events
Author: Michael Probst
"""

import argparse
import timeit
from GA import GA

EVENT_CODES = { 'E' : 'Enemies Attack',
                'X' : 'Wall Destroyed' ,
                'F' : 'Food Collected',
                'L' : 'Player Death',
                'W' : 'Player Win'}

parser = argparse.ArgumentParser(description='Define the problem to solve.')
parser.add_argument('--gens', type=int, default = 1, help='Number of generations the genetic algorithm generates.')
parser.add_argument('--verbose', help='Visualize the environment.', action='store_true')
parser.add_argument('--AN', help='Use the author needs mutation strategy', action='store_true')
parser.add_argument('--RWU', help='Use the recude when used mutation strategy', action='store_true')
parser.add_argument('--MM', help='Use the meaningful mutation strategy', action='store_true')
parser.add_argument('--NB', help='Use the need based mutation strategy', action='store_true')

args = parser.parse_args()

done = False
events = []
print(f'Event Options: ')
for key in EVENT_CODES.keys():
    print(f'{key} -> {EVENT_CODES[key]}')

mutations = []
if args.AN:
    mutations.append("AN")
if args.RWU:
    mutations.append("RWU")
if args.MM:
    mutations.append("MM")
if args.NB:
    mutations.append("NB")


time = timeit.default_timer()
print(f'Complete your sequence with an end condition: W or L')
while not done:
    event = input(f'Please enter event #{len(events) + 1}: ')[0]
    if event in EVENT_CODES.keys():
        events.append(event)
    else:
        print(f'Invalid event. Please select an event from the following list:')
        for key in EVENT_CODES.keys():
            print(f'{key} -> {EVENT_CODES[key]}')

    if event == 'L' or event == 'W':
        done = True

print(f'desired events: {events}')
genetic_algorithm = GA(events, args.gens, mutations, args.verbose)
print(f'Total Runtime: {(timeit.default_timer() - time):.2f}')
