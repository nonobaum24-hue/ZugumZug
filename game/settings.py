#import
import raylib as rl
from pyray import *
from random import randint
from collections import Counter, deque
from os.path import join

#Game Mechanic
WAGGONS = 45
STATIONS = 3
POINTS_FOR_LENGTH = {1: 1, 2: 2, 3: 4, 4: 7, 5: 10, 6: 15}

ROUTE_CARD_DRAWCOUNT = 4

#Ressources
WAGGON_COLOURS = ["pink", "white", "blue", "yellow", "orange", "black", "red", "green"]

ALL_WAGGON_CARDS = []
for colour in WAGGON_COLOURS:
    ALL_WAGGON_CARDS.extend([colour] * 12)
ALL_WAGGON_CARDS.extend(["locomotive"] * 14)

ALL_ROUTE_CARDS = [
    {"cityA": "Athina", "cityB": "Angora", "points": 5, "path" : "ZugumZug/game/assets/img/cards/routes/ATH-ANG.png"},
    {"cityA": "Budapest", "cityB": "Sofia", "points": 5, "path" : "ZugumZug/game/assets/img/cards/routes/BUD-SOF.png"},
    {"cityA": "Frankfurt", "cityB": "Kobenhavn", "points": 5, "path" : "ZugumZug/game/assets/img/cards/routes/FRA-KOB.png"},
    {"cityA": "Rostov", "cityB": "Erzurum", "points": 5, "path" : "ZugumZug/game/assets/img/cards/routes/ROS-ERZ.png"},
    {"cityA": "Sofia", "cityB": "Smyrna", "points": 5, "path" : "ZugumZug/game/assets/img/cards/routes/SOF-SMY.png"},
    {"cityA": "Kyiv", "cityB": "Petrograd", "points": 6, "path" : "ZugumZug/game/assets/img/cards/routes/KYI-PET.png"},
    {"cityA": "Zurich", "cityB": "Brindisi", "points": 6, "path" : "ZugumZug/game/assets/img/cards/routes/ZUR-BRI.png"},
    {"cityA": "Zurich", "cityB": "Budapest", "points": 6, "path" : "ZugumZug/game/assets/img/cards/routes/ZUR-BUD.png"},
    {"cityA": "Warszawa", "cityB": "Smolensk", "points": 6, "path" : "ZugumZug/game/assets/img/cards/routes/WAR-SMO.png"},
    {"cityA": "Zagrab", "cityB": "Brindisi", "points": 6, "path" : "ZugumZug/game/assets/img/cards/routes/ZAG-BRI.png"},
    {"cityA": "Paris", "cityB": "Zagrab", "points": 7, "path" : "ZugumZug/game/assets/img/cards/routes/PAR-ZAG.png"},
    {"cityA": "Brest", "cityB": "Marseille", "points": 7, "path" : "ZugumZug/game/assets/img/cards/routes/BRE-MAR.png"},
    {"cityA": "London", "cityB": "Berlin", "points": 7, "path" : "ZugumZug/game/assets/img/cards/routes/LON-BER.png"},
    {"cityA": "Edinburgh", "cityB": "Paris", "points": 7, "path" : "ZugumZug/game/assets/img/cards/routes/EDI-PAR.png"},
    {"cityA": "Amsterdam", "cityB": "Pamplona", "points": 7, "path" : "ZugumZug/game/assets/img/cards/routes/AMS-PAM.png"},
    {"cityA": "Roma", "cityB": "Smyrna", "points": 8, "path" : "ZugumZug/game/assets/img/cards/routes/ROM-SMY.png"},
    {"cityA": "Palermo", "cityB": "Constantinople", "points": 8, "path" : "ZugumZug/game/assets/img/cards/routes/PAL-CON.png"},
    {"cityA": "Sarajevo", "cityB": "Sevastopol", "points": 8, "path" : "ZugumZug/game/assets/img/cards/routes/SAR-SEV.png"},
    {"cityA": "Madrid", "cityB": "Dieppe", "points": 8, "path" : "ZugumZug/game/assets/img/cards/routes/MAD-DIE.png"},
    {"cityA": "Barcelona", "cityB": "Bruxelles", "points": 8, "path" : "ZugumZug/game/assets/img/cards/routes/BAR-BRU.png"},
    {"cityA": "Paris", "cityB": "Wien", "points": 8, "path" : "ZugumZug/game/assets/img/cards/routes/PAR-WIE.png"},
    {"cityA": "Barcelona", "cityB": "Munchen", "points": 8, "path" : "ZugumZug/game/assets/img/cards/routes/BAR-MUN.png"},
    {"cityA": "Brest", "cityB": "Venezia", "points": 8, "path" : "ZugumZug/game/assets/img/cards/routes/BRE-VEN.png"},
    {"cityA": "Smolensk", "cityB": "Rostov", "points": 8, "path" : "ZugumZug/game/assets/img/cards/routes/SMO-ROS.png"},
    {"cityA": "Marseille", "cityB": "Essen", "points": 8, "path" : "ZugumZug/game/assets/img/cards/routes/MAR-ESS.png"},
    {"cityA": "Kyiv", "cityB": "Sochi", "points": 8, "path" : "ZugumZug/game/assets/img/cards/routes/KYI-SOC.png"},
    {"cityA": "Madrid", "cityB": "Zurich", "points": 8, "path" : "ZugumZug/game/assets/img/cards/routes/MAD-ZUR.png"},
    {"cityA": "Berlin", "cityB": "Bucuresti", "points": 8, "path" : "ZugumZug/game/assets/img/cards/routes/BER-BUC.png"},
    {"cityA": "Bruxelles", "cityB": "Danzig", "points": 9, "path" : "ZugumZug/game/assets/img/cards/routes/BRU-DAN.png"},
    {"cityA": "Berlin", "cityB": "Roma", "points": 9, "path" : "ZugumZug/game/assets/img/cards/routes/BER-ROM.png"},
    {"cityA": "Angora", "cityB": "Kharkov", "points": 10, "path" : "ZugumZug/game/assets/img/cards/routes/ANG-KHA.png"},
    {"cityA": "Riga", "cityB": "Bucuresti", "points": 10, "path" : "ZugumZug/game/assets/img/cards/routes/RIG-BUC.png"},
    {"cityA": "Essen", "cityB": "Kyiv", "points": 10, "path" : "ZugumZug/game/assets/img/cards/routes/ESS-KYI.png"},
    {"cityA": "Venezia", "cityB": "Constantinople", "points": 10, "path" : "ZugumZug/game/assets/img/cards/routes/VEN-CON.png"},
    {"cityA": "London", "cityB": "Wien", "points": 10, "path" : "ZugumZug/game/assets/img/cards/routes/LON-WIE.png"},
    {"cityA": "Athina", "cityB": "Wilno", "points": 11, "path" : "ZugumZug/game/assets/img/cards/routes/ATH-WIL.png"},
    {"cityA": "Stockholm", "cityB": "Wien", "points": 11, "path" : "ZugumZug/game/assets/img/cards/routes/STO-WIE.png"},
    {"cityA": "Berlin", "cityB": "Moskva", "points": 12, "path" : "ZugumZug/game/assets/img/cards/routes/BER-MOS.png"},
    {"cityA": "Amsterdam", "cityB": "Wilno", "points": 12, "path" : "ZugumZug/game/assets/img/cards/routes/AMS-WIL.png"},
    {"cityA": "Frankfurt", "cityB": "Smolensk", "points": 13, "path" : "ZugumZug/game/assets/img/cards/routes/FRA-SMO.png"},
    # -- die 6 langen Strecken --
    {"cityA": "Lisboa", "cityB": "Danzig", "points": 20, "path" : "ZugumZug/game/assets/img/cards/routes/LIS-DAN.png"},
    {"cityA": "Brest", "cityB": "Petrograd", "points": 20, "path" : "ZugumZug/game/assets/img/cards/routes/BRE-PET.png"},
    {"cityA": "Palermo", "cityB": "Moskva", "points": 20, "path" : "ZugumZug/game/assets/img/cards/routes/PAL-MOS.png"},
    {"cityA": "Kobenhavn", "cityB": "Erzurum", "points": 21, "path" : "ZugumZug/game/assets/img/cards/routes/KOB-ERZ.png"},
    {"cityA": "Edinburgh", "cityB": "Athina", "points": 21, "path" : "ZugumZug/game/assets/img/cards/routes/EDI-ATH.png"},
    {"cityA": "Cadiz", "cityB": "Stockholm", "points": 21, "path" : "ZugumZug/game/assets/img/cards/routes/CAD-STO.png"},
]

GAME_TITLE = 'Zug um Zug'

#UI
WINDOW_HEIGHT = 720
WINDOW_WIDTH = 1280

FONT_SIZE = 20
BIEDERMEIER_PATH = "ZugumZug/game/assets/fonts/BiedermeierKursiv.ttf"

SCALE = WINDOW_WIDTH//1280

MAP_PATH = "ZugumZug/assets/img/map/map.png"
PATHS_WAGGON_CARDS = {
    "pink" : "ZugumZug/game/assets/img/cards/waggons/pink_waggon.png", 
    "white" : "ZugumZug/game/assets/img/cards/waggons/white_waggon.png", 
    "blue" : "ZugumZug/game/assets/img/cards/waggons/blue_waggon.png", 
    "yellow" : "ZugumZug/game/assets/img/cards/waggons/yellow_waggon.png", 
    "orange" : "ZugumZug/game/assets/img/cards/waggons/orange_waggon.png", 
    "black" : "ZugumZug/game/assets/img/cards/waggons/black_waggon.png", 
    "red" : "ZugumZug/game/assets/img/cards/waggons/red_waggon.png", 
    "green" : "ZugumZug/game/assets/img/cards/waggons/green_waggon.png"
}