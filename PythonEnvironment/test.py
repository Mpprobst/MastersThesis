"""
test.py
Purpose: Testing functioality of the scavenger environment
Author: Michael Probst
"""

import time
import scavenger_env as env
from random_agent import RandomAgent
from simple_agent import SimpleAgent
from astar_agent import AstarAgent

filename = "resources/training/level_1.txt"

f = open(filename, "r")
level_string = ""
for line in f:
    level_string += line
env = env.ScavengerEnv(level_string, True)

move_count = 0
points = 20

#agent = RandomAgent(points)
#agent = SimpleAgent(points)
agent = AstarAgent(points, env)

start_time = time.time()
move_time = start_time
while (not env.done and move_count < 50 and points > 0):
    print(f'points: {points}')
    env.print_env()
    move = agent.suggest_move(env)
    print(f'player move {move}')
    points += env.move(move)
    print(f'time to calculate move: {time.time() - move_time}')
    move_time = time.time()
    print("")

print(f'GAME OVER. Player {"Win" if points > 0 else "Lose"}\nGame Events: {env.events} total gameplay time = {(time.time() - start_time)}')
