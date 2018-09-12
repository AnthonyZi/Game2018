import numpy as np

from settings import *
from world_defines import *
from Objects import *



class World(object):
    def __init__(self, mapdata):

        if not isinstance(mapdata, list):
            mapdata = mapdata.splitlines()

        self.load_object_generator()
        self.load_map(mapdata)

    def load_object_generator(self):
        self.generate_object = dict()
        self.generate_object[WWALL] = Wall
        self.generate_object[WPLAYER] = Player



    def load_map(self, mapdata):
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

        for row,line in enumerate([l.strip("\n\r") for l in mapdata if not l.startswith("#")]):
            data_idx = int(row/CHUNKSIZE)
            chunk_idx = row % CHUNKSIZE
            for col,tile in enumerate(line.split(" ")):
                data_idy = int(col/CHUNKSIZE)
                chunk_idy = col % CHUNKSIZE
                self.data[col,row] = []
                for entity_symbol in tile:
                    if entity_symbol == ".":
                        continue
                    obj = self.generate_object[entity_symbol](self,col,row,entity_symbol)
                    self.data[col,row].append(obj)

        self.data = self.data[::-1]

    def dump_mapdata(self):
        out = ""
        for row in range(self.height):
            for col in range(self.width):
                if col != 0:
                    out += " "
                object_symbols = [o.symbol for o in self.data[col,row]]
                if len(object_symbols) != 0:
                    out += "".join(object_symbols)
                else:
                    out += "."
            out += "\n"
        for prop_key in self.properties.keys():
            out += "#{}={}\n".format(prop_key,self.properties[prop_key])
        return out
