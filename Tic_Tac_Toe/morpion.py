import os
import tkinter
from tkinter import messagebox
import math
import json
import random
from tkinter import font as tkfont

DATA_FILE = "players.json"

playerX = "X"
playerO = "O"

curr_player = playerX
mode_ia = False

turns = 0
game_over = False

current_username = None

# --- PALETTE CYBERPUNK INTIMIDANTE & ULTRA-HD ---
COLOR_DEEP_BLACK = "#050508"     # Fond ultra-sombre (OLED Black)
COLOR_GRID_LINE = "#3A0011"      # Lignes de grille - Rouge sang sombre
COLOR_TILE_BG = "#0D0E12"        # Fond des cases fermées
COLOR_TILE_HOVER = "#1A0008"     # Halo de survol agressif
COLOR_RED_NEON = "#FF003C"       # Rouge Néon Électrique (Joueur X)
COLOR_GREEN_NEON = "#00FF66"     # Vert Matrice / IA Cyber (Joueur O)
COLOR_GOLD_VICTORY = "#FFCC00"   # Or Brillant pour le vainqueur
COLOR_TEXT_MUTED = "#555A64"     # Gris technique pour les infos secondaires
COLOR_INTERFACE_BORDER = "#22252C" # Bordures de l'interface

def get_custom_fonts():
    # Utilisation de polices d'impact pour un effet lourd et pro
    font_title = ("Impact", 28)
    font_stats = ("Arial", 10, "bold")
    font_btn = ("Impact", 14)
    font_grid = ("Impact", 55)
    return font_title, font_stats, font_btn, font_grid

# --- REPRISE DE LA LOGIQUE ET DE L'AUTHENTIFICATION ---
def load_data():
    if not os.path.exists(DATA_FILE): return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f: data = json.load(f)
        for user in data:
            if "played" not in data[user]: data[user]["played"] = 0
            if "wins" not in data[user]: data[user]["wins"] = 0
            if "loses" not in data[user]: data[user]["loses"] = 0
            if "ties" not in data[user]: data[user]["ties"] = 0
        return data
    except: return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(data, f, indent=4, ensure_ascii=False)

def auth(mode):
    global current_username
    username = entry_username.get().strip()
    password = entry_password.get().strip()
    if not username or not password:
        messagebox.showerror("ERREUR SYSTEME", "Réessayez")
        return
    data = load_data()
    if mode == "login":
        if username not in data or data[username]["password"] != password:
            messagebox.showerror("ACCÈS REFUSÉ", "Identifiants invalides ou inconnus.")
            return
        current_username = username
        update_stats_label()
        window_login.withdraw()
        window_main.deiconify()
    else:
        if username in data:
            messagebox.showerror("ERREUR ENREGISTREMENT", "Ce profil existe déjà.")
            return
        data[username] = {"password": password, "played": 0, "wins": 0, "loses": 0, "ties": 0}
        save_data(data)
        messagebox.showinfo("SYSTÈME", "Profil enregistré. Prêt pour l'initialisation.")

def logout():
    global current_username
    current_username = None
    window_game.withdraw()
    window_main.withdraw()
    entry_username.delete(0, tkinter.END)
    entry_password.delete(0, tkinter.END)
    window_login.deiconify()

def update_stats(status):
    if not current_username or not mode_ia: return
    data = load_data()
    if current_username in data:
        stats = data[current_username]
        stats["played"] += 1
        if status == "win": stats["wins"] += 1
        elif status == "lose": stats["loses"] += 1
        elif status == "tie": stats["ties"] += 1
        save_data(data)
        update_stats_label()

def update_stats_label():
    if not current_username: return
    data = load_data()
    stats = data[current_username]
    label_stats.config(
        text=f"COMBATTANT : {current_username.upper()}\n[ MATCHS : {stats['played']}  |  VICTOIRES : {stats['wins']}  |  DÉFAITES : {stats['loses']} ]"
    )

