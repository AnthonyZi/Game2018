import sys
import socket

import time

from Client import Client

sys.path.insert(0, "./src/server/settings")
import settings as SETTINGS


class Server(object):
    def __init__(self, game, configuration):
        self.game = game

        self.num_players    = configuration["num_players"]
        self.ip_addr        = configuration["server_ip"]
        self.port_addr      = configuration["server_port"]

        self.clients = []

    def start_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.sock.bind(("localhost", 54321))
        except socket.error as msg:
            print("Failed to bind socket. Error code: {}, Message: {}".format(str(msg[0]),str(msg[1])))
            exit()

        self.sock.listen(10)

    def print_client_informations(self):
        time.sleep(0.2)
        num_ready = sum([1 for c in self.clients if c.ready])
        print("{}/{} clients, {} ready".format(len(self.clients),self.num_players,num_ready))
        self.send_server_info()

    def disconnect_client(self, client):
        self.clients.remove(client)
        self.print_client_informations()

    def connect_client(self):
        conn,addr = self.sock.accept()
        newClient = Client(self,conn,addr)
        newClient.start()
        self.clients.append(newClient)

    def connect_all_clients(self):
        while True:
            while len(self.clients) < self.num_players:
                self.connect_client()
                self.print_client_informations()

            ready = [c.ready for c in self.clients]
            maps = [c.mapdata for c in self.clients if c.mapdata is not None]
            if all(ready) and any(maps):
                break


            self.print_client_informations()
            time.sleep(2)


    def initialise(self):
        self.start_socket()
        self.connect_all_clients()
        self.game.new_game()
        self.game.start_game()

    def broadcast_content(self,nongame_content=None,game_content=None):
        for c in self.clients:
            c.send(nongame_content=nongame_content,game_content=game_content)

    def send_server_info(self):
        nongame_content = dict()

        status_players = [(c.playername,c.ready) for c in self.clients]

        nongame_content["num_players"] = self.num_players
        nongame_content["status_players"] = status_players

        self.broadcast_content(nongame_content=nongame_content)
