"""
goal.py
Purpose: implements the goal tile
Author: Michael Probst
"""

from tiles import tile

class Goal(tile.Tile):
    def __init__(self, icon):
        super().__init__(icon)

    def interact(self):
        return True
