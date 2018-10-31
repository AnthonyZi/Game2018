import numpy as np
import random

from settings import *
from world_defines import *
from Objects import *

class World(object):
    def __init__(self, mapdata):


        self.load_map(mapdata)

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
                    obj = OBJ_GENERATOR[entity_symbol](self,col,row,entity_symbol)
                    self.data[row,col].append(obj)

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

    def dump_mapdata_for_player(self, player_obj):
        out = ""
        for row in range(self.height):
            for col in range(self.width):
                if col != 0:
                    out += " "
                objects = [o for o in self.data[row,col]]
                for obj in objects:
                    symbol = obj.symbol
                    if obj.symbol == WPLAYER and not obj == player_obj:
                        symbol = WENEMY
                    out += symbol
                if len(objects) == 0:
                    out += " "
            out += "\n"
        for prop_key in self.properties.keys():
            out += "#{}={}\n".format(prop_key,self.properties[prop_key])
        return out

    def generate_player(self, x_cor,y_cor, playername):
        obj = OBJ_GENERATOR[WPLAYER](self,x_cor,y_cor,WPLAYER)
        obj.name = playername
        self.data[y_cor,x_cor].append(obj)
        return obj

    def get_all_objects(self, x_cor,y_cor):
        if len(self.data[y_cor,x_cor]) == 0:
            return None
        return self.data[y_cor,x_cor]

    def get_object(self, x_cor,y_cor, symbol):
        for obj in self.data[y_cor,x_cor]:
            if obj.symbol == symbol:
                return obj
        return None

    def move_object(self, obj, to_x,to_y):
        self.data[obj.y,obj.x].remove(obj)
        self.data[to_y,to_x].append(obj)

    def update_world(self, actions):
        updates = []
        random.shuffle(actions)
#        print(self.dump_mapdata())
        for action in actions:
            where,what,symbol,parameters = action
            x,y = where
            obj = self.get_object(x,y,symbol)
            action = obj.action[what](*parameters)
            if action:
                updates.append(action)
#        print(self.dump_mapdata())
        return updates
