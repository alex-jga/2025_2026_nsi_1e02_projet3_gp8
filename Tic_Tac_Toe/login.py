import os
import tkinter
from tkinter import messagebox
import math
import json
import random

DATA_FILE = "players.json"

playerX = "X"
playerO = "O"

curr_player = playerX
mode_ia = False

turns = 0
game_over = False

current_username = None

color_blue = "#4584b6"
color_red = "#d81832"
color_yellow = "#ffde57"
color_gray = "#343434"
color_light_gray = "#646464"

def load_data():

    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        for user in data:

            if "played" not in data[user]:
                data[user]["played"] = 0

            if "wins" not in data[user]:
                data[user]["wins"] = 0

            if "loses" not in data[user]:
                data[user]["loses"] = 0

            if "ties" not in data[user]:
                data[user]["ties"] = 0

        return data

    except:
        return {}

def save_data(data):

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def auth(mode):

    global current_username

    username = entry_username.get().strip()
    password = entry_password.get().strip()

    if not username or not password:
        messagebox.showerror("Erreur", "Remplissez tous les champs.")
        return

    data = load_data()

    if mode == "login":

        if username not in data:
            messagebox.showerror("Erreur", "Utilisateur inexistant.")
            return

        if data[username]["password"] != password:
            messagebox.showerror("Erreur", "Mot de passe incorrect.")
            return

        current_username = username

        update_stats_label()

        window_login.withdraw()
        window_main.deiconify()

        messagebox.showinfo("Succès", f"Bienvenue {username}")

    else:

        if username in data:
            messagebox.showerror("Erreur", "Utilisateur déjà existant.")
            return

        data[username] = {
            "password": password,
            "played": 0,
            "wins": 0,
            "loses": 0,
            "ties": 0
        }

        save_data(data)

        messagebox.showinfo("Succès", "Compte créé avec succès !")

def logout():

    global current_username

    current_username = None

    window_game.withdraw()
    window_main.withdraw()

    entry_username.delete(0, tkinter.END)
    entry_password.delete(0, tkinter.END)

    window_login.deiconify()

def update_stats(status):

    if not current_username or not mode_ia:
        return

    data = load_data()

    if current_username in data:

        stats = data[current_username]

        stats["played"] += 1

        if status == "win":
            stats["wins"] += 1

        elif status == "lose":
            stats["loses"] += 1

        elif status == "tie":
            stats["ties"] += 1

        save_data(data)

        update_stats_label()

def update_stats_label():

    if not current_username:
        return

    data = load_data()

    stats = data[current_username]

    label_stats.config(
        text=
        f"Joueur : {current_username}\n"
        f"Parties : {stats['played']} | "
        f"Victoires : {stats['wins']} | "
        f"Défaites : {stats['loses']} | "
        f"Nuls : {stats['ties']}"
    )

def set_tile(row, column):

    global curr_player
    global game_over

    if game_over:
        return

    if board[row][column]["text"] != "":
        return

    board[row][column]["text"] = curr_player

    check_winner()

    if game_over:
        return
    
    if mode_ia:

        curr_player = playerO

        label.config(text="Au tour de " + curr_player)

        window_game.after(200, ai_make_move)

    else:

        if curr_player == playerX:
            curr_player = playerO
        else:
            curr_player = playerX

        label.config(text="Au tour de " + curr_player)

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

            label.config(text="Au tour de " + curr_player)


def best_move():

    best_score = -math.inf
    move = None

    sim_board = [
        [board[r][c]["text"] for c in range(3)]
        for r in range(3)
    ]

    for r in range(3):
        for c in range(3):

            if sim_board[r][c] == "":

                sim_board[r][c] = playerO

                score = minimax(sim_board, False)

                sim_board[r][c] = ""

                if score > best_score:

                    best_score = score
                    move = (r, c)

    return move


def minimax(sim_board, is_maximizing):

    result = check_winner_sim(sim_board)

    if result is not None:

        if result == playerO:
            return 1

        if result == playerX:
            return -1

        return 0

    if is_maximizing:

        best_score = -math.inf

        for r in range(3):
            for c in range(3):

                if sim_board[r][c] == "":

                    sim_board[r][c] = playerO

                    score = minimax(sim_board, False)

                    sim_board[r][c] = ""

                    best_score = max(score, best_score)

        return best_score

    else:

        best_score = math.inf

        for r in range(3):
            for c in range(3):

                if sim_board[r][c] == "":

                    sim_board[r][c] = playerX

                    score = minimax(sim_board, True)

                    sim_board[r][c] = ""

                    best_score = min(score, best_score)

        return best_score


