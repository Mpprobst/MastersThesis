"""
floor.py
Purpose: implements the floor tile
Author: Michael Probst
"""

from tiles import tile

class Floor(tile.Tile):
    def __init__(self, icon):
        super().__init__(icon)
        if icon == 'F':
            self.has_food = True
        elif icon == 'E':
            self.has_enemy = True

    def interact(self):
        if self.has_enemy:
            return False
            
        return True

    def get_icon(self):
        if self.has_enemy:
            self.icon = 'E'
        elif self.has_food:
            self.icon = 'F'
        else:
            self.icon = '-'

        return self.icon

    def pickup_food(self):
        if self.has_food:
            self.icon = '-'
            self.has_food = False
