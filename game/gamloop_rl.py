from mechanicClasses import *

class game:
    def __init__(self, pManager, board):
        self.m = pManager
        self.b = board

        init_window(WINDOW_WIDTH, WINDOW_HEIGHT, GAME_TITLE)

        #select random first player
        self.m.currentPlayerIndex = randint(0, len(self.m.players)-1)

    def ask_route_card(self, route_card):
        pass

    def compute_buttons_dis_and_acc(self, x_Value):
        """Berechnet nur die Rechtecke (Position/Größe) für Discard/Accept,
        zeichnet aber nichts. Wird beim Aufbau des Zustands pro Spielerzug
        gebraucht (siehe build_card_state)."""
        text_size = measure_text('Discard', FONT_SIZE)
        rectangle_discard = Rectangle(x_Value-text_size//2, WINDOW_HEIGHT-WINDOW_HEIGHT//4-text_size//2, text_size, FONT_SIZE *1.2)

        text_size = measure_text('Accept', FONT_SIZE)
        rectangle_accept = Rectangle(x_Value-text_size//2, WINDOW_HEIGHT-WINDOW_HEIGHT//6-text_size//2, text_size, FONT_SIZE *1.2)

        return rectangle_discard, rectangle_accept

    def build_card_state(self, route_cards):
        """Baut EINMAL pro Spielerzug das Datenmodell für die Zielkarten-Auswahl
        auf (Buttons + choice=None). Wichtig: das darf NICHT jeden Frame neu
        aufgerufen werden, sonst geht jede Auswahl sofort wieder verloren.

        Nutzt card['path'] als Key statt der Karte selbst, weil Dicts nicht
        hashbar sind und ALL_ROUTE_CARDS-Einträge Dicts sind."""
        rectangles = {}
        x_Value = WINDOW_WIDTH // 4
        for card in route_cards:
            rec_dis, rec_acc = self.compute_buttons_dis_and_acc(x_Value)
            key = card["path"]
            rectangles[key] = {'card': card, 'discard_rec': rec_dis, 'accept_rec': rec_acc, 'choice': None}
            x_Value += WINDOW_WIDTH // 4

        return rectangles

    def draw_routecard_acceptance(self, rectangles):
        """Zeichnet jeden Frame die Karten + Buttons, basierend auf dem
        bereits bestehenden Zustand (rectangles). Verändert 'choice' nicht."""
        for entry in rectangles.values():
            card = entry['card']
            dr = entry['discard_rec']
            ar = entry['accept_rec']

            rc = load_texture(card["path"])
            x_center = int(dr.x + dr.width / 2)
            draw_texture(rc, x_center - rc.width//2, WINDOW_HEIGHT//3, WHITE)

            #Discard Button
            draw_rectangle(int(dr.x), int(dr.y), int(dr.width), int(dr.height), RED)
            draw_text('Discard', int(dr.x), int(dr.y), FONT_SIZE, WHITE)

            #Accept Button
            draw_rectangle(int(ar.x), int(ar.y), int(ar.width), int(ar.height), GREEN)
            draw_text('Accept', int(ar.x), int(ar.y), FONT_SIZE, WHITE)

    def check_if_everything_checked(self, diction):
        for entry in diction.values():
            if entry['choice'] is None:
                return False
        return True

    def start_game(self):
        given_cards = {}
        for player in self.m.players:
            given_cards[player] = self.m.handleDrawRouteCards()

        current_player = self.m.getCurrentPlayer()
        rectangles = self.build_card_state(given_cards[current_player])

        while not window_should_close():
            #drawing
            begin_drawing()
            self.draw_routecard_acceptance(rectangles)
            end_drawing()

            #input
            if is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT):
                mouse_pos = get_mouse_position()
                for entry in rectangles.values():
                    if check_collision_point_rec(mouse_pos, entry['accept_rec']):
                        entry['choice'] = 'accepted'
                    elif check_collision_point_rec(mouse_pos, entry['discard_rec']):
                        entry['choice'] = 'discarded'

            if self.check_if_everything_checked(rectangles):
                kept = [entry['card'] for entry in rectangles.values() if entry['choice'] == 'accepted']
                if len(kept) <= 1:
                    pass
                else:
                    self.m.handleKeepRouteCards(given_cards[current_player], kept)

                    self.m.nextPlayer()
                    current_player = self.m.getCurrentPlayer()
                    rectangles = self.build_card_state(given_cards[current_player])