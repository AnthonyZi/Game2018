import random
import math
import queue
import time

from Server import Server
from World import World
from world_defines import *
from settings import *


class Game(object):
    def __init__(self, conf): 
        server_conf = dict()
        server_conf["num_players"] = conf["num_players"]
        server_conf["server_ip"] = conf["server_ip"]
        server_conf["server_port"] = conf["server_port"]

        self.server = Server(self,server_conf)
        self.server.initialise()

        self.ready = False

    def load_map(self):
        player_maps = [c.mapdata for c in self.server.clients if c.mapdata]
        mapdata = random.choice(player_maps)

        self.world = World(mapdata)

    def initialise_players(self):

        player_coordinates  = []
        player_distance_min = int(max(self.world.width,self.world.height)/self.server.num_players*0.9)
        player_distance_max = int(max(self.world.width,self.world.height)/self.server.num_players*1.1)

        for client in self.server.clients:
            while True:
                rand_x = random.randint(0,self.world.width-1)
                rand_y = random.randint(0,self.world.height-1)

                dists = [math.hypot(rand_x-px,rand_y-py) for px,py,pname in player_coordinates]
                if all([d >= player_distance_min for d in dists]) and all([d <= player_distance_max for d in dists]):

                    if self.world.get_object(rand_x,rand_y, WGROUND):
                        print("playername: {} -> {},{}".format(client.playername,rand_x,rand_y))
                        # determine player position and unicast map with player position!
                        player_coordinates.append((rand_x,rand_y,client.playername))
                        client.player_obj = self.world.generate_player(rand_x,rand_y,client.playername)
                        break

        for client in self.server.clients:
            individual_mapdata = self.world.dump_mapdata_for_player(client.player_obj)
#            print("{} -> \n{}".format(client.playername,individual_mapdata))
            client.send(nongame_content={"mapdata":individual_mapdata})


    def new_game(self):
        self.ready = False
        self.load_map()
#        print(self.world.dump_mapdata())
        self.initialise_players()
        self.ready = True

    def start_game(self):
        self.playing = True
        while self.playing:
            t0 = time.time()

            actions = self.recv_all_actions()
            updates = self.world.update_world(actions)

            self.server.broadcast_content(game_content=updates)

            trest = (1/FPS)-(time.time()-t0)
            if trest < (3/FPS)/4:
                print("restzeit: {}s -> {}%".format(trest,trest/(1/FPS)))
            time.sleep(max(0,trest))



    def recv_all_actions(self):
        actions = []
        for i,client in enumerate(self.server.clients):
#            try:
#                client_actions = client.recv_queue.get(block=True, timeout=2)
#                actions.extend(client_actions)
#            except queue.Empty:
#                print("no packet received from {}".format(client.get_playername()))
            client_actions = client.recv_queue.get(block=True)
            actions.extend(client_actions)
        return actions
