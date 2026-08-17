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

    def draw_buttons_dis_and_acc(self):
        text_size = measure_text('Discard', FONT_SIZE)
        draw_rectangle(WINDOW_WIDTH//3-text_size//2, WINDOW_HEIGHT-WINDOW_HEIGHT//4-text_size//2, text_size, int(FONT_SIZE *1.2), RED)
        draw_text('Discard', WINDOW_WIDTH//3-text_size//2, WINDOW_HEIGHT-WINDOW_HEIGHT//4-text_size//2, FONT_SIZE, WHITE)
        rectangle_discard = Rectangle(WINDOW_WIDTH//3-text_size//2, WINDOW_HEIGHT-WINDOW_HEIGHT//4-text_size//2, text_size, FONT_SIZE *1.1)

        #Accept Button
        text_size = measure_text('Accept', FONT_SIZE)
        draw_rectangle(WINDOW_WIDTH//3*2-text_size//2, WINDOW_HEIGHT-WINDOW_HEIGHT//4-text_size//2, text_size, int(FONT_SIZE *1.2), GREEN)
        draw_text('Accept', WINDOW_WIDTH//3*2-text_size//2, WINDOW_HEIGHT-WINDOW_HEIGHT//4-text_size//2, FONT_SIZE, WHITE)
        rectangle_accept = Rectangle(WINDOW_WIDTH//3*-text_size//2, WINDOW_HEIGHT-WINDOW_HEIGHT//4-text_size//2, text_size, FONT_SIZE *1.1)

        return rectangle_discard, rectangle_accept
    
    def draw_routecard_acceptance(self, route_card):
        rec_dis, rec_acc = self.draw_buttons_dis_and_acc()
        rc = load_texture(route_card)
        draw_texture(rc, WINDOW_WIDTH//2-rc.width//2, WINDOW_HEIGHT//3, WHITE)
        return rec_dis, rec_acc


    def start_game(self):
        list_of_handled_players = []
        
        while not window_should_close():
            self.draw_routecard_acceptance())
