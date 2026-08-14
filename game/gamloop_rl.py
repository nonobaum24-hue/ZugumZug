from mechanicClasses import * 

class game:
    def __init__(self, pManager, board):
        self.pManager = pManager
        self.board = board

        init_window(WINDOW_HEIGHT, WINDOW_WIDTH, GAME_TITLE)

    def start_game(self):
        
