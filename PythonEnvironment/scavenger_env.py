"""
scavenger_env.py
Purpose: provides an environment replicating the Scavenger game for agents to play
Author: Michael Probst
"""

import numpy as np
from tiles import floor
from tiles import wall
from tiles import goal


MOVE_FACTORS = { 'U' : (-1, 0),
                 'D' : (1, 0),
                 'L' : (0, -1),
                 'R' : (0, 1) }

EVENT_CODES = { 'Enemies Attack' : 'E',
                'Wall Destroyed' : 'W',
                'Food Collected' : 'F',
                'Player Death' : 'L',
                'Player Win' : 'V' }

class Player():
    def __init__(self, start_pos):
        self.position = start_pos
        self.points = 20

class ScavengerEnv():
    # Given a file to base the level off of
    def __init__(self, file):
        self.level_width = 8    # number of columns in the level space (x dirextion)
        self.level_height = 8   # number of rows in the level space (y direction)
        self.level = []     # matrix containing level information. SHOULD BE INDEXED (y, x)
        self.player_points = 20
        self.player_position = (self.level_height-1, 0)
        self.goal_position = (0, self.level_width-1)
        self.food_positions = []
        self.enemy_positions = []
        self.turn = 1       # subtracted by 1 each time the player moves. All enemies move when turn == 0
        self.done = False
        self.events = []

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
                    self.goal_position = (len(self.level), len(level_row))
                elif char == 'S':
                    tile = floor.Floor('-')
                    self.player_position = (len(self.level), len(level_row))

                if tile == None:
                    print(f'Tile type {char} undetermined')
                if tile != None:
                    level_row.append(tile)
            self.level.append(level_row)

        #self.print_env()

    def print_env(self):
        print(f'player pos: ({self.player_position[1]}, {self.player_position[0]})')
        for i in range(len(self.level)):
            row = self.level[i]
            row_string = ""
            for j in range(len(row)):
                if (i,j) == self.player_position:
                    row_string += 'A'
                else:
                    row_string += row[j].get_icon()
            print(row_string)
    # Given a move from the agent, adjust the environment
    # Potential moves are : U, D, L, R for Up, Down, Left, and Right movement
    # Returns the score earned after the move
    def move(self, move):
        # get tile next to player
        move_factor = MOVE_FACTORS[move]
        # ensure player stays in bounds of game
        x = self.player_position[0] + move_factor[0]
        y = self.player_position[1] + move_factor[1]
        if x >= self.level_width or x < 0:
            x = self.player_position[0]

        if y >= self.level_height or y < 0:
            y = self.player_position[1]
        next_pos = (x,y)
        next_tile = self.level[next_pos[0]][next_pos[1]]
        points = -1

        # check if the next tile is a wall and if it has been destroyed after interacting with it
        is_wall = isinstance(next_tile, wall.Wall)
        if is_wall:
            is_wall = next_tile.health >= 0

        # if move successful, change player position
        if next_tile.interact():
            if is_wall:
                if next_tile.health < 0:
                    self.broadcast_event('Wall Destroyed')

            if next_tile.has_food:
                next_tile.pickup_food()
                self.broadcast_event('Food Collected')
                points += 20
            self.player_position = next_pos

        print(f'{self.player_position} == {self.goal_position}')
        if self.player_position == self.goal_position:
            self.broadcast_event('Player Win')
            self.done = True
            return points
        self.turn -= 1

        # enemy turn
        if self.turn == 0:
            print("enemies move...")
            #print(f'enemy positions: {self.enemy_positions}')
            for i in range(len(self.enemy_positions)):
                enemy = self.enemy_positions[i]
                enemy_move = (0, 0)
                # move in the X direction toward the player
                if enemy[1] != self.player_position[1]:
                    enemy_move = (0, 1) if enemy[1] < self.player_position[1] else (0, -1)
                # otherwise move in Y direction if not on same row as player.
                else:
                    enemy_move = (1, 0) if enemy[0] < self.player_position[0] else (-1, 0)

                enemy_pos = ((enemy[0] + enemy_move[0]),(enemy[1] + enemy_move[1]))
                #print(f'enemy move: {enemy_move} new pos: {enemy_pos}')

                # if enemy would move into the player, instead they attack
                if enemy_pos == self.player_position:
                    self.broadcast_event('Enemies Attack')
                    points -= 20
                    enemy_pos = enemy

                # ensure Enemies don't occupy the same space
                self.level[enemy[0]][enemy[1]].has_enemy = False
                if enemy_pos in self.enemy_positions:
                    enemy_pos = enemy
                    #print(f'cannot stand on another. New pos: {enemy_pos}')

                # ensure enemies don't move into a wall
                if not isinstance(self.level[enemy_pos[0]][enemy_pos[1]], floor.Floor):
                    enemy_pos = enemy

                # since the player wont move outside the bounds of the level, the enemies probably wont. I might need to work that in later
                enemy = enemy_pos
                self.level[enemy[0]][enemy[1]].has_enemy = True

                self.enemy_positions[i] = enemy
            self.turn = 2

        self.player_points += points
        if self.player_points <= 0:
            self.broadcast_event('Player Death')
            self.done = True
        return points

    def broadcast_event(self, event):
        print(f'{event}')
        self.events.append(EVENT_CODES[event])

    def get_adjacent_tiles(self):
        tiles = []
        for factor in MOVE_FACTORS:
            x = MOVE_FACTORS[factor][0] + self.player_position[0]
            y = MOVE_FACTORS[factor][1] + self.player_position[1]
            if x >= self.level_width or x < 0:
                x = self.player_position[0]
            if y >= self.level_height or y < 0:
                y = self.player_position[1]
            next_pos = (x,y)
            print(f'({y}, {x}) if move {factor}')
            tiles.append(self.level[next_pos[0]][next_pos[1]])

        return tiles
