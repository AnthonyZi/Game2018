import sys

import threading
import socket
import queue
import json
from collections import defaultdict
from collections import deque

from settings import *


class SendThread(threading.Thread):
    def __init__(self, sock, send_queue):
        super().__init__()
        self.sock = sock
        self.send_queue = send_queue
        self.sockwriter = sock.makefile(mode="w")

        self.running = True

    def close(self):
        self.running = False

    def run(self):
        while self.running:
            try:
                msg = self.send_queue.get(block=True, timeout=3)
                self.sockwriter.write("{}{}".format(msg,PACKET_DELIMITER))
                self.sockwriter.flush()
            except queue.Empty:
                pass

class Client(threading.Thread):
    def __init__(self, configuration):
        super().__init__()
        self.server_ip      = configuration["server_ip"]
        self.server_port    = configuration["server_port"]
        self.playername     = configuration["playername"]

        self.send_queue = queue.Queue()
        self.recv_queue = deque()

        self.packet_buffer = []

        self.running = True

        self.server_info = defaultdict(str)

        self.status_players = []
        self.num_players = 0
        self.mapdata = None

    def close(self):
        self.running = False
        self.sock.shutdown(socket.SHUT_RDWR)

    def connect_socket(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.server_ip,self.server_port))
        except socket.error:
            print("Failed to create socket")

    def packet_complete(self,packet):
        return packet.endswith(PACKET_DELIMITER)

    def interpret_packet(self,packet):
        nongame_content = None
        game_content    = None

        if packet:
            content = json.loads(packet)

            if "nongame"    in content.keys():
                nongame_content = content["nongame"]
            if "game"       in content.keys():
                game_content    = content["game"]

        return nongame_content,game_content

    def interpret_nongame_content(self,nongame_content):
        if "num_players"            in nongame_content.keys():
            self.num_players            = nongame_content["num_players"]
        if "status_players"         in nongame_content.keys():
            self.status_players         = nongame_content["status_players"]
        if "mapdata" in nongame_content.keys():
            self.mapdata                = nongame_content["mapdata"]


    def receive_packet_from_socket(self):
        packet_received = ""
        while True:
            data = self.sock.recv(1024)
            if not data:
                print("lost connection to server {}:{}".format(self.server_ip,self.server_port))
                self.running = False
                break
            data = data.decode()

            packet_received += data

            if self.packet_complete(packet_received):
                break

        return packet_received[:-7]

    def receive_packet(self):
        if len(self.packet_buffer) > 0:
            packet = self.packet_buffer.pop(0)
        else:
            packet = self.receive_packet_from_socket()

            if PACKET_DELIMITER in packet:
                self.packet_buffer += packet.split(PACKET_DELIMITER)
                packet = self.packet_buffer.pop(0)

        nongame_content,game_content = self.interpret_packet(packet)

        if nongame_content is not None:
            self.interpret_nongame_content(nongame_content)
        return game_content

    def run(self):
        self.connect_socket()
        sthread = SendThread(self.sock, self.send_queue)
        sthread.start()
        print("connected to server {}:{}".format(self.server_ip,self.server_port))

        while self.running:
            packet_content = self.receive_packet()
            if packet_content is not None:
                self.recv_queue.append(packet_content)

        sthread.close()
        sthread.join()

    def send(self, nongame_content=None, game_content=None):
        packet = dict()

        if nongame_content  is not None:
            packet["nongame"]   = nongame_content
        if game_content     is not None:
            packet["game"]      = game_content

        packet_json = json.dumps(packet)
        self.send_queue.put(packet_json)

    def send_playername(self):
        nongame_content = dict()
        nongame_content["playername"] = self.playername
        self.send(nongame_content=nongame_content)

    def send_ready(self,ready_state):
        nongame_content = dict()
        nongame_content["ready"] = ready_state
        self.send(nongame_content=nongame_content)
