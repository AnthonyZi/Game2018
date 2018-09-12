from collections import defaultdict

from world_defines import *

class GameObject(object):
    def __init__(self, x,y, symbol):
        self.x = x
        self.y = y

        self.symbol = symbol

class Player(GameObject):
    def __init__(self, world, x,y, symbol):
        super().__init__(x,y,symbol)

        self.world = world

        self.dx = 0
        self.dy = 0

        self.velocity = 1

class Wall(GameObject):
    def __init__(self, world, x,y, symbol):
        super().__init__(x,y,symbol)

        self.world = world