def check_winner_sim(b):

    for i in range(3):

        if b[i][0] == b[i][1] == b[i][2] != "":
            return b[i][0]

        if b[0][i] == b[1][i] == b[2][i] != "":
            return b[0][i]

    if b[0][0] == b[1][1] == b[2][2] != "":
        return b[0][0]

    if b[0][2] == b[1][1] == b[2][0] != "":
        return b[0][2]

    for r in range(3):
        for c in range(3):

            if b[r][c] == "":
                return None

    return "Tie"

def check_winner():

    global turns
    global game_over

    turns += 1

    for row in range(3):

        if board[row][0]["text"] == board[row][1]["text"] == board[row][2]["text"] != "":

            winner(board[row][0]["text"])

            for column in range(3):
                board[row][column].config(
                    foreground=color_yellow,
                    background=color_light_gray
                )

            return

    for column in range(3):

        if board[0][column]["text"] == board[1][column]["text"] == board[2][column]["text"] != "":

            winner(board[0][column]["text"])

            for row in range(3):
                board[row][column].config(
                    foreground=color_yellow,
                    background=color_light_gray
                )

            return

    if board[0][0]["text"] == board[1][1]["text"] == board[2][2]["text"] != "":

        winner(board[0][0]["text"])

        for i in range(3):
            board[i][i].config(
                foreground=color_yellow,
                background=color_light_gray
            )

        return

    if board[0][2]["text"] == board[1][1]["text"] == board[2][0]["text"] != "":

        winner(board[0][2]["text"])

        board[0][2].config(foreground=color_yellow, background=color_light_gray)
        board[1][1].config(foreground=color_yellow, background=color_light_gray)
        board[2][0].config(foreground=color_yellow, background=color_light_gray)

        return

    if turns == 9:

        game_over = True

        label.config(
            text="Égalité !",
            foreground=color_red
        )

        update_stats("tie")

def winner(player):

    global game_over

    game_over = True

    label.config(
        text=player + " a gagné !",
        foreground=color_yellow
    )

    if player == playerX:
        update_stats("win")
    else:
        update_stats("lose")

def new_game():

    global turns
    global game_over
    global curr_player

    turns = 0
    game_over = False

    for row in range(3):
        for column in range(3):

            board[row][column].config(
                text="",
                foreground=color_blue,
                background=color_gray
            )

    if mode_ia:

        curr_player = random.choice([playerX, playerO])

    else:

        curr_player = playerX

    label.config(
        text="Au tour de " + curr_player,
        foreground="white"
    )

    if mode_ia and curr_player == playerO:

        window_game.after(200, ai_make_move)

def retour_menu():

    window_game.withdraw()

    window_main.deiconify()

def lancer_partie(ia_mode):

    global mode_ia

    mode_ia = ia_mode

    new_game()

    window_main.withdraw()

    window_game.deiconify()

window_login = tkinter.Tk()

window_login.title("Connexion Tic Tac Toe")

window_login.config(background=color_gray)

frame_login = tkinter.Frame(
    window_login,
    background=color_gray
)

frame_login.pack(
    padx=30,
    pady=30
)

label_title = tkinter.Label(
    frame_login,
    text="Connexion / Inscription",
    font=("Consolas", 18, "bold"),
    background=color_gray,
    foreground="white"
)

label_title.pack(pady=10)

label_user = tkinter.Label(
    frame_login,
    text="Nom d'utilisateur",
    font=("Consolas", 12),
    background=color_gray,
    foreground="white"
)

label_user.pack(anchor="w")

entry_username = tkinter.Entry(
    frame_login,
    font=("Consolas", 12)
)

entry_username.pack(fill="x", pady=5)

label_pass = tkinter.Label(
    frame_login,
    text="Mot de passe",
    font=("Consolas", 12),
    background=color_gray,
    foreground="white"
)

