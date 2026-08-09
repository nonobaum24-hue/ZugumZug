import json
import mechanicClasses as m
from gameLoop import Game
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
mapdata_path = os.path.join(script_dir, "mapData.json")

with open(mapdata_path) as f:
    mapData = json.load(f)

board = m.Board()
board.loadMap(mapData)

wc = m.WaggonStack()
rcs = m.RouteCardStack()
p1 = m.Player("Nono", "red", wc)
p2 = m.Player("Bob", "blue", wc)
pcs = m.PublicCardStack(wc)
pm = m.PlayerManager([p1, p2], wc, pcs, rcs)

game = Game(pm, board)
game.startGame()
game.run()