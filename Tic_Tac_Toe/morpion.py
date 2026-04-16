import tkinter 

def set_tile(row, column):
    global curr_player

    if (game_over):
        return

    if board[row][column]["text"] != "":
        return
    
    board[row][column]["text"] = curr_player

    if curr_player == playerO: 
        curr_player = playerX
    else:
        curr_player = playerO
    
    label["text"] = " Au tour de " + curr_player


    check_winner()

def check_winner():
    global turns, game_over
    turns += 1


    for row in range(3):
        if (board[row][0]["text"] == board[row][1]["text"] == board[row][2]["text"]
            and board[row][0]["text"] != ""):
            label.config(text=board[row][0]["text"]+" a gagné!", foreground=color_yellow)
            for column in range(3):
                board[row][column].config(foreground=color_yellow, background=color_light_gray)
            game_over = True
            return
    

    for column in range(3):
        if (board[0][column]["text"] == board[1][column]["text"] == board[2][column]["text"]
            and board[0][column]["text"] != ""):
            label.config(text=board[0][column]["text"]+" a gagné!", foreground=color_yellow)
            for row in range(3):
                board[row][column].config(foreground=color_yellow, background=color_light_gray)
            game_over = True
            return


    if (board[0][0]["text"] == board[1][1]["text"] == board[2][2]["text"]
        and board[0][0]["text"] != ""):
        label.config(text=board[0][0]["text"]+" a gagné!", foreground=color_yellow)
        for i in range(3):
            board[i][i].config(foreground=color_yellow, background=color_light_gray)
        game_over = True
        return


    if (board[0][2]["text"] == board[1][1]["text"] == board[2][0]["text"]
        and board[0][2]["text"] != ""):
        label.config(text=board[0][2]["text"]+"  a gagné!", foreground=color_yellow)
        board[0][2].config(foreground=color_yellow, background=color_light_gray)
        board[1][1].config(foreground=color_yellow, background=color_light_gray)
        board[2][0].config(foreground=color_yellow, background=color_light_gray)
        game_over = True
        return
    
 
    if (turns == 9):
        game_over = True
        label.config(text="Egalité !", foreground=color_red)

def new_game():
    global turns, game_over

    turns = 0
    game_over = False

    label.config(text=" Au tour de " + curr_player, foreground="white")

    for row in range(3):
        for column in range(3):
            board[row][column].config(text="", foreground=color_blue, background=color_gray)

def retour_menu():
    window_j1_vs_j2.withdraw()

def open_window_j1_vs_j2():
    window_j1_vs_j2.deiconify()

def open_window_j1_vs_ia():
    pass

playerX = "X"
playerO = "O"
curr_player = playerX
board = [[0, 0, 0], 
         [0, 0, 0], 
         [0, 0, 0]]

color_blue = "#4584b6"
color_red = "#d81832"
color_yellow = "#ffde57"
color_gray = "#343434"
color_light_gray = "#646464"

turns = 0
game_over = False

window_main = tkinter.Tk()

frame_main = tkinter.Frame(window_main, background=color_gray)

label_main = tkinter.Label(frame_main , text=" Voulez-vous jouer contre un ami, une ia ou vous-même ?", font=("Consolas", 20),
                            background=color_gray, foreground="white")
label_main.pack()

button_main_j1_vs_j2 = tkinter.Button(frame_main, text="J1 versus J2 (Contre un ami ou contre vous même)", font=("Consolas", 20), background=color_gray,
                        foreground="white", command=open_window_j1_vs_j2)

button_main_j1_vs_ia = tkinter.Button(frame_main, text="J1 versus IA (bientôt)", font=("Consolas", 20),
                        background=color_gray, foreground="white", command=open_window_j1_vs_ia)

button_main = tkinter.Button(frame_main, text="Quitter le jeu", font=("Consolas", 20), background=color_gray,
                        foreground="white", command=quit)


frame_main.pack()
button_main_j1_vs_j2.pack()
button_main_j1_vs_ia.pack()
button_main.pack()

window_j1_vs_j2 = tkinter.Tk()
window_j1_vs_j2.title("Tic Tac Toe")
window_j1_vs_j2.resizable(False, False)

window_j1_vs_j2.withdraw()

frame = tkinter.Frame(window_j1_vs_j2)
label = tkinter.Label(frame, text=" Au tour de " + curr_player, font=("Consolas", 20), background=color_gray,
                      foreground="white")
label.grid(row=0, column=0, columnspan=3, sticky="we")

for row in range(3):
    for column in range(3):
        board[row][column] = tkinter.Button(frame, text="", font=("Consolas", 50, "bold"),
                                            background=color_gray, foreground=color_blue, width=4, height=1,
                                            command=lambda row=row, column=column: set_tile(row, column))
        board[row][column].grid(row=row+1, column=column)

button = tkinter.Button(frame, text="Rejouer", font=("Consolas", 20), background=color_gray,
                        foreground="white", command=new_game)
button.grid(row=4, column=0, columnspan=3, sticky="we")

button = tkinter.Button(frame, text="Retourner au menu", font=("Consolas", 20), background=color_gray,
                        foreground="white", command=retour_menu)
button.grid(row=5, column=0, columnspan=3, sticky="we")

button = tkinter.Button(frame, text="Quitter le jeu", font=("Consolas", 20), background=color_gray,
                        foreground="white", command=quit)
button.grid(row=6, column=0, columnspan=3, sticky="we")


frame.pack()


window_j1_vs_j2.update()
window_width = window_j1_vs_j2.winfo_width()
window_height = window_j1_vs_j2.winfo_height()
screen_width = window_j1_vs_j2.winfo_screenwidth()
screen_height = window_j1_vs_j2.winfo_screenheight()

window_x = int((screen_width/2) - (window_width/2))
window_y = int((screen_height/2) - (window_height/2))


window_j1_vs_j2.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

window_main.mainloop()