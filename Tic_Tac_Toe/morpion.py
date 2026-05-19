import tkinter
import math



def set_tile(row, column):
    global curr_player, game_over

    if game_over or board[row][column]["text"] != "":
        return
    
    
    board[row][column]["text"] = curr_player
    check_winner()

    
    if not game_over and mode_ia:
        curr_player = playerO
        label["text"] = " Au tour de " + curr_player
        label.update()
        window_game.after(400, ai_make_move) 
    
    
    elif not game_over:
        curr_player = playerO if curr_player == playerX else playerX
        label["text"] = " Au tour de " + curr_player

def ai_make_move():
    global curr_player
    if game_over:
        return

    
    move = best_move()
    if move:
        row, column = move
        board[row][column]["text"] = playerO
        check_winner()
        
        if not game_over:
            curr_player = playerX
            label["text"] = " Au tour de " + curr_player



def check_winner_sim(b):
    """ Évalue le plateau virtuel pour l'IA (sans toucher à l'interface graphique) """
    for i in range(3):
        if b[i][0] == b[i][1] == b[i][2] and b[i][0] != "":
            return b[i][0]
        if b[0][i] == b[1][i] == b[2][i] and b[0][i] != "":
            return b[0][i]
            
    if b[0][0] == b[1][1] == b[2][2] and b[0][0] != "":
        return b[0][0]
    if b[0][2] == b[1][1] == b[2][0] and b[0][2] != "":
        return b[0][2]
        
    for r in range(3):
        for c in range(3):
            if b[r][c] == "":
                return None
    return "Tie"

def best_move():
    best_score = -math.inf
    move = None
    
    
    sim_board = [[board[r][c]["text"] for c in range(3)] for r in range(3)]
    
    for r in range(3):
        for c in range(3):
            if sim_board[r][c] == "":
                sim_board[r][c] = playerO
                score = minimax(sim_board, 0, False)
                sim_board[r][c] = ""
                if score > best_score:
                    best_score = score
                    move = (r, c)
    return move

def minimax(sim_board, depth, is_maximizing):
    result = check_winner_sim(sim_board)
    if result is not None:
        if result == playerO: return 1
        if result == playerX: return -1
        return 0

    if is_maximizing:
        best_score = -math.inf
        for r in range(3):
            for c in range(3):
                if sim_board[r][c] == "":
                    sim_board[r][c] = playerO
                    score = minimax(sim_board, depth + 1, False)
                    sim_board[r][c] = ""
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = math.inf
        for r in range(3):
            for c in range(3):
                if sim_board[r][c] == "":
                    sim_board[r][c] = playerX
                    score = minimax(sim_board, depth + 1, True)
                    sim_board[r][c] = ""
                    best_score = min(score, best_score)
        return best_score


def check_winner():
    global turns, game_over
    turns += 1

   
    for row in range(3):
        if board[row][0]["text"] == board[row][1]["text"] == board[row][2]["text"] and board[row][0]["text"] != "":
            label.config(text=board[row][0]["text"]+" a gagné!", foreground=color_yellow)
            for column in range(3):
                board[row][column].config(foreground=color_yellow, background=color_light_gray)
            game_over = True
            return
    
 
    for column in range(3):
        if board[0][column]["text"] == board[1][column]["text"] == board[2][column]["text"] and board[0][column]["text"] != "":
            label.config(text=board[0][column]["text"]+" a gagné!", foreground=color_yellow)
            for row in range(3):
                board[row][column].config(foreground=color_yellow, background=color_light_gray)
            game_over = True
            return


    if board[0][0]["text"] == board[1][1]["text"] == board[2][2]["text"] and board[0][0]["text"] != "":
        label.config(text=board[0][0]["text"]+" a gagné!", foreground=color_yellow)
        for i in range(3):
            board[i][i].config(foreground=color_yellow, background=color_light_gray)
        game_over = True
        return

    if board[0][2]["text"] == board[1][1]["text"] == board[2][0]["text"] and board[0][2]["text"] != "":
        label.config(text=board[0][2]["text"]+" a gagné!", foreground=color_yellow)
        board[0][2].config(foreground=color_yellow, background=color_light_gray)
        board[1][1].config(foreground=color_yellow, background=color_light_gray)
        board[2][0].config(foreground=color_yellow, background=color_light_gray)
        game_over = True
        return
    
    if turns == 9:
        game_over = True
        label.config(text="Égalité !", foreground=color_red)