# --- ENROULEMENT DE LA LOGIQUE DE JEU AGRESSIVE ---
def set_tile(row, column):
    global curr_player, game_over
    if game_over or board[row][column]["text"] != "": return

    if curr_player == playerX:
        board[row][column].config(text=playerX, foreground=COLOR_RED_NEON, activeforeground=COLOR_RED_NEON)
    else:
        board[row][column].config(text=playerO, foreground=COLOR_GREEN_NEON, activeforeground=COLOR_GREEN_NEON)

    check_winner()
    if game_over: return
    
    if mode_ia:
        curr_player = playerO
        label.config(text="IA", foreground=COLOR_GREEN_NEON)
        window_game.after(100, ai_make_move)
    else:
        curr_player = playerO if curr_player == playerX else playerX
        color_info = COLOR_RED_NEON if curr_player == playerX else COLOR_GREEN_NEON
        label.config(text=f"JOUEUR {curr_player}", foreground=color_info)

def ai_make_move():
    global curr_player
    if game_over: return
    move = best_move()
    if move:
        row, column = move
        board[row][column].config(text=playerO, foreground=COLOR_GREEN_NEON, activeforeground=COLOR_GREEN_NEON)
        check_winner()
        if not game_over:
            curr_player = playerX
            label.config(text=f"JOUEUR {curr_player}", foreground=COLOR_RED_NEON)

# --- ALGORITHME DE PREDATION (MINIMAX) ---
def best_move():
    best_score = -math.inf
    move = None
    sim_board = [[board[r][c]["text"] for c in range(3)] for r in range(3)]
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
        if result == playerO: return 1
        if result == playerX: return -1
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
        if b[i][0] == b[i][1] == b[i][2] != "": return b[i][0]
        if b[0][i] == b[1][i] == b[2][i] != "": return b[0][i]
    if b[0][0] == b[1][1] == b[2][2] != "": return b[0][0]
    if b[0][2] == b[1][1] == b[2][0] != "": return b[0][2]
    for r in range(3):
        for c in range(3):
            if b[r][c] == "": return None
    return "Tie"

# --- CALCULE DE DESTRUCTION ET VERDICT ---
def check_winner():
    global turns, game_over
    turns += 1
    for row in range(3):
        if board[row][0]["text"] == board[row][1]["text"] == board[row][2]["text"] != "":
            highlight_winner(board[row][0]["text"], [(row, 0), (row, 1), (row, 2)])
            return
    for column in range(3):
        if board[0][column]["text"] == board[1][column]["text"] == board[2][column]["text"] != "":
            highlight_winner(board[0][column]["text"], [(0, column), (1, column), (2, column)])
            return
    if board[0][0]["text"] == board[1][1]["text"] == board[2][2]["text"] != "":
        highlight_winner(board[0][0]["text"], [(0, 0), (1, 1), (2, 2)])
        return
    if board[0][2]["text"] == board[1][1]["text"] == board[2][0]["text"] != "":
        highlight_winner(board[0][2]["text"], [(0, 2), (1, 1), (2, 0)])
        return
    if turns == 9:
        game_over = True
        label.config(text="ÉGALITÉ COLD... IMPASSE RECONNU.", foreground=COLOR_TEXT_MUTED)
        update_stats("tie")

def highlight_winner(player, tiles):
    global game_over
    game_over = True
    if player == playerX:
        label.config(text=f"DOMINATION : JOUEUR {player} ÉCRASE LA PARTIE !", foreground=COLOR_RED_NEON)
        update_stats("win")
    else:
        label.config(text=f"ANNIHILATION", foreground=COLOR_GREEN_NEON)
        update_stats("lose")
        
    for row, col in tiles:
        board[row][col].config(background="#150005", foreground=COLOR_GOLD_VICTORY, activebackground="#150005")

