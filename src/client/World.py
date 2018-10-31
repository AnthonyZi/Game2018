import numpy as np
import pyglet as pg

from settings import *
from world_defines import *
from Objects import *

class ImageLoader(object):
    def __init__(self):
        self.imgs = dict()


        self.imgs[WPLAYER] = pg.image.ImageGrid(pg.image.load(WIMGS[WPLAYER]), 4,5, item_width=32,item_height=32)
        self.imgs[WENEMY] = pg.image.ImageGrid(pg.image.load(WIMGS[WENEMY]), 4,5, item_width=32,item_height=32)

        object_sheet = pg.image.ImageGrid(pg.image.load(WIMGS_GAMEOBJECTS), 95,64, item_width=32,item_height=32)

        self.imgs[WGROUND] = object_sheet[WIMGS[WGROUND]]
        self.imgs[WWALL] = object_sheet[WIMGS[WWALL]]

    def get_img(self, symbol):
        return self.imgs[symbol]

class World(object):
    def __init__(self, game):
        self.game = game

        self.player = None
        self.update_object_symbols = [WENEMY] # player is always inside this list
        self.update_objects = []

        mapdata = self.game.client.mapdata

        self.img_loader = ImageLoader()
        self.load_update_dict()

        self.load_map(mapdata)



    def load_update_dict(self):
        self.update_dict = dict()
        self.update_dict["move"] = self.move_object

    def load_map(self, mapdata):
        if not isinstance(mapdata, list):
            mapdata = mapdata.splitlines()

        self.properties = dict()
        for line in [l for l in mapdata if l.startswith("#")]:
            prop_key,prop = line.strip("# \n\r").split("=")
            self.properties[prop_key] = prop

        self.height = 0
        self.width = 0
        for line in [l.strip("\n\r") for l in mapdata if not l.startswith("#")]:
            self.width = max(self.width, len(line.split(" ")))
            self.height += 1


        self.data = np.empty((self.height,self.width), dtype=object)
        for row in range(self.height):
            for col in range(self.width):
                self.data[row,col] = []

        for row,line in enumerate([l.strip("\n\r") for l in mapdata if not l.startswith("#")]):
            for col,tile in enumerate(line.split(" ")):
                for entity_symbol in tile:
                    if entity_symbol == WIGNORE:
                        continue

                    obj = OBJ_GENERATOR[entity_symbol](self.game,col,row,entity_symbol, self.img_loader.get_img(entity_symbol))
                    self.data[row,col].append(obj)

                    if entity_symbol == WPLAYER:
                        self.player = obj
                        self.update_objects.append(obj)
                    elif entity_symbol in self.update_object_symbols:
                        self.update_objects.append(obj)


    def get_all_objects(self, x_cor, y_cor):
        if len(self.data[y_cor,x_cor]) == 0:
            return None
        return self.data[y_cor,x_cor]

    def get_object(self, x_cor, y_cor, symbol):
        for obj in self.data[y_cor,x_cor]:
            if obj.symbol == symbol:
                return obj
        return None


    ## update functions:
    def apply_updates(self, updates):
#        print("updates: \n{}".format(updates))
        for update in updates:
            where,what,symbol,parameters = update
            self.update_dict[what](where,symbol,parameters)

    ##########################################################################
    #
    # BEGIN specific update functions (these are called by update_dict
    #

    def move_object(self, where, symbol, dest):
        from_x,from_y = where
        dest_x,dest_y = dest
        obj = self.get_object(from_x,from_y,symbol)

        # object moves towards new position and updates its own set of coordinates
        # world_drawer changes are also called by object, because these are dependend on object
        obj.move_to(dest_x,dest_y)

        # world changes place of object
        self.data[from_y,from_x].remove(obj)
        self.data[dest_y,dest_x].append(obj)

        # change chunk if necessary
        chunk_old_x = int(from_x/CHUNKSIZE)
        chunk_old_y = int(from_y/CHUNKSIZE)
        chunk_new_x = int(dest_x/CHUNKSIZE)
        chunk_new_y = int(dest_y/CHUNKSIZE)
        if not chunk_old_x == chunk_new_x or not chunk_old_y == chunk_new_y:
            obj.sprite.batch = self.game.world_drawer.sprite_chunks[obj.layer,chunk_new_y,chunk_new_x]
#            print("change batch: {},{}".format(chunk_new_x,chunk_new_y))

    #
    # END specific update functions (these are called by update_dict
    #
    ##########################################################################

    def dump_mapdata(self):
        out = ""
        for row in range(self.height):
            for col in range(self.width):
                if col != 0:
                    out += " "
                object_symbols = [o.symbol for o in self.data[row,col]]
                if len(object_symbols) != 0:
                    out += "".join(object_symbols)
                else:
                    out += " "
            out += "\n"
        for prop_key in self.properties.keys():
            out += "#{}={}\n".format(prop_key,self.properties[prop_key])
        return out
