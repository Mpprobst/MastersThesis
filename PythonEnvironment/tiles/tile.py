"""
tile.py
Purpose: base class for all tiles in the scavenger game
Author: Michael Probst
"""

class Tile():
    def __init__(self, icon):
        self.icon = icon     # icon that represents the tile
        self.has_food = False
        self.has_enemy = False

    # What happens when an entity walks into the tile
    # Returns true or false based on if player can occupy the space
    def interact(self):
        raise NotImplementedError

    def get_icon(self):
        return self.icon
