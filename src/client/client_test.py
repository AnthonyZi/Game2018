from World import World
from Client import Client

import time

if __name__ == "__main__":
    conf = dict()
    conf["playername"] = "Assax"
    conf["server_ip"]   = "localhost"
    conf["server_port"] = 54321

    c = Client(conf)
    c.start()

    with open("map.txt", "r") as mapfile:
        mapdata = mapfile.readlines()
        w = World(mapdata)
        mapdata = w.dump_mapdata()

    c.send_playername()
    c.send_ready(True)
    c.send(nongame_content={"mapdata": mapdata})

    # wait until server starts game

    while not c.mapdata:
        print("{}: {}".format(c.num_players,c.status_players))
        time.sleep(2)
    print("{}: {}".format(c.num_players,c.status_players))

    w = World(c.mapdata)
    print(w.dump_mapdata())
