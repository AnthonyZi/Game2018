import sys
import os
import queue
import threading

import pyglet as pg
from pyglet.window import key
from pyglet.window import FPSDisplay

from World import World
from WorldDrawer import WorldDrawer
from Client import Client
from settings import *
from world_defines import *

import time

class Game(pg.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.frame_rate = 1/FPS
        self.fps_display = FPSDisplay(self)

        self.load_keyevent_dicts()

        self.wait_for_response = False
        self.update_queue = queue.Queue()

    def load_keyevent_dicts(self):

        self.direction_dict = dict()
        self.direction_dict[key.LEFT]   = [-1, 0]
        self.direction_dict[key.RIGHT]  = [+1, 0]
        self.direction_dict[key.UP]     = [ 0, 1]
        self.direction_dict[key.DOWN]   = [ 0,-1]

        self.kdict = dict()
        self.kdict["direction"]    = [0,0]

    def connect_to_server(self, playername=PLAYERNAME, address=SERVER_ADDRESS, port=SERVER_PORT):
        conf = dict()
        conf["playername"]  = playername
        conf["server_ip"]   = address
        conf["server_port"] = port

        self.client = Client(conf)
        self.client.start()
        self.client.send_playername()

    def new_game(self, mapfile):
        self.send_mapdata(mapfile)
        self.client.send_ready(True)

        while not self.client.mapdata:
            print("{}: {}".format(self.client.num_players,self.client.status_players))
            time.sleep(1)
        print("all player ready!")

#        print(self.client.mapdata)

        self.world = World(self)
        self.world_drawer = WorldDrawer(self)

#        print(self.world.dump_mapdata())

    def send_mapdata(self, filename):
        with open(filename, "r") as mapfile:
            mapdata = mapfile.readlines()
            self.client.send(nongame_content={"mapdata":mapdata[::-1]})

    def start(self):
        pg.clock.schedule_interval(self.update, self.frame_rate)
#        self.lock_step_thread = LockStepThread(self)
#        self.lock_step_thread.start()
        pg.app.run()

    def update(self, dt):
        for obj in self.world.update_objects:
            obj.update(dt)

        if not self.wait_for_response:
            game_content = self.prepare_packet() # empty list if no action for server
#            print("DESIRED:\n{}".format(game_content)) if len(updates)>0 else None
            self.client.send(game_content=game_content)
            self.wait_for_response=True

#        elif all(gui_updates_finished):
        else:
            try:
                updates = self.client.recv_queue.popleft()
#                print("UPDATES:\n{}".format(updates)) if len(updates)>0 else None
                self.world.apply_updates(updates)
                self.wait_for_response = False
            except IndexError:
                pass

    def prepare_packet(self):
        game_content = []

        # player movements
        # player movement can be triggered if either character stands still or
        # if last player movement is already 70% done -> reduces visible lag because of
        # network traffic (rtt)
        if self.world.player.walk_prog_factor == 0 or self.world.player.walk_prog_factor > 0.6:
            dx,dy = self.kdict["direction"]
            # if no movement -> nop, so that other players are allowed to move
#            if not (dx != 0 and dy != 0):
            if dx != 0 or dy != 0:
                self.world.player.set_image_by_direction(dx,dy)
                px,py = int(self.world.player.x),int(self.world.player.y)
                destx,desty = px+dx,py+dy
                game_content.append( ((px,py), "move", WPLAYER, (destx,desty)) )

        # packet prepared
        return game_content

    def quit(self):
        self.client.close()
        pg.app.exit()

    def on_draw(self):
        self.clear()
        self.world_drawer.draw()
        self.fps_display.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol in self.direction_dict.keys():
            self.kdict["direction"] = self.direction_dict[symbol]
        elif symbol == key.ESCAPE:
            self.quit()


    def on_key_release(self, symbol, modifiers):
        if symbol in self.direction_dict.keys():
            if self.kdict["direction"] == self.direction_dict[symbol]:
                self.kdict["direction"] = [0,0]
