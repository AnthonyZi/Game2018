import time

from Game import Game


if __name__ == "__main__":

    conf = dict()
    conf["num_players"] = 1
    conf["server_ip"]   = "localhost"
    conf["server_port"] = 54321

    g = Game(conf)

    g.new_game()

    while not g.ready:
        time.sleep(1)

    g.start_game()
