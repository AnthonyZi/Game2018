from Game import Game

if __name__ == "__main__":
    g = Game(1200,800, "helloo")
    g.connect_to_server(playername="A2")
    g.new_game("map.txt")
    g.start()
