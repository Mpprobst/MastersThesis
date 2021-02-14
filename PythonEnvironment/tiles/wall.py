"""
wall.py
Purpose: implements the wall tile
Author: Michael Probst
"""

from tiles import tile

# Walls can be hit by the player 3 times and they will be destroyed
class Wall(tile.Tile):
    def __init__(self, icon):
        super().__init__(icon)
        self.health = int(icon)

    def interact(self):
        self.health -= 1
        self.icon = f'{self.health}'
        print(f'wall hp: {self.health} icon = {self.icon}')
        if self.health <= 0:
            self.icon = '-'
            return True

        return False
