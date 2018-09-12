import random

from Server import Server
from World import World


class Game(object):
    def __init__(self, conf):

        server_conf = dict()
        server_conf["num_players"] = conf["num_players"]
        server_conf["server_ip"] = conf["server_ip"]
        server_conf["server_port"] = conf["server_port"]

        self.server = Server(self,server_conf)
        self.server.initialise()

    def load_map(self):
        player_maps = [c.mapdata for c in self.server.clients if c.mapdata]
        mapdata = random.choice(player_maps)

        self.server.broadcast_content(nongame_content={"mapdata":mapdata})

        self.world = World(mapdata)


    def new_game(self):
        self.load_map()

    def start_game(self):
        pass
