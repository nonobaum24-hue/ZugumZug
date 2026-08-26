from mechanicClasses import *

class game:

    def __init__(self, pManager, board):
        self.m = pManager
        self.b = board

        init_window(WINDOW_WIDTH, WINDOW_HEIGHT, GAME_TITLE)
        self.BIEDERMEIER = load_font(BIEDERMEIER_PATH)

        #select random first player
        self.m.currentPlayerIndex = randint(0, len(self.m.players)-1)

    def compute_buttons_dis_and_acc(self, x_Value, y_value):
        """Berechnet nur die Rechtecke (Position/Größe) für Discard/Accept,
        zeichnet aber nichts. Wird beim Aufbau des Zustands pro Spielerzug
        gebraucht (siehe build_card_state)."""
        text_size = measure_text_ex(self.BIEDERMEIER, 'Discard', FONT_SIZE*3, 1)
        rectangle_discard = Rectangle(x_Value-text_size.x, y_value-text_size.y, text_size.x*2, text_size.y*2)

        text_size = measure_text_ex(self.BIEDERMEIER, 'Accept', FONT_SIZE*3, 1)
        rectangle_accept = Rectangle(x_Value-text_size.x, y_value + text_size.y, text_size.x*2, text_size.y*2)

        return rectangle_discard, rectangle_accept

    def build_card_state(self, route_cards):
        """Baut EINMAL pro Spielerzug das Datenmodell für die Zielkarten-Auswahl
        auf (Buttons + choice=None). Wichtig: das darf NICHT jeden Frame neu
        aufgerufen werden, sonst geht jede Auswahl sofort wieder verloren.

        Nutzt card['path'] als Key statt der Karte selbst, weil Dicts nicht
        hashbar sind und ALL_ROUTE_CARDS-Einträge Dicts sind."""
        rectangles = {}
        x_Value = WINDOW_WIDTH // 4
        y_Value = WINDOW_HEIGHT - WINDOW_HEIGHT//5
        for card in route_cards:
            rec_dis, rec_acc = self.compute_buttons_dis_and_acc(x_Value, y_Value)
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
            draw_texture_ex(rc, Vector2(x_center - rc.width//2, WINDOW_HEIGHT//3), 0, SCALE*0.1, WHITE)

            #Discard Button
            draw_rectangle_rec(dr, RED)
            draw_text_ex(self.BIEDERMEIER, 'Discard', Vector2(int(dr.x), int(dr.y)), FONT_SIZE*3, 1, WHITE)

            #Accept Button
            draw_rectangle_rec(ar, GREEN)
            draw_text_ex(self.BIEDERMEIER, 'Accept', Vector2(int(ar.x), int(ar.y)), FONT_SIZE*3, 1, WHITE)

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
            if is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT):
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

        #Wagon Cards Widget
        waggon_card_aesth_stack = load_texture("ZugumZug/game/assets/img/main_game_ui/waggon_cards.png")
        draw_texture_ex(waggon_card_aesth_stack, Vector2(0,WINDOW_HEIGHT-waggon_card_aesth_stack.height), 0, SCALE, WHITE)

        #Wagon Cards Widget
        route_card_aesth_stack = load_texture("ZugumZug/game/assets/img/main_game_ui/route_cards.png")
        draw_texture_ex(route_card_aesth_stack, Vector2(WINDOW_WIDTH-route_card_aesth_stack.width,WINDOW_HEIGHT-route_card_aesth_stack.height), 0, SCALE, WHITE)

        #draw progress bar
        progress_bar = load_texture('ZugumZug/game/assets/img/main_game_ui/progress_bar.png')
        if progress_bar.width == 0:
            print("WARNUNG: progress_bar.png konnte nicht geladen werden, Fortschrittsbalken wird nicht gezeichnet.")
        else:
            bar_scale = WINDOW_WIDTH/progress_bar.width
            draw_texture_ex(progress_bar, Vector2(0,0), 0, bar_scale, WHITE)


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
        draw_text_ex(self.BIEDERMEIER, "Start Round", Vector2(WINDOW_WIDTH//2-text.x/2, WINDOW_HEIGHT//10), FONT_SIZE, 1, BLACK)
        draw_rectangle(WINDOW_WIDTH//2-text.x/2, WINDOW_HEIGHT//10, text.x, text.y, GREEN)
        return Rectangle(WINDOW_WIDTH//2-text.x/2, WINDOW_HEIGHT//10, text.x, text.y)

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