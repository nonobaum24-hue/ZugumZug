"""
Generiert alle Zielkarten-Bilder (destination tickets) fuer ZugumZug aus der
Vorlage routecard_blank.png:

- Oben ins rechteckige Feld: "StadtA - StadtB" (bei Overflow zweizeilig,
  jeweils zentriert)
- Unten rechts ins runde Feld: die Punktzahl, in BiedermeierKursiv (der
  Font, der schon im Projekt unter game/assets/fonts liegt)
- In der Mitte: StadtA und StadtB als roter Punkt an ihrer ungefaehren
  geografischen Position auf der Karte (Koordinaten wurden anhand der
  sichtbaren Kuestenlinien/Grenzen dieser konkreten Kartenvorlage von Hand
  kalibriert, siehe city_coords.py)

Speichert jede Karte unter <OUTPUT_DIR>/<CODE>.png, z.B.
game/assets/img/cards/BUD-SOF.png - identisch zu den "path"-Eintraegen in
ALL_ROUTE_CARDS (settings.py).
"""

import os
from PIL import Image, ImageDraw, ImageFont

from city_coords import CITY_PIXELS

# -----------------------------------------------------------------------
# Konfiguration
# -----------------------------------------------------------------------

# Absolut statt relativ zum aktuellen Arbeitsverzeichnis - so funktioniert
# das Skript egal von wo aus es aufgerufen wird (z.B. "python3
# routecard_generator/generate_route_cards.py" aus dem Repo-Root).
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)

TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "routecard_blank.png")
# Die Schriftart liegt nicht im routecard_generator-Ordner selbst, sondern
# wird aus game/assets/fonts wiederverwendet (dieselbe Datei, die auch
# gamloop_rl.py fuers Spiel laedt).
FONT_PATH = os.path.join(REPO_ROOT, "game", "assets", "fonts", "BiedermeierKursiv.ttf")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output_cards")   # lokal zum Testen
# Wenn direkt im Repo erzeugt wird (siehe run_batch.py), zeigt das hierher:
# OUTPUT_DIR = os.path.join(REPO_ROOT, "game", "assets", "img", "cards")

TITLE_BOX = (220, 75, 1180, 195)     # (x0, y0, x1, y1) - beschreibbarer Bereich oben
TITLE_COLOR = (55, 35, 20)
TITLE_MAX_FONT = 84
TITLE_MIN_FONT = 34
TITLE_LINE_GAP = 6

POINTS_CENTER = (1230, 845)          # gemessene tatsaechliche Kreismitte in
                                      # der Vorlage (war vorher (1155, 785),
                                      # was spuerbar daneben lag - siehe
                                      # Kommentar unten)
POINTS_RADIUS = 115                  # nutzbarer Innenradius, mit etwas
                                      # Sicherheitsabstand zum goldenen Ring
POINTS_COLOR = (25, 15, 10)
POINTS_FONT_SIZE = 250

DOT_RADIUS = 9
DOT_FILL = (196, 30, 30)
DOT_OUTLINE = (40, 10, 10)
DOT_OUTLINE_WIDTH = 2

# Die 40 Zielkarten aus settings.py (ALL_ROUTE_CARDS), hier ohne pyray-
# Abhaengigkeit noch einmal als reine Daten hinterlegt, plus dem
# Datei-Code (aus dem "path"-Feld abgeleitet).
ROUTE_CARDS = [
    ("Athina", "Angora", 5, "ATH-ANG"),
    ("Budapest", "Sofia", 5, "BUD-SOF"),
    ("Frankfurt", "Kobenhavn", 5, "FRA-KOB"),
    ("Rostov", "Erzurum", 5, "ROS-ERZ"),
    ("Sofia", "Smyrna", 5, "SOF-SMY"),
    ("Kyiv", "Petrograd", 6, "KYI-PET"),
    ("Zurich", "Brindisi", 6, "ZUR-BRI"),
    ("Zurich", "Budapest", 6, "ZUR-BUD"),
    ("Warszawa", "Smolensk", 6, "WAR-SMO"),
    ("Zagrab", "Brindisi", 6, "ZAG-BRI"),
    ("Paris", "Zagrab", 7, "PAR-ZAG"),
    ("Brest", "Marseille", 7, "BRE-MAR"),
    ("London", "Berlin", 7, "LON-BER"),
    ("Edinburgh", "Paris", 7, "EDI-PAR"),
    ("Amsterdam", "Pamplona", 7, "AMS-PAM"),
    ("Roma", "Smyrna", 8, "ROM-SMY"),
    ("Palermo", "Constantinople", 8, "PAL-CON"),
    ("Sarajevo", "Sevastopol", 8, "SAR-SEV"),
    ("Madrid", "Dieppe", 8, "MAD-DIE"),
    ("Barcelona", "Bruxelles", 8, "BAR-BRU"),
    ("Paris", "Wien", 8, "PAR-WIE"),
    ("Barcelona", "Munchen", 8, "BAR-MUN"),
    ("Brest", "Venezia", 8, "BRE-VEN"),
    ("Smolensk", "Rostov", 8, "SMO-ROS"),
    ("Marseille", "Essen", 8, "MAR-ESS"),
    ("Kyiv", "Sochi", 8, "KYI-SOC"),
    ("Madrid", "Zurich", 8, "MAD-ZUR"),
    ("Berlin", "Bucuresti", 8, "BER-BUC"),
    ("Bruxelles", "Danzig", 9, "BRU-DAN"),
    ("Berlin", "Roma", 9, "BER-ROM"),
    ("Angora", "Kharkov", 10, "ANG-KHA"),
    ("Riga", "Bucuresti", 10, "RIG-BUC"),
    ("Essen", "Kyiv", 10, "ESS-KYI"),
    ("Venezia", "Constantinople", 10, "VEN-CON"),
    ("London", "Wien", 10, "LON-WIE"),
    ("Athina", "Wilno", 11, "ATH-WIL"),
    ("Stockholm", "Wien", 11, "STO-WIE"),
    ("Berlin", "Moskva", 12, "BER-MOS"),
    ("Amsterdam", "Wilno", 12, "AMS-WIL"),
    ("Frankfurt", "Smolensk", 13, "FRA-SMO"),
    ("Lisboa", "Danzig", 20, "LIS-DAN"),
    ("Brest", "Petrograd", 20, "BRE-PET"),
    ("Palermo", "Moskva", 20, "PAL-MOS"),
    ("Kobenhavn", "Erzurum", 21, "KOB-ERZ"),
    ("Edinburgh", "Athina", 21, "EDI-ATH"),
    ("Cadiz", "Stockholm", 21, "CAD-STO"),
]


