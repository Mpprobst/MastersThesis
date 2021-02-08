"""
simple_agent.py
Purpose: implements an agent that moves up until it hits the top of the board,
then it will move right until it has won
Author: Michael Probst
"""
import random

MOVES = ['U', 'D', 'L', 'R']

class SimpleAgent():
    def __init__(self, start_score):
        self.reward = start_score

    def suggest_move(self, env):
        if env.player_position[0] > 0:
            return 'U'

        return 'R'
