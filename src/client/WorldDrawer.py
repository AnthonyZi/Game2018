import pyglet as pg
import numpy as np

from math import ceil

from World import World
from Camera import Camera
from settings import *
from world_defines import *


# organises world in chunks and updates only by camera captured part of the world
class WorldDrawer(object):
    def __init__(self, game):
        self.game = game

        self.initialise_player_position()
        self.initialise_camera()
        self.initialise_chunks()

    def initialise_player_position(self):
        self.center_x = self.game.world.player.x
        self.center_y = self.game.world.player.y
        self.center_x_chunk = int(self.center_x/CHUNKSIZE)
        self.center_y_chunk = int(self.center_y/CHUNKSIZE)

    def initialise_camera(self):

        self.camera = Camera(*self.game.get_size())
        self.camera.set_camera_pos_pix(self.center_x*TILESIZE,self.center_y*TILESIZE)
#        self.camera.move(self.center_x,self.center_y)
#        self.camera.move_pix(TILESIZE/2,TILESIZE/2)

    def initialise_chunks(self):

        self.chunks_width    = ceil(self.game.world.width/CHUNKSIZE)
        self.chunks_height   = ceil(self.game.world.height/CHUNKSIZE)

        screen_chunks_width  = self.camera.width/TILESIZE/CHUNKSIZE
        screen_chunks_height = self.camera.height/TILESIZE/CHUNKSIZE
        self.screen_chunks_side_h  = ceil(screen_chunks_width/2)
        self.screen_chunks_side_v  = ceil(screen_chunks_height/2)

        self.sprite_chunks  = np.empty((NUM_LAYERS,self.chunks_height,self.chunks_width), dtype=object)
        for layer in range(NUM_LAYERS):
            for row in range(self.chunks_height):
                for col in range(self.chunks_width):
                    batch = pg.graphics.Batch()
                    self.sprite_chunks[layer,row,col] = batch

        for layer in range(NUM_LAYERS):
            for row in range(self.game.world.height):
                chunk_row   = int(row/CHUNKSIZE)
                for col in range(self.game.world.width):
                    chunk_col   = int(col/CHUNKSIZE)
                    for sprite in [obj.sprite for obj in self.game.world.data[row,col] if obj.layer == layer]:
                        # flip sprites for right display of map (top-left corner as origin)
#                        sprite.y = self.game.world.height - sprite.y
                        sprite.batch = self.sprite_chunks[layer,chunk_row,chunk_col]

    def draw(self):
        for sprites_layer in self.get_sprite_chunks_to_draw():
            for sprite_batch in sprites_layer:
                sprite_batch.draw()

    def get_sprite_chunks_to_draw(self):
        min_x = max(0,self.center_x_chunk-self.screen_chunks_side_h)
        max_x = self.center_x_chunk+self.screen_chunks_side_h
        min_y = max(0,self.center_y_chunk-self.screen_chunks_side_v)
        max_y = self.center_y_chunk+self.screen_chunks_side_v

        batches = []
        for layer in range(NUM_LAYERS):
            batches.append(list(self.sprite_chunks[layer,min_y:max_y+1,min_x:max_x+1].ravel()))
        return batches

    def move_center_pix(self,to_x,to_y):
        self.camera.set_camera_pos_pix(to_x,to_y)

        self.center_x = int(to_x/TILESIZE)
        self.center_y = int(to_y/TILESIZE)


        self.center_x_chunk = int(self.center_x/CHUNKSIZE)
        self.center_y_chunk = int(self.center_y/CHUNKSIZE)


#    def find_player(self):
#        for row in range(self.game.world.height):
#            for col in range(self.game.world.width):
#                if(self.game.world.get_object(col,row,WPLAYER)):
#                    return col,row
