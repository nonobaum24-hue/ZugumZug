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
    {"cityA": "Athina", "cityB": "Angora", "points": 5, "path" : "ZugumZug/assets/img/cards/ATH-ANG.png"},
    {"cityA": "Budapest", "cityB": "Sofia", "points": 5, "path" : "ZugumZug/assets/img/cards/BUD-SOF.png"},
    {"cityA": "Frankfurt", "cityB": "Kobenhavn", "points": 5, "path" : "ZugumZug/assets/img/cards/FRA-KOB.png"},
    {"cityA": "Rostov", "cityB": "Erzurum", "points": 5, "path" : "ZugumZug/assets/img/cards/ROS-ERZ.png"},
    {"cityA": "Sofia", "cityB": "Smyrna", "points": 5, "path" : "ZugumZug/assets/img/cards/SOF-SMY.png"},
    {"cityA": "Kyiv", "cityB": "Petrograd", "points": 6, "path" : "ZugumZug/assets/img/cards/KYI-PET.png"},
    {"cityA": "Zurich", "cityB": "Brindisi", "points": 6, "path" : "ZugumZug/assets/img/cards/ZUR-BRI.png"},
    {"cityA": "Zurich", "cityB": "Budapest", "points": 6, "path" : "ZugumZug/assets/img/cards/ZUR-BUD.png"},
    {"cityA": "Warszawa", "cityB": "Smolensk", "points": 6, "path" : "ZugumZug/assets/img/cards/WAR-SMO.png"},
    {"cityA": "Zagrab", "cityB": "Brindisi", "points": 6, "path" : "ZugumZug/assets/img/cards/ZAG-BRI.png"},
    {"cityA": "Paris", "cityB": "Zagrab", "points": 7, "path" : "ZugumZug/assets/img/cards/PAR-ZAG.png"},
    {"cityA": "Brest", "cityB": "Marseille", "points": 7, "path" : "ZugumZug/assets/img/cards/BRE-MAR.png"},
    {"cityA": "London", "cityB": "Berlin", "points": 7, "path" : "ZugumZug/assets/img/cards/LON-BER.png"},
    {"cityA": "Edinburgh", "cityB": "Paris", "points": 7, "path" : "ZugumZug/assets/img/cards/EDI-PAR.png"},
    {"cityA": "Amsterdam", "cityB": "Pamplona", "points": 7, "path" : "ZugumZug/assets/img/cards/AMS-PAM.png"},
    {"cityA": "Roma", "cityB": "Smyrna", "points": 8, "path" : "ZugumZug/assets/img/cards/ROM-SMY.png"},
    {"cityA": "Palermo", "cityB": "Constantinople", "points": 8, "path" : "ZugumZug/assets/img/cards/PAL-CON.png"},
    {"cityA": "Sarajevo", "cityB": "Sevastopol", "points": 8, "path" : "ZugumZug/assets/img/cards/SAR-SEV.png"},
    {"cityA": "Madrid", "cityB": "Dieppe", "points": 8, "path" : "ZugumZug/assets/img/cards/MAD-DIE.png"},
    {"cityA": "Barcelona", "cityB": "Bruxelles", "points": 8, "path" : "ZugumZug/assets/img/cards/BAR-BRU.png"},
    {"cityA": "Paris", "cityB": "Wien", "points": 8, "path" : "ZugumZug/assets/img/cards/PAR-WIE.png"},
    {"cityA": "Barcelona", "cityB": "Munchen", "points": 8, "path" : "ZugumZug/assets/img/cards/BAR-MUN.png"},
    {"cityA": "Brest", "cityB": "Venezia", "points": 8, "path" : "ZugumZug/assets/img/cards/BRE-VEN.png"},
    {"cityA": "Smolensk", "cityB": "Rostov", "points": 8, "path" : "ZugumZug/assets/img/cards/SMO-ROS.png"},
    {"cityA": "Marseille", "cityB": "Essen", "points": 8, "path" : "ZugumZug/assets/img/cards/MAR-ESS.png"},
    {"cityA": "Kyiv", "cityB": "Sochi", "points": 8, "path" : "ZugumZug/assets/img/cards/KYI-SOC.png"},
    {"cityA": "Madrid", "cityB": "Zurich", "points": 8, "path" : "ZugumZug/assets/img/cards/MAD-ZUR.png"},
    {"cityA": "Berlin", "cityB": "Bucuresti", "points": 8, "path" : "ZugumZug/assets/img/cards/BER-BUC.png"},
    {"cityA": "Bruxelles", "cityB": "Danzig", "points": 9, "path" : "ZugumZug/assets/img/cards/BRU-DAN.png"},
    {"cityA": "Berlin", "cityB": "Roma", "points": 9, "path" : "ZugumZug/assets/img/cards/BER-ROM.png"},
    {"cityA": "Angora", "cityB": "Kharkov", "points": 10, "path" : "ZugumZug/assets/img/cards/ANG-KHA.png"},
    {"cityA": "Riga", "cityB": "Bucuresti", "points": 10, "path" : "ZugumZug/assets/img/cards/RIG-BUC.png"},
    {"cityA": "Essen", "cityB": "Kyiv", "points": 10, "path" : "ZugumZug/assets/img/cards/ESS-KYI.png"},
    {"cityA": "Venezia", "cityB": "Constantinople", "points": 10, "path" : "ZugumZug/assets/img/cards/VEN-CON.png"},
    {"cityA": "London", "cityB": "Wien", "points": 10, "path" : "ZugumZug/assets/img/cards/LON-WIE.png"},
    {"cityA": "Athina", "cityB": "Wilno", "points": 11, "path" : "ZugumZug/assets/img/cards/ATH-WIL.png"},
    {"cityA": "Stockholm", "cityB": "Wien", "points": 11, "path" : "ZugumZug/assets/img/cards/STO-WIE.png"},
    {"cityA": "Berlin", "cityB": "Moskva", "points": 12, "path" : "ZugumZug/assets/img/cards/BER-MOS.png"},
    {"cityA": "Amsterdam", "cityB": "Wilno", "points": 12, "path" : "ZugumZug/assets/img/cards/AMS-WIL.png"},
    {"cityA": "Frankfurt", "cityB": "Smolensk", "points": 13, "path" : "ZugumZug/assets/img/cards/FRA-SMO.png"},
    # -- die 6 langen Strecken --
    {"cityA": "Lisboa", "cityB": "Danzig", "points": 20, "path" : "ZugumZug/assets/img/cards/LIS-DAN.png"},
    {"cityA": "Brest", "cityB": "Petrograd", "points": 20, "path" : "ZugumZug/assets/img/cards/BRE-PET.png"},
    {"cityA": "Palermo", "cityB": "Moskva", "points": 20, "path" : "ZugumZug/assets/img/cards/PAL-MOS.png"},
    {"cityA": "Kobenhavn", "cityB": "Erzurum", "points": 21, "path" : "ZugumZug/assets/img/cards/KOB-ERZ.png"},
    {"cityA": "Edinburgh", "cityB": "Athina", "points": 21, "path" : "ZugumZug/assets/img/cards/EDI-ATH.png"},
    {"cityA": "Cadiz", "cityB": "Stockholm", "points": 21, "path" : "ZugumZug/assets/img/cards/CAD-STO.png"},
]

GAME_TITLE = 'Zug um Zug'

#UI
WINDOW_HEIGHT = 720
WINDOW_WIDTH = 1280

FONT_SIZE = 20

MAP_PATH = "ZugumZug/assets/img/map/map.png"
PATHS_WAGGON_CARDS = {
    "pink" : "ZugumZug/assets/img/cards/oink_waggon.png", 
    "white" : "ZugumZug/assets/img/cards/white_waggon.png", 
    "blue" : "ZugumZug/assets/img/cards/blue_waggon.png", 
    "yellow" : "ZugumZug/assets/img/cards/yellow_waggon.png", 
    "orange" : "ZugumZug/assets/img/cards/orange_waggon.png", 
    "black" : "ZugumZug/assets/img/cards/black_waggon.png", 
    "red" : "ZugumZug/assets/img/cards/red_waggon.png", 
    "green" : "ZugumZug/assets/img/cards/green_waggon.png"
}

PATHS_ROUTE_CARDS = {

}