def new_game():
    global turns, game_over, curr_player
    turns = 0
    game_over = False
    
    for row in range(3):
        for column in range(3):
            board[row][column].config(text="", background=COLOR_TILE_BG, foreground=COLOR_RED_NEON)

    if mode_ia:
        curr_player = random.choice([playerX, playerO])
    else:
        curr_player = playerX

    color_info = COLOR_RED_NEON if curr_player == playerX else COLOR_GREEN_NEON
    text_info = f"SÉQUENCE : JOUEUR {curr_player}" if not mode_ia else (f"ENGAGEMENT REQUIS ({curr_player})" if curr_player == playerX else "L'IA ENGAGE L'ASSAUT (O)")
    label.config(text=text_info, foreground=color_info)

    if mode_ia and curr_player == playerO:
        label.config(text="L'IA PREND LE CONTRÔLE...", foreground=COLOR_GREEN_NEON)
        window_game.after(100, ai_make_move)

def retour_menu():
    window_game.withdraw()
    window_main.deiconify()

def lancer_partie(ia_mode):
    global mode_ia
    mode_ia = ia_mode
    new_game()
    window_main.withdraw()
    window_game.deiconify()


# --- CONSTRUCTEUR DE L'INTERFACE CADRÉE ET SOMBRE ---
window_login = tkinter.Tk()
window_login.title("CONNEXION")
window_login.config(background=COLOR_DEEP_BLACK)
window_login.geometry("400x520")

f_title, f_stats, f_btn, f_grid = get_custom_fonts()

# Bouton de Commande Style Terminal
def create_gaming_button(parent, text, command, bg_color, hover_color, font, fg_color="white", border_c=COLOR_INTERFACE_BORDER, pady=6):
    btn = tkinter.Button(
        parent, text=text, font=font, background=bg_color, foreground=fg_color,
        relief="flat", activebackground=hover_color, activeforeground=fg_color, 
        highlightthickness=2, highlightbackground=border_c, cursor="hand2", command=command
    )
    btn.pack(fill="x", pady=pady, ipady=8)
    btn.bind("<Enter>", lambda e: btn.config(background=hover_color))
    btn.bind("<Leave>", lambda e: btn.config(background=bg_color))
    return btn

# LOGIN FRAME
frame_login = tkinter.Frame(window_login, background=COLOR_DEEP_BLACK)
frame_login.pack(expand=True, padx=40, fill="x")

tkinter.Label(frame_login, text="OXO", font=f_title, background=COLOR_DEEP_BLACK, foreground=COLOR_RED_NEON).pack(pady=5)
tkinter.Label(frame_login, text="ENTREZ VOS COORDONNÉES", font=("Arial", 9, "bold"), background=COLOR_DEEP_BLACK, foreground=COLOR_TEXT_MUTED).pack(pady=(0, 25))

tkinter.Label(frame_login, text="// NOM D'UTILISATEUR", font=("Arial", 9, "bold"), background=COLOR_DEEP_BLACK, foreground="white").pack(anchor="w")
entry_username = tkinter.Entry(frame_login, font=("Arial", 12), bg=COLOR_TILE_BG, fg="white", insertbackground=COLOR_RED_NEON, relief="flat", highlightthickness=1, highlightbackground=COLOR_INTERFACE_BORDER)
entry_username.pack(fill="x", pady=(5, 15), ipady=8)

tkinter.Label(frame_login, text="// CLÉ DE SÉCURITÉ (PASSWORD)", font=("Arial", 9, "bold"), background=COLOR_DEEP_BLACK, foreground="white").pack(anchor="w")
entry_password = tkinter.Entry(frame_login, font=("Arial", 12), bg=COLOR_TILE_BG, fg="white", insertbackground=COLOR_RED_NEON, relief="flat", highlightthickness=1, highlightbackground=COLOR_INTERFACE_BORDER, show="*")
entry_password.pack(fill="x", pady=5, ipady=8)

create_gaming_button(frame_login, "CONNEXION", lambda: auth("login"), COLOR_RED_NEON, "#C4002E", f_btn, fg_color="white", border_c="#C4002E", pady=(25, 8))
create_gaming_button(frame_login, "NOUVEAU PROFIL", lambda: auth("register"), COLOR_TILE_BG, "#171A21", f_btn, fg_color=COLOR_TEXT_MUTED, pady=2)


