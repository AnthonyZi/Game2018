import threading
import socket
import queue
import json

from settings import *


class SendThread(threading.Thread):
    def __init__(self, connection, send_queue):
        super().__init__()
        self.connection = connection
        self.send_queue = send_queue
        self.sockwriter = self.connection.makefile(mode="w")

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
    def __init__(self, server, connection, address):
        super().__init__()
        self.server = server
        self.connection = connection
        self.address = address
        self.send_queue = queue.Queue()
        self.recv_queue = queue.Queue()

        self.packet_buffer = []

        self.running = True

        self.playername = ""
        self.mapdata = None
        self.ready = False

    def get_playername(self):
        return self.playername if self.playername is not "" else self.address

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
        if "playername"     in nongame_content.keys():
            self.playername = nongame_content["playername"]
        if "ready"          in nongame_content.keys():
            self.ready      = nongame_content["ready"]
        if "mapdata"        in nongame_content.keys():
            self.mapdata    = nongame_content["mapdata"]


    def receive_packet_from_socket(self):
        packet_received = ""
        while True:
            data = self.connection.recv(1024)
            if not data:
                print("lost connection to client {}".format(self.get_playername()))
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
        sthread = SendThread(self.connection, self.send_queue)
        sthread.start()
        print("connected client {}".format(self.get_playername()))

        while self.running:
            packet_content = self.receive_packet()
            if packet_content is not None:
                self.recv_queue.put(packet_content)

        sthread.close()
        sthread.join()

        self.server.disconnect_client(self)

    def send(self, nongame_content=None, game_content=None):
        packet = dict()

        if nongame_content  is not None:
            packet["nongame"]   = nongame_content
        if game_content     is not None:
            packet["game"]      = game_content

        packet_json = json.dumps(packet)
        self.send_queue.put(packet_json)
