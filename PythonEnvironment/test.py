"""
test.py
Purpose: Testing functioality of the scavenger environment
Author: Michael Probst
"""

import scavenger_env as env
from random_agent import RandomAgent

filename = "resources/training/level_5.txt"
env = env.ScavengerEnv(filename)

move_count = 0
points = 20

agent = RandomAgent(points)
while (not env.done and move_count < 50 and points > 0):
    move = agent.suggest_move(env)
    points += env.move(move)
    print(f'moved {move}. points: {points}')
    env.print_env()
