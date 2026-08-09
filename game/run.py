import json
import mechanicClasses as m
from gameLoop import Game

with open("mapData.json") as f:
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