import tkinter
def print_winner():
    global win

    if win is False:
        win = True

    window_win = tkinter.Tk()
    window_win.title("Victoire")

    texte = f"Le joueur {current_player} a gagné le jeu"

    label = tkinter.Label(window_win, text=texte)
    label.pack()

    window_win.mainloop()
       
       

def switch_player():
    global current_player
    if current_player == 'X':
        current_player = '0'
    else:
        current_player = 'X'

def check_win(clicked_row, clicked_col):

    # detecter victoire horizontale
    count = 0
    for i in range(3):
        current_button = buttons[i][clicked_row]
        if current_button['text'] == current_player:
            count += 1
    if count == 3:
        print_winner()

    # detecter victoire verticale
    count = 0
    for i in range(3):
        current_button = buttons[clicked_col][i]
        if current_button['text'] == current_player:
            count += 1
    if count == 3:
        print_winner()

    # detecter victoire diagonale
    count = 0
    for i in range(3):
        current_button = buttons[i][i]
        if current_button['text'] == current_player:
            count += 1
    if count == 3:
        print_winner()

    # detecter victoire diagonale inversee
    count = 0
    for i in range(3):
        current_button = buttons[2-i][i]
        if current_button['text'] == current_player:
            count += 1
    if count == 3:
        print_winner()

    if win is False:
        count = 0
        for col in range(3):
            for row in range(3):
                current_button = buttons[col][row]
                if current_button['text'] == 'X' or current_button['text'] == '0':
                    count += 1
        if count == 9:
            print("Match nul")


def place_symbol(row, column):

    clicked_button = buttons[column][row]
    if clicked_button['text'] == "":
        clicked_button.config(text=current_player)

        check_win(row, column)
        switch_player()

def draw_grid():
    for column in range(3):
        buttons_in_cols = []
        for row in range(3):
            button = tkinter.Button(
                root, font=("Arial", 50),
                width=5, height=2,
                command=lambda r=row, c=column: place_symbol(r, c)
            )
            button.grid(row=row, column=column)
            buttons_in_cols.append(button)
        buttons.append(buttons_in_cols)

# stockages
buttons = []
current_player = 'X'
win = False

# creer la fenetre du jeu
root = tkinter.Tk()

# creer la fenetre du gagnant


# personnalisation de la fenetre
root.title("TicTacToe")
root.minsize(500, 500)

draw_grid()
root.mainloop()