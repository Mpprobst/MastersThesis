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
        self.health = 3

    def interact(self):
        self.health -= 1
        if self.health < 0:
            self.icon = '-'
            return True

        return False
