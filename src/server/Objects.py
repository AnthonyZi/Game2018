import random
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

        self.action["move"] = self.move

    def move(self, nx,ny):
        x_old, y_old = self.x, self.y

        def return_move():
            where = (x_old,y_old)
            what = "move"
            symbol = WPLAYER
            param = (self.x,self.y)
            return (where,what,symbol,param)

        nx = min(self.world.width-1,max(0,nx))
        ny = min(self.world.height-1,max(0,ny))
        dx = nx-self.x
        dy = ny-self.y
        if dx == 0 and dy == 0:
#            print("no movement")
            return return_move()


        if dx != 0:
            dx = int(dx/abs(dx))
        if dy != 0:
            dy = int(dy/abs(dy))

        nx = self.x+dx
        ny = self.y+dy

        # move checks for nx,ny:
        if dx != 0 and dy != 0:
            if not self.world.get_object(self.x,ny,WGROUND) and not self.world.get_object(nx,self.y,WGROUND):
                return return_move()
        if not self.world.get_object(nx,ny,WGROUND):
#            print("no ground at {},{}".format(nx,ny))
            if random.randint(0,1) == 0:
                if not self.world.get_object(nx,self.y,WGROUND):
#                    print("no ground at {},{}".format(nx,self.y))
                    if not self.world.get_object(self.x,ny,WGROUND):
#                        print("no ground at {},{}".format(self.x,ny))
                        return return_move()
                    nx = self.x
                else:
                    ny = self.y
            else:
                if not self.world.get_object(self.x,ny,WGROUND):
#                    print("no ground at {},{}".format(self.x,ny))
                    if not self.world.get_object(nx,self.y,WGROUND):
#                        print("no ground at {},{}".format(nx,self.y))
                        return return_move()
                    ny = self.y
                else:
                    nx = self.x

        if self.world.get_object(nx,ny,WPLAYER):
#            print("field occupied at {},{}".format(nx,ny))
            return False
        # move checks all ok!

        self.world.move_object(self,nx,ny)
        self.x = nx
        self.y = ny

#        print("moving to {},{}".format(nx,ny))
        return return_move()

class Wall(GameObject):
    def __init__(self, world, x,y, symbol):
        super().__init__(x,y,symbol)
        self.world = world

class Ground(GameObject):
    def __init__(self, world, x,y, symbol):
        super().__init__(x,y,symbol)
        self.world = world

class Ignore(GameObject):
    def __init__(self, world, x,y, symbol):
        super().__init__(x,y,symbol)
        self.world = world

OBJ_GENERATOR = dict()
OBJ_GENERATOR[WPLAYER]  = Player
OBJ_GENERATOR[WWALL]    = Wall
OBJ_GENERATOR[WGROUND]  = Ground
OBJ_GENERATOR[WIGNORE]  = Ignore
