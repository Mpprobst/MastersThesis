"""
test.py
Purpose: Testing functioality of the scavenger environment
Author: Michael Probst
"""
import timeit
import scavenger_env as env
from random_agent import RandomAgent
from simple_agent import SimpleAgent
from astar_agent import AstarAgent

filename = "resources/training/level_8.txt"

f = open(filename, "r")
level_string = ""
for line in f:
    level_string += line
env = env.ScavengerEnv(level_string, True)

move_count = 0
points = 30

#agent = RandomAgent(points)
#agent = SimpleAgent(points)
agent = AstarAgent(points, env)

start_time = timeit.default_timer()
move_time = start_time
while (not env.done and move_count < 50):
    env.print_env()
    move = agent.suggest_move(env)
    print(f'player move {move}')
    env.move(move)
    #print(f'time to calculate move: {timeit.default_timer() - move_time}')
    move_time = timeit.default_timer()
    print("")

print(f'GAME OVER. Player {"Win" if env.player_points > 0 else "Lose"} with {env.player_points} points.\nGame Events: {env.events} total gameplay time = {(timeit.default_timer() - start_time)}')
