"""
run_rl.py

Startet die raylib-Grafikversion (gamloop_rl.py) auf einem echten Display,
im Unterschied zu run.py, das die alte Konsolen-/Pygame-Version
(gameLoop.py) startet.

Ausführen (aus dem "game"-Ordner heraus, damit die relativen
"ZugumZug/game/..."-Pfade in Code/settings.py auflösen - siehe Hinweis
unten):

    cd .. && python3 game/run_rl.py

Ablauf zum Testen des Starts:
1. Fenster öffnet sich, im Hintergrund wird eine zufällige Zugreihenfolge
   ausgelost (siehe game.__init__ in gamloop_rl.py).
2. start_game() läuft: jeder Spieler bekommt Zielkarten zum
   Annehmen/Ablehnen (Klick auf die roten/grünen Buttons). Mindestens 1
   Karte muss behalten werden.
3. Danach startet game_loop(): idle_screen() mit "Start Round"-Button,
   danach choose_action() mit den drei Optionen (Strecke besetzen /
   Waggonkarte ziehen / Zielkarte ziehen).

Zum Beenden: Fenster schließen (X) oder ESC (raylib-Standard).
"""

import json
import os
import sys

GAME_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(GAME_DIR)
sys.path.insert(0, GAME_DIR)

# Der Code in gamloop_rl.py/settings.py verwendet fest verdrahtete Pfade wie
# "ZugumZug/game/assets/...". Die lösen nur auf, wenn das Arbeitsverzeichnis
# der ELTERNORDNER des geklonten "ZugumZug"-Repos ist. Falls du dieses
# Skript aus einem anderen Ordner heraus startest, wechseln wir das
# Arbeitsverzeichnis hier automatisch dorthin.
os.chdir(os.path.dirname(REPO_ROOT))

import mechanicClasses as m
from gamloop_rl import game as Game

mapdata_path = os.path.join(GAME_DIR, "mapData.json")
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

g = Game(pm, board)
g.start_game()
g.game_loop()