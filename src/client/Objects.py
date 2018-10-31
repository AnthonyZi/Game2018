from collections import defaultdict
import pyglet as pg
import math
import time

from settings import *
from world_defines import *

class GameObject(object):
    def __init__(self, game, x,y, symbol, pgimage, layer):
        self.game = game
        self.x = x
        self.y = y
        self.symbol = symbol
        self.layer = layer

        self.sprite = pg.sprite.Sprite(pgimage, x=self.x*TILESIZE, y=self.y*TILESIZE)

    def flip_y(self, y_cor):
        return self.game.world.height - y_cor

class Character(object):
    def __init__(self, game, x,y, symbol, pgimage_seq):
        self.game = game
        self.x = x
        self.y = y
        self.symbol = symbol
        self.layer = 3

        self.action = "stand"

        self.load_sprite_sheet(pgimage_seq)

        self.sprite = pg.sprite.Sprite(self.imgs_by_direction[3]["stand"], x=self.x*TILESIZE, y=self.y*TILESIZE)

        self.sprite_last_x = self.sprite.x
        self.sprite_last_y = self.sprite.y
        self.sprite_next_x = self.sprite.x
        self.sprite_next_y = self.sprite.y
        self.walk_prog_factor = 0


    def load_sprite_sheet(self,pgimage_seq):
        def get_animation(i,j):
            return pg.image.Animation.from_image_sequence(pgimage_seq[i:i+j],0.1,loop=True)

        # directions:
        #      1
        #      ^
        # 2 <- + -> 0
        #      v
        #      3
        self.imgs_by_direction = dict()
        self.imgs_by_direction[0] = dict()
        self.imgs_by_direction[1] = dict()
        self.imgs_by_direction[2] = dict()
        self.imgs_by_direction[3] = dict()
        self.imgs_by_direction[1]["stand"]        = pgimage_seq[0]
        self.imgs_by_direction[0]["stand"]        = pgimage_seq[5]
        self.imgs_by_direction[2]["stand"]        = pgimage_seq[10]
        self.imgs_by_direction[3]["stand"]        = pgimage_seq[15]
        self.imgs_by_direction[1]["walk"]         = get_animation( 1, 4)
#        self.imgs_by_direction[( 0, 1)]["spellcast"]    = get_animation( 0, 7)
#        self.imgs_by_direction[( 0, 1)]["slash"]        = get_animation(169, 6)
#        self.imgs_by_direction[( 0, 1)]["hurt"]         = get_animation(260, 6)
        self.imgs_by_direction[0]["walk"]         = get_animation( 6, 4)
#        self.imgs_by_direction[( 1, 0)]["spellcast"]    = get_animation(39, 7)
#        self.imgs_by_direction[( 1, 0)]["slash"]        = get_animation(208, 6)
#        self.imgs_by_direction[( 1, 0)]["hurt"]         = get_animation(260, 6)
        self.imgs_by_direction[2]["walk"]         = get_animation(11, 4)
#        self.imgs_by_direction[(-1, 0)]["spellcast"]    = get_animation(13, 7)
#        self.imgs_by_direction[(-1, 0)]["slash"]        = get_animation(182, 6)
#        self.imgs_by_direction[(-1, 0)]["hurt"]         = get_animation(260, 6)
        self.imgs_by_direction[3]["walk"]         = get_animation(16, 4)
#        self.imgs_by_direction[( 0,-1)]["spellcast"]    = get_animation(26, 7)
#        self.imgs_by_direction[( 0,-1)]["slash"]        = get_animation(195, 6)
#        self.imgs_by_direction[( 0,-1)]["hurt"]         = get_animation(260, 6)

    def set_image_by_direction(self, dx,dy):
        direction = (round(math.atan2(dy,dx)*2/math.pi)+4)%4 # 0:right, 1:up, 2:left, 3:down
        self.sprite.image = self.imgs_by_direction[direction][self.action]

    def move_to(self, to_x,to_y):

        self.sprite_last_x = self.sprite.x
        self.sprite_last_y = self.sprite.y
        self.sprite_next_x = to_x*TILESIZE
        self.sprite_next_y = to_y*TILESIZE
        self.x = to_x
        self.y = to_y

        self.action = "walk"
        self.walk_prog_factor = 0

        dx = self.sprite_next_x - self.sprite_last_x
        dy = self.sprite_next_y - self.sprite_last_y
        self.set_image_by_direction(dx,dy)

#        self.sprite.x = self.x*TILESIZE
#        self.sprite.y = self.y*TILESIZE
#        self.sprite.y = self.flip_y(self.y)

    def update(self,dt):
#        print("self.action={}".format(self.action))

        if self.action == "walk":
            # max approx. 0.9: 32*(1-0.98) = 0.64 pixel jumps (recognised as lag on fast machines)
            # lag is worse if correct sprite position (see below) is not aligned after every step!
            if self.walk_prog_factor < 1:

                self.walk_prog_factor += dt*CHARACTER_WALK_SPEED # dt*CWS: CWS in fields per second

                self.sprite.x = (1-self.walk_prog_factor)*self.sprite_last_x + self.walk_prog_factor*self.sprite_next_x
                self.sprite.y = (1-self.walk_prog_factor)*self.sprite_last_y + self.walk_prog_factor*self.sprite_next_y

#                print("walked a step {},{}".format(self.sprite.x,self.sprite.y))

            else:
                self.action = "stand"
                self.walk_prog_factor = 0

                dx = self.sprite_next_x - self.sprite_last_x
                dy = self.sprite_next_y - self.sprite_last_y
                self.set_image_by_direction(dx,dy)

                # it looks better if sprite is visually not in place in the tradeoff against lagging
#                self.sprite.x = self.x*TILESIZE
#                self.sprite.y = self.y*TILESIZE

#                print("stopped walking {},{}".format(self.sprite.x,self.sprite.y))

class Player(Character):
    def __init__(self, game, x,y, symbol, pgimage):
        super().__init__(game,x,y,symbol,pgimage)

    def move_to(self, to_x,to_y):
        super().move_to(to_x,to_y)

    def update(self,dt):
        super().update(dt)
#        print("##{},{},{}".format(time.time(),self.sprite.x,self.sprite.y))
        self.game.world_drawer.move_center_pix(self.sprite.x,self.sprite.y)

class Enemy(Character):
    def __init__(self, game, x,y, symbol, pgimage):
        super().__init__(game,x,y,symbol,pgimage)
        self.symbol = WPLAYER

    def move_to(self, to_x,to_y):
        super().move_to(to_x,to_y)
        dx = to_x - self.x
        dy = to_y - self.y
        self.set_image_by_direction(dx,dy)



class Wall(GameObject):
    def __init__(self, game, x,y, symbol, pgimage):
        super().__init__(game,x,y,symbol,pgimage,layer=0)

class Ground(GameObject):
    def __init__(self, game, x,y, symbol, pgimage):
        super().__init__(game,x,y,symbol,pgimage,layer=0)


OBJ_GENERATOR = dict()
OBJ_GENERATOR[WPLAYER]  = Player
OBJ_GENERATOR[WENEMY]   = Enemy
OBJ_GENERATOR[WWALL]    = Wall
OBJ_GENERATOR[WGROUND]  = Ground
