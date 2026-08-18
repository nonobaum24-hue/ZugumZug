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

    def draw_buttons_dis_and_acc(self, x_Value):
        text_size = measure_text('Discard', FONT_SIZE)
        draw_rectangle(x_Value-text_size//2, WINDOW_HEIGHT-WINDOW_HEIGHT//4-text_size//2, text_size, int(FONT_SIZE *1.2), RED)
        draw_text('Discard', x_Value-text_size//2, WINDOW_HEIGHT-WINDOW_HEIGHT//4-text_size//2, FONT_SIZE, WHITE)
        rectangle_discard = Rectangle(x_Value-text_size//2, WINDOW_HEIGHT-WINDOW_HEIGHT//4-text_size//2, text_size, FONT_SIZE *1.1)

        #Accept Button
        text_size = measure_text('Accept', FONT_SIZE)
        draw_rectangle(x_Value-text_size//2, WINDOW_HEIGHT-WINDOW_HEIGHT//6-text_size//2, text_size, int(FONT_SIZE *1.2), GREEN)
        draw_text('Accept', x_Value-text_size//2, WINDOW_HEIGHT-WINDOW_HEIGHT//6-text_size//2, FONT_SIZE, WHITE)
        rectangle_accept = Rectangle(x_Value-text_size//2, WINDOW_HEIGHT-WINDOW_HEIGHT//6-text_size//2, text_size, FONT_SIZE *1.1)

        return rectangle_discard, rectangle_accept
    
    def draw_routecard_acceptance(self, route_cards):
        rclist = route_cards
        rectangles = {}
        x_Value = WINDOW_WIDTH // 4
        for card in rclist:
            rc = load_texture(card["path"])
            draw_texture(rc, x_Value - rc.width//2, WINDOW_HEIGHT//3, WHITE) 
            rec_dis, rec_acc = self.draw_buttons_dis_and_acc(x_Value)
            rectangles.update({card:{'discard_rec': rec_dis, 'accept_rec': rec_acc, 'choice' = None}})
            x_Value += WINDOW_WIDTH//4

        return rectangles

    def check_if_everything_checked(diction):
        for i in diction:
            sub_dict = i[card]
            if sub_dict['choice'] == None:
                return False
        return True

    def start_game(self):
        given_cards = {}
        for i in self.m.players: 
            given_cards.update({i:self.m.handleDrawRouteCards()})
        
        while not window_should_close():
            #drawing

            begin_drawing()

            rectangles = self.draw_routecard_acceptance()

            end_drawing()

            #input

            if is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT):
                mouse_pos = get_mouse_position()
                for i in rectangles.values:
                    for rectangle in i:
                        if check_collision_point_rec(mouse_pos, rectangle['acc_rec']):
                            i.update({'choice': 'accepted'})
                        elif check_collision_point_rec(mouse_pos, rectangle['dis_rec']):
                            i.update({'choice': 'discarded'})

            if self.check_if_everything_checked(rectangles):
                self.m.nextPlayer()
                