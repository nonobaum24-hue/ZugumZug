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
        should_start_game = False
        given_cards = {}
        for player in self.m.players:
            given_cards[player] = self.m.handleDrawRouteCards()

        current_player = self.m.getCurrentPlayer()
        rectangles = self.build_card_state(given_cards[current_player])
        players_handled = 0

        while not window_should_close() and not should_start_game():
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
                    players_handled += 1
                    if players_handled == len(self.m.players):
                        should_start_game = True

    def draw_action_options(self):
        begin_drawing()
        clear_background()
        self.draw_ui()
        draw_rectangle(0,0,WINDOW_WIDTH, WINDOW_HEIGHT, (0,0,0,50))

        occupy_choice = load_texture("ZugumZug/game/assets/img/choice/occupy.png")
        draw_texture(occupy_choice, WINDOW_WIDTH//occupy_choice.width, WINDOW_HEIGHT//2-occupy_choice.height//2, WHITE)
        rec_occupy = Rectangle(WINDOW_WIDTH//occupy_choice.width, WINDOW_HEIGHT//2-occupy_choice.height//2, occupy_choice.width, occupy_choice.height)

        waggon_choice = load_texture("ZugumZug/game/assets/img/choice/waggon.png")
        draw_texture(waggon_choice, WINDOW_WIDTH//2-waggon_choice.width//2, WINDOW_HEIGHT//2-waggon_choice.height//2, WHITE)
        rec_waggon = Rectangle(WINDOW_WIDTH//waggon_choice.width, WINDOW_HEIGHT//2-waggon_choice.height//2, waggon_choice.width, waggon_choice.height)

        route_card_choice = load_texture("ZugumZug/game/assets/img/choice/route_card.png")
        draw_texture(route_card_choice, WINDOW_WIDTH-WINDOW_WIDTH-route_card_choice.width*2, WINDOW_HEIGHT//2-route_card_choice.height//2, WHITE)
        rec_route = Rectangle(WINDOW_WIDTH//route_card_choice.width, WINDOW_HEIGHT//2-route_card_choice.height//2, route_card_choice.width, route_card_choice.height)
        end_drawing()

        return rec_occupy, rec_waggon, rec_route

    def draw_ui(self):

        #draw Map
        europe_map = load_texture("ZugumZug/game/assets/img/main_game_ui/map.png")
        map_scale = WINDOW_WIDTH/europe_map.width
        draw_texture_ex(europe_map, Vector2(0,0), 0, map_scale, WHITE)

        #draw routes
        self.draw_all_route_recs()

        #Wagon Cards Widget
        waggon_card_aesth_stack = load_texture("ZugumZug/game/assets/img/main_game_ui/waggon_cards.png")
        draw_texture_ex(waggon_card_aesth_stack, Vector2(0,WINDOW_HEIGHT-waggon_card_aesth_stack.height), 0, SCALE, WHITE)

        #Wagon Cards Widget
        route_card_aesth_stack = load_texture("ZugumZug/game/assets/img/main_game_ui/route_cards.png")
        draw_texture_ex(route_card_aesth_stack, Vector2(WINDOW_WIDTH-route_card_aesth_stack,WINDOW_HEIGHT-route_card_aesth_stack.height), 0, SCALE, WHITE)

        #draw progress bar
        progress_bar = load_texture('ZugumZug/game/assets/img/main_game_ui/progress_bar.png')
        bar_scale = WINDOW_WIDTH/progress_bar.width
        draw_texture_ex(progress_bar, Vector2(0,0), 0, bar_scale, WHITE)


    def choose_action(self):
        while True:
            rec_occupy, rec_waggon, rec_route = self.draw_action_options
            actions = [rec_occupy, rec_waggon, rec_route]
            if is_mouse_button_released(rl.MOUSE_BUTTON_LEFT):
                mouse_pos = get_mouse_position
                for action in actions:
                    if check_collision_point_rec(mouse_pos, action):
                        return actions.index[action]

    def draw_start_button(self):
        text = measure_text_ex(BIEDERMEIER, 'Start Round', FONT_SIZE, 1)
        draw_text_ex(BIEDERMEIER, "Start Round", Vector2(WINDOW_WIDTH//2-text.x/2, WINDOW_HEIGHT//10), FONT_SIZE, 1, BLACK)
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
            if is_key_pressed(rl.KEY_SPACE): self.show_route_cards()
            if is_key_pressed(rl.KEY_LEFT_SHIFT): self.show_waggon_cards()

    def show_waggon_cards(self):
        current_player = self.m.getCurrentPlayer()
        colour_index = 1
        for colour in range(WAGGON_COLOURS):
            card_text = load_texture("ZugumZug/game/assets/img/waggons/"+colour)
            draw_texture(card_text, WINDOW_WIDTH*colour_index, WINDOW_HEIGHT//2-card_text//2, BLACK)
            count = current_player.waggonCards.count(colour)
            text = measure_text_ex(BIEDERMEIER, count, FONT_SIZE, 1)
            draw_text(colour, WINDOW_WIDTH*colour_index+card_text.width//2-text.x//2, WINDOW_HEIGHT//2-card_text.height//2-text.y, FONT_SIZE*4, WHITE)



    def game_loop(self):
        while not window_should_close():
            self.idle_screen()
            choice = self.choose_action
            if choice == 0: self.occupy_screen()
            elif choice == 1: self.draw_waggon_cards_screen
            elif choice == 2: self.draw_route_cards_screen
            self.m.nextplayer()
