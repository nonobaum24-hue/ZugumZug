from mechanicClasses import *

class game:

    def __init__(self, pManager, board):
        self.m = pManager
        self.b = board

        init_window(WINDOW_WIDTH, WINDOW_HEIGHT, GAME_TITLE)
        self.BIEDERMEIER = load_font(BIEDERMEIER_PATH)

        #select random first player
        self.m.currentPlayerIndex = randint(0, len(self.m.players)-1)

    def compute_buttons_dis_and_acc(self, x_center, bottom_margin):
        """Berechnet nur die Rechtecke (Position/Größe) für Discard/Accept,
        zeichnet aber nichts. Buttons sind nur ein kleines Stück größer als
        ihr Text (Padding) und liegen mittig unter x_center. Verankert von
        UNTEN (bottom_margin = Abstand des Accept-Buttons zum Fensterrand),
        damit beide Buttons bei jeder Fenstergröße sichtbar bleiben, statt
        wie vorher unten abgeschnitten zu werden. Wird beim Aufbau des
        Zustands pro Spielerzug gebraucht (siehe build_card_state)."""
        padding_x = FONT_SIZE
        padding_y = FONT_SIZE // 2
        gap_between_buttons = FONT_SIZE // 2

        text_size = measure_text_ex(self.BIEDERMEIER, 'Accept', FONT_SIZE*3, 1)
        accept_w = text_size.x + 2*padding_x
        accept_h = text_size.y + 2*padding_y
        accept_y = WINDOW_HEIGHT - bottom_margin - accept_h
        rectangle_accept = Rectangle(x_center - accept_w/2, accept_y, accept_w, accept_h)

        text_size = measure_text_ex(self.BIEDERMEIER, 'Discard', FONT_SIZE*3, 1)
        discard_w = text_size.x + 2*padding_x
        discard_h = text_size.y + 2*padding_y
        discard_y = accept_y - gap_between_buttons - discard_h
        rectangle_discard = Rectangle(x_center - discard_w/2, discard_y, discard_w, discard_h)

        return rectangle_discard, rectangle_accept

    def build_card_state(self, route_cards):
        """Baut EINMAL pro Spielerzug das Datenmodell für die Zielkarten-Auswahl
        auf (Buttons + choice=None). Wichtig: das darf NICHT jeden Frame neu
        aufgerufen werden, sonst geht jede Auswahl sofort wieder verloren.

        Die Spalten (eine pro Karte) werden spiegelbildlich über die
        Fensterbreite verteilt, mit gleich großem Rand (column_margin) links
        und rechts sowie gleich großen Abständen zwischen den Spalten - die
        Buttons UND die Kartenbilder werden auf denselben x_center gelegt.
        Die Kartenbreite wird proportional zur Spaltenbreite berechnet
        (card_target_width), statt fest auf SCALE*0.1 - das war vorher immer
        ~70px, egal wie viel Platz eigentlich da war.

        Nutzt card['path'] als Key statt der Karte selbst, weil Dicts nicht
        hashbar sind und ALL_ROUTE_CARDS-Einträge Dicts sind."""
        rectangles = {}
        n = len(route_cards)
        column_margin = WINDOW_WIDTH // 15
        usable_width = WINDOW_WIDTH - 2 * column_margin
        column_width = usable_width / n
        card_target_width = column_width * 0.75
        card_y = WINDOW_HEIGHT // 8
        bottom_margin = WINDOW_HEIGHT // 12

        for i, card in enumerate(route_cards):
            x_center = column_margin + column_width * (i + 0.5)
            rec_dis, rec_acc = self.compute_buttons_dis_and_acc(x_center, bottom_margin)
            key = card["path"]
            rectangles[key] = {
                'card': card, 'discard_rec': rec_dis, 'accept_rec': rec_acc, 'choice': None,
                'card_target_width': card_target_width, 'card_y': card_y,
            }

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
            # Skalierung proportional zur gewünschten Zielbreite statt einem
            # festen SCALE*0.1 - so nutzt die Karte den tatsächlich
            # verfügbaren Spaltenplatz aus, egal wie groß das Originalbild ist.
            card_scale = entry['card_target_width'] / rc.width *1.2
            draw_texture_ex(rc, Vector2(x_center - (rc.width*card_scale)/2, entry['card_y']), 0, card_scale, WHITE)

            #Discard Button
            draw_rectangle_rec(dr, RED)
            text_size = measure_text_ex(self.BIEDERMEIER, 'Discard', FONT_SIZE*3, 1)
            text_x = dr.x + (dr.width - text_size.x) / 2
            text_y = dr.y + (dr.height - text_size.y) / 2
            draw_text_ex(self.BIEDERMEIER, 'Discard', Vector2(int(text_x), int(text_y)), FONT_SIZE*3, 1, WHITE)

            #Accept Button
            draw_rectangle_rec(ar, GREEN)
            text_size = measure_text_ex(self.BIEDERMEIER, 'Accept', FONT_SIZE*3, 1)
            text_x = ar.x + (ar.width - text_size.x) / 2
            text_y = ar.y + (ar.height - text_size.y) / 2
            draw_text_ex(self.BIEDERMEIER, 'Accept', Vector2(int(text_x), int(text_y)), FONT_SIZE*3, 1, WHITE)

    def check_if_everything_checked(self, diction):
        for entry in diction.values():
            if entry['choice'] is None:
                return False
        return True

    def show_checked_recs(self, rectangles):
        for i in rectangles.values():
            if i['choice'] == 'accepted':
                rectangle = i['accept_rec']
                draw_rectangle_pro(rectangle, Vector2(0,0), 0, BLACK)
            elif i['choice'] == 'discarded':
                rectangle = i['discard_rec']
                draw_rectangle_pro(rectangle, Vector2(0,0), 0, BLACK)

    def start_game(self):
        should_start_game = False
        given_cards = {}
        for player in self.m.players:
            given_cards[player] = self.m.handleDrawRouteCards()

        current_player = self.m.getCurrentPlayer()
        rectangles = self.build_card_state(given_cards[current_player])
        players_handled = 0

        while not window_should_close() and not should_start_game:
            #drawing
            begin_drawing()
            self.draw_routecard_acceptance(rectangles)
            self.show_checked_recs(rectangles)
            end_drawing()

            #input
            if is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT) or is_mouse_button_pressed(rl.MOUSE_BUTTON_MIDDLE):
                mouse_pos = get_mouse_position()
                for entry in rectangles.values():
                    if check_collision_point_rec(mouse_pos, entry['accept_rec']):
                        entry['choice'] = 'accepted'
                    elif check_collision_point_rec(mouse_pos, entry['discard_rec']):
                        entry['choice'] = 'discarded'

            if self.check_if_everything_checked(rectangles):
                kept = [entry['card'] for entry in rectangles.values() if entry['choice'] == 'accepted']
                if len(kept) < 1:
                    for entry in rectangles.values():
                        entry['choice'] = None
                else:
                    self.m.handleKeepRouteCards(given_cards[current_player], kept)
                    self.m.nextPlayer()
                    current_player = self.m.getCurrentPlayer()
                    rectangles = self.build_card_state(given_cards[current_player])
                    players_handled += 1
                    if players_handled == len(self.m.players):
                        should_start_game = True
            clear_background(BLACK)

    def draw_action_options(self):
        begin_drawing()
        clear_background(RAYWHITE)
        self.draw_ui()
        draw_rectangle(0,0,WINDOW_WIDTH, WINDOW_HEIGHT, (0,0,0,50))

        # Drei Optionen nebeneinander auf 1/4, 2/4 (Mitte) und 3/4 der Fensterbreite,
        # jeweils um die eigene Textur-Breite zentriert.
        occupy_choice = load_texture("ZugumZug/game/assets/img/choice/occupy.png")
        occupy_x = WINDOW_WIDTH//4 - occupy_choice.width//2
        draw_texture(occupy_choice, occupy_x, WINDOW_HEIGHT//2-occupy_choice.height//2, WHITE)
        rec_occupy = Rectangle(occupy_x, WINDOW_HEIGHT//2-occupy_choice.height//2, occupy_choice.width, occupy_choice.height)

        waggon_choice = load_texture("ZugumZug/game/assets/img/choice/waggon.png")
        waggon_x = WINDOW_WIDTH//2 - waggon_choice.width//2
        draw_texture(waggon_choice, waggon_x, WINDOW_HEIGHT//2-waggon_choice.height//2, WHITE)
        rec_waggon = Rectangle(waggon_x, WINDOW_HEIGHT//2-waggon_choice.height//2, waggon_choice.width, waggon_choice.height)

        route_card_choice = load_texture("ZugumZug/game/assets/img/choice/route_card.png")
        route_x = WINDOW_WIDTH*3//4 - route_card_choice.width//2
        draw_texture(route_card_choice, route_x, WINDOW_HEIGHT//2-route_card_choice.height//2, WHITE)
        rec_route = Rectangle(route_x, WINDOW_HEIGHT//2-route_card_choice.height//2, route_card_choice.width, route_card_choice.height)
        end_drawing()

        return rec_occupy, rec_waggon, rec_route

    def draw_all_route_recs(self):
        """TODO: zeichnet aktuell noch nichts - die Strecken-Rechtecke fuers
        Board sind hier noch nicht implementiert. Vorher fehlte diese Methode
        komplett, obwohl draw_ui() sie aufruft (AttributeError)."""
        pass

    def draw_ui(self):

        #draw Map
        europe_map = load_texture("ZugumZug/game/assets/img/main_game_ui/map.png")
        if europe_map.width == 0:
            # Textur konnte nicht geladen werden (fehlendes/leeres Asset) -
            # ohne diese Absicherung fuehrt die Division unten zu einem
            # ZeroDivisionError.
            print("WARNUNG: map.png konnte nicht geladen werden, Karte wird nicht gezeichnet.")
        else:
            map_scale = WINDOW_WIDTH/europe_map.width
            draw_texture_ex(europe_map, Vector2(0,0), 0, map_scale, WHITE)

        #draw routes
        self.draw_all_route_recs()


    def choose_action(self):
        while True:
            rec_occupy, rec_waggon, rec_route = self.draw_action_options()
            actions = [rec_occupy, rec_waggon, rec_route]
            if is_mouse_button_released(rl.MOUSE_BUTTON_LEFT):
                mouse_pos = get_mouse_position()
                for action in actions:
                    if check_collision_point_rec(mouse_pos, action):
                        return actions.index(action)

    def draw_start_button(self):
        text = measure_text_ex(self.BIEDERMEIER, 'Start Round', FONT_SIZE, 1)
        x = int(WINDOW_WIDTH//2-text.x/2)
        y = WINDOW_HEIGHT//10
        draw_text_ex(self.BIEDERMEIER, "Start Round", Vector2(x, y), FONT_SIZE, 1, BLACK)
        draw_rectangle(x, y, int(text.x), int(text.y), GREEN)
        return Rectangle(x, y, text.x, text.y)

    def idle_screen(self):
        ready = False
        while ready != True:
            begin_drawing()
            self.draw_ui()
            start_button = self.draw_start_button()
            #input
            if is_mouse_button_released(rl.MOUSE_BUTTON_LEFT):
                mouse_pos = get_mouse_position()
                if check_collision_point_rec(mouse_pos, start_button): ready = True
            if is_key_down(rl.KEY_SPACE): self.show_route_cards()
            if is_key_down(rl.KEY_LEFT_SHIFT): self.show_waggon_cards()
            end_drawing()

    def show_waggon_cards(self):
        """Zeigt alle Waggonkarten-Stapel mit Anzahl nebeneinander an.
        Nutzt die echten Pfade aus PATHS_WAGGON_CARDS (settings.py) statt
        eines falschen, nicht existierenden Verzeichnisses, und teilt die
        Fensterbreite gleichmäßig auf die 8 Farben auf, statt sie mit der
        vollen WINDOW_WIDTH weit außerhalb des Fensters zu platzieren."""
        current_player = self.m.getCurrentPlayer()
        column_width = WINDOW_WIDTH // len(WAGGON_COLOURS)
        colour_index = 0
        for colour in WAGGON_COLOURS:
            card_text = load_texture(PATHS_WAGGON_CARDS[colour])
            x_pos = column_width * colour_index
            draw_texture(card_text, x_pos, WINDOW_HEIGHT//2-card_text.height//2, BLACK)
            count = str(current_player.waggonCards.count(colour))
            text = measure_text_ex(self.BIEDERMEIER, count, FONT_SIZE, 1)
            draw_text(colour, int(x_pos+card_text.width//2-text.x//2), int(WINDOW_HEIGHT//2-card_text.height//2-text.y), FONT_SIZE*4, WHITE)
            colour_index += 1

    def sort_route_cards_into_pages(self):
        """Teilt die Zielkarten des aktuellen Spielers in 6er-Seiten auf.
        Vorher wurde current_player selbst statt current_player.routeCards
        indiziert (Player ist nicht indizierbar), und es landete pro
        6er-Block nur 1 Karte auf der Seite statt 6."""
        current_player = self.m.getCurrentPlayer()
        pages = {}
        page = []
        page_index = 0
        for cards_index, card in enumerate(current_player.routeCards):
            page.append(card)
            if (cards_index + 1) % 6 == 0:
                pages[page_index] = page
                page = []
                page_index += 1
        if page:
            pages[page_index] = page
        return pages

    def show_route_card_page(self, page):
        """pages[page] ist bereits die Liste der Karten dieser Seite - .values
        gehört zu dict, nicht zu list. Außerdem wurde 'card' (das Texture-
        Objekt) statt 'card.width' mit 1.5 multipliziert."""
        pages = self.sort_route_cards_into_pages()
        cards = pages.get(page, [])
        for i, card_data in enumerate(cards):
            card = load_texture(card_data["path"])
            draw_texture_ex(card, Vector2(WINDOW_WIDTH//2-card.width*1.5+((i+1)*card.width), WINDOW_HEIGHT//2-card.height*1.5), 0, SCALE, WHITE)

    def draw_page_buttons(self):
        arrow = load_texture("ZugumZug/game/assets/img/choice/arrow.png")
        draw_texture_ex(arrow, Vector2(arrow.width*1.5, WINDOW_HEIGHT//2+arrow.height//2), 180, SCALE, WHITE)
        rec_last_page = Rectangle(arrow.width/2, WINDOW_HEIGHT//2-arrow.height//2, arrow.width, arrow.height)

        draw_texture_ex(arrow, Vector2(WINDOW_WIDTH-1.5*arrow.width, WINDOW_HEIGHT//2-arrow.height), 0, SCALE, WHITE)
        rec_next_page = Rectangle(WINDOW_WIDTH-1.5*arrow.width, WINDOW_HEIGHT//2-arrow.height, arrow.width, arrow.height)

        return rec_last_page, rec_next_page

    def show_route_cards(self):
        # draw_page_buttons() gibt (rec_last_page, rec_next_page) zurück - vorher
        # wurde beim Entpacken die Reihenfolge vertauscht, sodass "vor" und
        # "zurück" ihre Bedeutung tauschten.
        rec_last_page, rec_next_page = self.draw_page_buttons()
        page = 0
        should_return = False
        while not should_return:
            self.show_route_card_page(page)
            if is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT):
                mouse_pos = get_mouse_position()
                if check_collision_point_rec(mouse_pos, rec_next_page): page += 1
                elif check_collision_point_rec(mouse_pos, rec_last_page): page -= 1
            elif is_key_pressed(rl.KEY_SPACE): should_return = True


    def occupy_screen(self):
        """TODO: Strecken-Beanspruchung ist im grafischen Loop noch nicht
        implementiert (existiert bisher nur in der Konsolen-Variante
        gameLoop.py als _handleClaimRoute). Platzhalter, damit game_loop
        nicht crasht."""
        pass

    def game_loop(self):
        while not window_should_close():
            self.idle_screen()
            # choose_action() muss AUFGERUFEN werden (fehlende Klammern
            # verglichen vorher eine Methodenreferenz mit 0/1/2, was nie
            # zutraf). Die Ziel-Methoden hiessen ausserdem anders als die
            # tatsaechlich definierten (show_waggon_cards/show_route_cards).
            choice = self.choose_action()
            if choice == 0: self.occupy_screen()
            elif choice == 1: self.show_waggon_cards()
            elif choice == 2: self.show_route_cards()
            self.m.nextPlayer()