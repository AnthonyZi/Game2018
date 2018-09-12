from collections import defaultdict

from world_defines import *

class GameObject(object):
    def __init__(self, x,y, symbol):
        self.x = x
        self.y = y
        self.symbol = symbol

        self.action = defaultdict(lambda : self.no_action)

    def no_action(self):
        pass

class Player(GameObject):
    def __init__(self, world, x,y, symbol):
        super().__init__(x,y,symbol)

        self.world = world

        self.dx = 0
        self.dy = 0

        self.velocity = 1

        self.action["move"] = self.move

    def collide_with_walls(self, x, y):
        if self.world.get_object(x,y,WWALL):
            return True
        return False

    def move(self, dx,dy):
        x_old, y_old = self.x, self.y
        if dx != 0:
            dx = int(dx/abs(dx))
        if dy != 0:
            dy = int(dy/abs(dy))

        for step in range(int(self.velocity)):
            if self.collide_with_walls(self.x+dx, self.y+dy):
                break
            self.x += dx
            self.y += dy

        if self.x != old_x or self.y != old_y:
            self.world.move_object(self,self.x,self.y)

class Wall(GameObject):
    def __init__(self, world, x,y, symbol):
        super().__init__(x,y,symbol)

        self.world = world