label_pass.pack(anchor="w")

entry_password = tkinter.Entry(
    frame_login,
    font=("Consolas", 12),
    show="*"
)

entry_password.pack(fill="x", pady=5)

btn_login = tkinter.Button(
    frame_login,
    text="Se connecter",
    font=("Consolas", 14),
    background=color_blue,
    foreground="white",
    command=lambda: auth("login")
)

btn_login.pack(fill="x", pady=10)

btn_register = tkinter.Button(
    frame_login,
    text="Créer un compte",
    font=("Consolas", 12),
    background=color_light_gray,
    foreground="white",
    command=lambda: auth("register")
)

btn_register.pack(fill="x")

window_main = tkinter.Toplevel()

window_main.title("Menu")

window_main.config(background=color_gray)

window_main.withdraw()

window_main.protocol("WM_DELETE_WINDOW", quit)

frame_main = tkinter.Frame(
    window_main,
    background=color_gray
)

frame_main.pack(
    padx=20,
    pady=20
)

label_main = tkinter.Label(
    frame_main,
    text="Choisissez votre mode",
    font=("Consolas", 18),
    background=color_gray,
    foreground="white"
)

label_main.pack(pady=10)

label_stats = tkinter.Label(
    frame_main,
    text="",
    font=("Consolas", 12, "italic"),
    background=color_gray,
    foreground=color_yellow
)

label_stats.pack(pady=10)

btn_j1_v_j2 = tkinter.Button(
    frame_main,
    text="Joueur vs Joueur",
    font=("Consolas", 16),
    background=color_gray,
    foreground="white",
    command=lambda: lancer_partie(False)
)

btn_j1_v_j2.pack(fill="x", pady=5)

btn_j1_v_ia = tkinter.Button(
    frame_main,
    text="Joueur vs IA",
    font=("Consolas", 16),
    background=color_gray,
    foreground="white",
    command=lambda: lancer_partie(True)
)

btn_j1_v_ia.pack(fill="x", pady=5)

btn_logout = tkinter.Button(
    frame_main,
    text="Déconnexion",
    font=("Consolas", 16),
    background=color_red,
    foreground="white",
    command=logout
)

btn_logout.pack(fill="x", pady=5)

btn_quit = tkinter.Button(
    frame_main,
    text="Quitter",
    font=("Consolas", 16),
    background=color_gray,
    foreground="white",
    command=quit
)

btn_quit.pack(fill="x", pady=5)

window_game = tkinter.Toplevel()

window_game.title("Tic Tac Toe")

window_game.resizable(False, False)

window_game.withdraw()

window_game.protocol("WM_DELETE_WINDOW", quit)

frame = tkinter.Frame(
    window_game,
    background=color_gray
)

frame.pack()

label = tkinter.Label(
    frame,
    text="Au tour de " + curr_player,
    font=("Consolas", 20),
    background=color_gray,
    foreground="white"
)

label.grid(
    row=0,
    column=0,
    columnspan=3,
    sticky="we"
)

board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

for row in range(3):
    for column in range(3):

        board[row][column] = tkinter.Button(
            frame,
            text="",
            font=("Consolas", 50, "bold"),
            background=color_gray,
            foreground=color_blue,
            width=4,
            height=1,
            command=lambda r=row, c=column: set_tile(r, c)
        )

        board[row][column].grid(
            row=row + 1,
            column=column
        )

button_replay = tkinter.Button(
    frame,
    text="Rejouer",
    font=("Consolas", 18),
    background=color_gray,
    foreground="white",
    command=new_game
)

button_replay.grid(
    row=4,
    column=0,
    columnspan=3,
    sticky="we"
)

button_menu = tkinter.Button(
    frame,
    text="Retour menu",
    font=("Consolas", 18),
    background=color_gray,
    foreground="white",
    command=retour_menu
)

button_menu.grid(
    row=5,
    column=0,
    columnspan=3,
    sticky="we"
)

button_exit = tkinter.Button(
    frame,
    text="Quitter",
    font=("Consolas", 18),
    background=color_gray,
    foreground="white",
    command=quit
)

button_exit.grid(
    row=6,
    column=0,
    columnspan=3,
    sticky="we"
)

window_login.mainloop()
