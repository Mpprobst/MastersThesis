"""
enemy.py
Purpose: implements the enemy tile
Author: Michael Probst
"""

from tiles import tile
# CURRENTLY NOT USED
class Enemy(tile.Tile):
    def __init__(self, icon):
        super.__init__(icon)
        # TODO: maybe implement enemy health in the future

    def interact(self):
        return False