def new_game():
    global turns, game_over, curr_player
    turns = 0
    game_over = False
    curr_player = playerX
    label.config(text=" Au tour de " + curr_player, foreground="white")
    for row in range(3):
        for column in range(3):
            board[row][column].config(text="", foreground=color_blue, background=color_gray)

def retour_menu():
    window_game.withdraw()
    window_main.deiconify()

def lancer_partie(ia_mode):
    global mode_ia
    mode_ia = ia_mode
    window_main.withdraw()
    new_game()
    window_game.deiconify()



playerX = "X"
playerO = "O"
curr_player = playerX
mode_ia = False

color_blue = "#4584b6"
color_red = "#d81832"
color_yellow = "#ffde57"
color_gray = "#343434"
color_light_gray = "#646464"

turns = 0
game_over = False


window_main = tkinter.Tk()
window_main.title("Menu Tic Tac Toe")
window_main.config(background=color_gray)

frame_main = tkinter.Frame(window_main, background=color_gray)
frame_main.pack(padx=20, pady=20)

label_main = tkinter.Label(frame_main, text="Choisissez votre mode de jeu :", font=("Consolas", 18), background=color_gray, foreground="white")
label_main.pack(pady=10)

btn_j1_v_j2 = tkinter.Button(frame_main, text="Joueur 1 vs Joueur 2", font=("Consolas", 16), background=color_gray, foreground="white", command=lambda: lancer_partie(False))
btn_j1_v_j2.pack(fill="x", pady=5)

btn_j1_v_ia = tkinter.Button(frame_main, text="Joueur 1 vs IA (Minimax)", font=("Consolas", 16), background=color_gray, foreground="white", command=lambda: lancer_partie(True))
btn_j1_v_ia.pack(fill="x", pady=5)

btn_quit = tkinter.Button(frame_main, text="Quitter le jeu", font=("Consolas", 16), background=color_gray, foreground="white", command=quit)
btn_quit.pack(fill="x", pady=5)


window_game = tkinter.Toplevel()
window_game.title("Tic Tac Toe - Partie")
window_game.resizable(False, False)
window_game.withdraw()

frame = tkinter.Frame(window_game, background=color_gray)
frame.pack()

label = tkinter.Label(frame, text=" Au tour de " + curr_player, font=("Consolas", 20), background=color_gray, foreground="white")
label.grid(row=0, column=0, columnspan=3, sticky="we")


board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

for row in range(3):
    for column in range(3):
        board[row][column] = tkinter.Button(frame, text="", font=("Consolas", 50, "bold"),
                                            background=color_gray, foreground=color_blue, width=4, height=1,
                                            command=lambda r=row, c=column: set_tile(r, c))
        board[row][column].grid(row=row+1, column=column)


button_replay = tkinter.Button(frame, text="Rejouer", font=("Consolas", 18), background=color_gray, foreground="white", command=new_game)
button_replay.grid(row=4, column=0, columnspan=3, sticky="we")

button_menu = tkinter.Button(frame, text="Retourner au menu", font=("Consolas", 18), background=color_gray, foreground="white", command=retour_menu)
button_menu.grid(row=5, column=0, columnspan=3, sticky="we")

button_exit = tkinter.Button(frame, text="Quitter le jeu", font=("Consolas", 18), background=color_gray, foreground="white", command=quit)
button_exit.grid(row=6, column=0, columnspan=3, sticky="we")


window_game.update()
window_x = int((window_game.winfo_screenwidth()/2) - (window_game.winfo_width()/2))
window_y = int((window_game.winfo_screenheight()/2) - (window_game.winfo_height()/2))
window_game.geometry(f"+{window_x}+{window_y}")

window_main.mainloop()