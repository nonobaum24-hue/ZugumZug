from mechanicClasses import * 

init_window(WINDOW_WIDTH, WINDOW_HEIGHT, GAME_TITLE)

def draw_buttons():
    begin_drawing()

    text_size = measure_text('Discard', FONT_SIZE)
    draw_rectangle(WINDOW_WIDTH//3-text_size//2, WINDOW_HEIGHT-WINDOW_HEIGHT//4-text_size//2, text_size, int(FONT_SIZE *1.2), RED)
    draw_text('Discard', WINDOW_WIDTH//3-text_size//2, WINDOW_HEIGHT-WINDOW_HEIGHT//4-text_size//2, FONT_SIZE, WHITE)
    rectange_discard = Rectangle(WINDOW_WIDTH//3-text_size//2, WINDOW_HEIGHT-WINDOW_HEIGHT//4-text_size//2, text_size, FONT_SIZE *1.1)

    #Accept Button
    text_size = measure_text('Accept', FONT_SIZE)
    draw_rectangle(WINDOW_WIDTH//3*2-text_size//2, WINDOW_HEIGHT-WINDOW_HEIGHT//4-text_size//2, text_size, int(FONT_SIZE *1.2), GREEN)
    draw_text('Accept', WINDOW_WIDTH//3*2-text_size//2, WINDOW_HEIGHT-WINDOW_HEIGHT//4-text_size//2, FONT_SIZE, WHITE)
    rectange_accept = Rectangle(WINDOW_WIDTH//3*-text_size//2, WINDOW_HEIGHT-WINDOW_HEIGHT//4-text_size//2, text_size, FONT_SIZE *1.1)

    end_drawing()

    return rectange_discard, rectange_accept