# -----------------------------------------------------------------------
# Hilfsfunktionen
# -----------------------------------------------------------------------

def text_size(draw, text, font):
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    return r - l, b - t


def fit_title_font(draw, text, max_width):
    """Verkleinert die Schrift, bis der Text (einzeilig) in max_width passt.
    Gibt (font, passt_einzeilig) zurueck."""
    size = TITLE_MAX_FONT
    while size >= TITLE_MIN_FONT:
        font = ImageFont.truetype(FONT_PATH, size)
        w, _ = text_size(draw, text, font)
        if w <= max_width:
            return font, True
        size -= 2
    return ImageFont.truetype(FONT_PATH, TITLE_MIN_FONT), False


def draw_title(draw, city_a, city_b):
    x0, y0, x1, y1 = TITLE_BOX
    box_w = x1 - x0
    box_h = y1 - y0
    single_line = f"{city_a} - {city_b}"

    font, fits = fit_title_font(draw, single_line, box_w)

    if fits:
        cx = x0 + box_w / 2
        cy = y0 + box_h / 2
        draw.text((cx, cy), single_line, font=font, fill=TITLE_COLOR, anchor="mm")
        return

    # Passt auch bei Mindestgroesse nicht einzeilig -> zweizeilig, mittig
    font = ImageFont.truetype(FONT_PATH, TITLE_MIN_FONT)
    # Falls sogar eine einzelne Stadt bei Mindestgroesse zu breit waere,
    # weiter verkleinern.
    size = TITLE_MIN_FONT
    while size > 14 and (
        text_size(draw, city_a, font)[0] > box_w
        or text_size(draw, city_b, font)[0] > box_w
    ):
        size -= 2
        font = ImageFont.truetype(FONT_PATH, size)

    _, h1 = text_size(draw, city_a, font)
    _, h2 = text_size(draw, city_b, font)
    total_h = h1 + TITLE_LINE_GAP + h2
    cx = x0 + box_w / 2
    y1_pos = y0 + (box_h - total_h) / 2 + h1 / 2
    y2_pos = y1_pos + h1 / 2 + TITLE_LINE_GAP + h2 / 2

    draw.text((cx, y1_pos), city_a, font=font, fill=TITLE_COLOR, anchor="mm")
    draw.text((cx, y2_pos), city_b, font=font, fill=TITLE_COLOR, anchor="mm")


def draw_points(draw, points):
    text = str(points)
    size = POINTS_FONT_SIZE
    # Bei zweistelligen Zahlen etwas kleiner, damit sie sicher in den
    # Kreis passen.
    if len(text) > 1:
        size = int(POINTS_FONT_SIZE * 0.8)
    font = ImageFont.truetype(FONT_PATH, size)
    cx, cy = POINTS_CENTER
    draw.text((cx, cy), text, font=font, fill=POINTS_COLOR, anchor="mm")


def draw_city_dot(draw, city_name):
    if city_name not in CITY_PIXELS:
        raise KeyError(f"Keine Koordinaten fuer Stadt '{city_name}' hinterlegt.")
    x, y = CITY_PIXELS[city_name]
    r = DOT_RADIUS
    draw.ellipse(
        [x - r, y - r, x + r, y + r],
        fill=DOT_FILL,
        outline=DOT_OUTLINE,
        width=DOT_OUTLINE_WIDTH,
    )


def generate_card(city_a, city_b, points, code, output_dir):
    im = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(im)

    draw_title(draw, city_a, city_b)
    draw_points(draw, points)
    draw_city_dot(draw, city_a)
    draw_city_dot(draw, city_b)

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{code}.png")
    im.save(out_path)
    return out_path


def generate_all(output_dir=OUTPUT_DIR):
    paths = []
    for city_a, city_b, points, code in ROUTE_CARDS:
        paths.append(generate_card(city_a, city_b, points, code, output_dir))
    return paths


if __name__ == "__main__":
    paths = generate_all()
    print(f"{len(paths)} Karten erzeugt in '{OUTPUT_DIR}/'.")