# MENU FRAME
window_main = tkinter.Toplevel()
window_main.title("MENU")
window_main.config(background=COLOR_DEEP_BLACK)
window_main.withdraw()
window_main.protocol("WM_DELETE_WINDOW", quit)
window_main.geometry("420x540")

frame_main = tkinter.Frame(window_main, background=COLOR_DEEP_BLACK)
frame_main.pack(expand=True, padx=40, fill="x")

tkinter.Label(frame_main, text="MENU", font=f_title, background=COLOR_DEEP_BLACK, foreground=COLOR_GREEN_NEON).pack(pady=10)
label_stats = tkinter.Label(frame_main, text="", font=f_stats, background=COLOR_DEEP_BLACK, foreground=COLOR_GOLD_VICTORY)
label_stats.pack(pady=(0, 30))

create_gaming_button(frame_main, "[ P2P ]  DUEL LOCAL", lambda: lancer_partie(False), COLOR_TILE_BG, "#171A21", f_btn, pady=8)
create_gaming_button(frame_main, "[ P2IA ]  AFFRONTER L'IA", lambda: lancer_partie(True), COLOR_TILE_BG, COLOR_TILE_HOVER, f_btn, fg_color=COLOR_GREEN_NEON, border_c=COLOR_GREEN_NEON, pady=8)

tkinter.Frame(frame_main, height=2, bg=COLOR_INTERFACE_BORDER).pack(fill="x", pady=25)
create_gaming_button(frame_main, "DECONNEXION", logout, COLOR_DEEP_BLACK, COLOR_TILE_BG, ("Arial", 10, "bold"), fg_color=COLOR_TEXT_MUTED, pady=2)
create_gaming_button(frame_main, "ÉTEINDRE LE SYSTÈME", quit, "#73001C", "#4A0012", f_btn, pady=10)


# GAME WINDOW (GRILLE HAUTE DÉFINITION INTIMIDANTE)
window_game = tkinter.Toplevel()
window_game.title("JEU")
window_game.resizable(False, False)
window_game.withdraw()
window_game.config(background=COLOR_DEEP_BLACK)
window_game.protocol("WM_DELETE_WINDOW", quit)

# Indicateur de menace
label = tkinter.Label(window_game, text=f"TOUR : JOUEUR {curr_player}", font=("Impact", 18), background=COLOR_DEEP_BLACK, foreground=COLOR_RED_NEON)
label.pack(pady=20)

# Le conteneur génère des lignes 4K ultra-fines et agressives
grid_container = tkinter.Frame(window_game, background=COLOR_GRID_LINE, bd=0)
grid_container.pack(padx=30, pady=5)

board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

for row in range(3):
    for column in range(3):
        btn = tkinter.Button(
            grid_container,
            text="",
            font=f_grid,
            background=COLOR_TILE_BG,
            activebackground=COLOR_TILE_HOVER,
            relief="flat",
            width=3,
            height=1,
            cursor="hand2"
        )
        # Espacement de 4px pour un quadrillage ultra-net et contrasté
        btn.grid(row=row, column=column, padx=4, pady=4) 
        btn.config(command=lambda r=row, c=column: set_tile(r, c))
        
        # Gestion des effets visuels dynamiques
        def on_enter(e, b=btn): 
            if b["text"] == "": b.config(background=COLOR_TILE_HOVER)
        def on_leave(e, b=btn): 
            if b["text"] == "": b.config(background=COLOR_TILE_BG)
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        board[row][column] = btn


frame_controls = tkinter.Frame(window_game, background=COLOR_DEEP_BLACK)
frame_controls.pack(padx=30, pady=25, fill="x")

create_gaming_button(frame_controls, "REJOUER", new_game, COLOR_TILE_BG, "#171A21", f_btn, pady=4)
create_gaming_button(frame_controls, "ABANDONNER / MENU", retour_menu, COLOR_DEEP_BLACK, COLOR_TILE_BG, ("Arial", 10, "bold"), fg_color=COLOR_TEXT_MUTED, pady=2)

window_login.mainloop()