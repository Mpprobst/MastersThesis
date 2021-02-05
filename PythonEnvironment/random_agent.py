"""
random_agent.py
Purpose: implements an agent that takes random actions
Author: Michael Probst
"""
import random

MOVES = ['U', 'D', 'L', 'R']

class RandomAgent():
    def __init__(self, start_score):
        self.reward = start_score

    def suggest_move(self, env):
        tiles = env.get_adjacent_tiles()
        tile_string = ""
        for t in tiles:
            tile_string += t.get_icon()

        print(f'adjacent tiles: {tile_string}')

        return random.choice(MOVES)
