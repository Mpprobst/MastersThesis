"""
scavenger_env.py
Purpose: provides an environment replicating the Scavenger game for agents to play
Author: Michael Probst
"""

import numpy as np
from tiles import floor
from tiles import wall
from tiles import goal


MOVE_FACTORS = { 'U' : (1, 0),
                 'D' : (-1, 0),
                 'L' : (0, -1),
                 'R' : (0, 1) }

class Player():
    def __init__(self, start_pos):
        self.position = start_pos
        self.points = 20

class ScavengerEnv():
    # Given a file to base the level off of
    def __init__(self, file):
        self.level_width = 8    # number of columns in the level space (x dirextion)
        self.level_height = 8   # number of rows in the level space (y direction)
        self.level = []     # matrix containing level information
        self.player_points = 20
        self.player_position = (0, self.level_height-1)
        self.goal_position = (self.level_width-1, self.level_height-1)
        self.food_positions = []
        self.enemy_positions = []
        self.turn = 1       # subtracted by 1 each time the player moves. All enemies move when turn == 0

        f = open(file, "r")
        for line in f:
            level_row = []
            for char in line:
                tile = None
                if char == '\n':
                    continue

                if char == '-':
                    tile = floor.Floor('-')
                elif char == 'W':
                    tile = wall.Wall(char)
                elif char == 'F':
                    tile = floor.Floor('F')
                    self.food_positions.append((len(self.level), len(level_row)))
                elif char == 'E':
                    tile = floor.Floor('E')
                    self.enemy_positions.append((len(self.level), len(level_row)))
                elif char == 'G':
                    tile = goal.Goal('G')
                elif char == 'S':
                    tile = floor.Floor('-')
                    self.player_position = (len(self.level), len(level_row))

                if tile == None:
                    print(f'Tile type {char} undetermined')
                if tile != None:
                    level_row.append(tile)
            self.level.append(level_row)

        self.print_env()

    def print_env(self):
        for i in range(len(self.level)):
            row = self.level[i]
            row_string = ""
            for j in range(len(row)):
                if (i,j) == self.player_position:
                    row_string += 'A'
                row_string += row[j].get_icon()
            print(row_string)
    # Given a move from the agent, adjust the environment
    # Potential moves are : U, D, L, R for Up, Down, Left, and Right movement
    # Returns the score earned after the move
    def move(self, move):
        # get tile next to player
        move_factor = MOVE_FACTORS[move]
        next_pos = self.player_position + move_factor
        # ensure player stays in bounds of game
        if next_pos[0] >= self.level_width or next_pos[0] < 0:
            next_pos[0] = self.player_position[0]

        if next_pos[1] >= self.level_height or next_pos[1] < 0:
            next_pos[1] = self.player_position[1]

        next_tile = self.level[next_pos[0]][next_pos[1]]
        # interact with the tile
        points = -1
        # if move successful, change player position
        if next_tile.interact():
            if next_tile.has_food:
                points += 20
            player_position += next_pos
        player_points += points

        self.turn -= 1

        # enemy turn
        if self.turn == 0:
            for enemy in self.enemy_positions:
                print(enemy)


            self.turn = 2



        return points
