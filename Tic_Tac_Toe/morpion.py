import os
import sys
import threading
import tkinter
from tkinter import messagebox, filedialog, ttk
import math
import json
import random
from tkinter import font as tkfont

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from qlearning import (
    QLearningAgent,
    TicTacToeEnv,
    run_training_episode,
    q_move_for_player,
    board_to_key,
    check_winner_cells,
    QTABLE_DEFAULT,
)

DATA_FILE = "players.json"

playerX = "X"
playerO = "O"

curr_player = playerX
mode_ia = False

turns = 0
game_over = False

current_username = None

ql_agent = QLearningAgent()
ql_env = TicTacToeEnv()
ql_training_active = False
ql_demo_active = False
ql_demo_steps = [0]

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
    
    font_title = ("Impact", 28)
    font_stats = ("Arial", 10, "bold")
    font_btn = ("Impact", 14)
    font_grid = ("Impact", 55)
    return font_title, font_stats, font_btn, font_grid


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
    move = q_move_for_player(ql_agent, board, playerO)
    if move is None:
        move = best_move()
    if move:
        row, column = move
        board[row][column].config(text=playerO, foreground=COLOR_GREEN_NEON, activeforeground=COLOR_GREEN_NEON)
        check_winner()
        if not game_over:
            curr_player = playerX
            label.config(text=f"JOUEUR {curr_player}", foreground=COLOR_RED_NEON)


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
        label.config(text="ÉGALITE.", foreground=COLOR_TEXT_MUTED)
        update_stats("tie")

def highlight_winner(player, tiles):
    global game_over
    game_over = True
    if player == playerX:
        label.config(text=f"JOUEUR {player} A GAGNE ", foreground=COLOR_RED_NEON)
        update_stats("win")
    else:
        label.config(text=f"JOUEUR {player} A GAGNE", foreground=COLOR_GREEN_NEON)
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
    text_info = f"SÉQUENCE : JOUEUR {curr_player}" if not mode_ia else (f"TOUR : ({curr_player})" if curr_player == playerX else "L'IA ENGAGE L'ASSAUT (O)")
    label.config(text=text_info, foreground=color_info)

    if mode_ia and curr_player == playerO:
        label.config(text="TOUR : IA", foreground=COLOR_GREEN_NEON)
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


def ouvrir_entrainement_rl():
    """Ouvre la fenêtre d'entraînement IA vs IA (Q-learning)."""
    window_main.withdraw()
    window_rl.deiconify()
    _rl_refresh_stats()
    _rl_log("Prêt. Lancez l'apprentissage ou chargez une table Q.")


def retour_menu_depuis_rl():
    _rl_stop_training()
    _rl_stop_demo()
    window_rl.withdraw()
    window_main.deiconify()


def _rl_log(msg):
    rl_log.insert(tkinter.END, msg + "\n")
    rl_log.see(tkinter.END)


def _rl_refresh_stats():
    total = max(1, ql_agent.episode_count)
    rl_lbl_episode.config(text=str(ql_agent.episode_count))
    rl_lbl_epsilon.config(text=f"{ql_agent.epsilon:.3f}")
    rl_lbl_wins.config(
        text=f"X:{ql_agent.win_x}  O:{ql_agent.win_o}  Nuls:{ql_agent.ties}"
    )
    if ql_agent.episode_count:
        pct = (ql_agent.win_x + ql_agent.win_o + ql_agent.ties) / total * 100
        rl_lbl_rate.config(text=f"{pct:.0f}% parties terminées")
    else:
        rl_lbl_rate.config(text="—")


def _rl_update_grid_from_cells(cells):
    for r in range(3):
        for c in range(3):
            v = cells[r * 3 + c]
            btn = rl_board[r][c]
            if v == playerX:
                btn.config(text=playerX, foreground=COLOR_RED_NEON)
            elif v == playerO:
                btn.config(text=playerO, foreground=COLOR_GREEN_NEON)
            else:
                btn.config(text="", foreground=COLOR_TEXT_MUTED)


def _rl_training_loop(n_episodes):
    global ql_training_active
    ql_agent.alpha = float(rl_spin_alpha.get())
    ql_agent.gamma = float(rl_spin_gamma.get())

    for ep in range(n_episodes):
        if not ql_training_active:
            break
        run_training_episode(ql_agent, ql_env)
        ql_agent.decay_epsilon()
        ql_agent.episode_count += 1

        if ep % 10 == 0:
            last_cells = list(ql_env.cells)
            ep_num = ql_agent.episode_count
            eps = ql_agent.epsilon
            wx, wo, ties = ql_agent.win_x, ql_agent.win_o, ql_agent.ties
            window_rl.after(
                0,
                lambda c=last_cells, n=ep_num, e=eps, x=wx, o=wo, t=ties: (
                    _rl_update_grid_from_cells(c),
                    rl_progress.config(value=n),
                    rl_lbl_episode.config(text=str(n)),
                    rl_lbl_epsilon.config(text=f"{e:.3f}"),
                    rl_lbl_wins.config(text=f"X:{x}  O:{o}  Nuls:{t}"),
                ),
            )

    window_rl.after(0, _rl_on_training_finished)


def _rl_on_training_finished():
    global ql_training_active
    ql_training_active = False
    ql_btn_train.config(text="▶  APPRENTISSAGE (Q-learning)")
    rl_progress.pack_forget()
    _rl_refresh_stats()
    _rl_log(
        f"Entraînement terminé — {ql_agent.episode_count} épisodes | "
        f"états appris : {len(ql_agent.q_table)}"
    )


def _rl_start_training():
    global ql_training_active
    if ql_training_active:
        return
    n = int(rl_spin_episodes.get())
    ql_agent.epsilon = 1.0
    ql_training_active = True
    ql_btn_train.config(text="⏹  ARRÊTER")
    rl_progress.config(maximum=n, value=0)
    rl_progress.pack(fill="x", pady=(0, 8))
    _rl_log(f"Début : {n} épisodes | α={ql_agent.alpha} | γ={ql_agent.gamma}")
    threading.Thread(
        target=_rl_training_loop, args=(n,), daemon=True
    ).start()


def _rl_stop_training():
    global ql_training_active
    ql_training_active = False


def _rl_toggle_training():
    if ql_training_active:
        _rl_stop_training()
        ql_btn_train.config(text="▶  APPRENTISSAGE (Q-learning)")
        rl_progress.pack_forget()
        _rl_log("Entraînement interrompu.")
    else:
        _rl_start_training()


def _rl_save_qtable():
    path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON", "*.json")],
        initialfile=QTABLE_DEFAULT,
        initialdir=_SCRIPT_DIR,
    )
    if path:
        ql_agent.save_q_table(path)
        _rl_log(f"Table Q sauvegardée : {path}")


def _rl_load_qtable():
    path = filedialog.askopenfilename(
        filetypes=[("JSON", "*.json")],
        initialdir=_SCRIPT_DIR,
    )
    if path:
        try:
            ql_agent.load_q_table(path)
            _rl_refresh_stats()
            _rl_log(f"Table Q chargée : {path} ({len(ql_agent.q_table)} états)")
        except Exception as e:
            messagebox.showerror("Erreur", f"Chargement impossible : {e}")


def _rl_reset_agent():
    global ql_agent
    if messagebox.askyesno("Reset", "Effacer la table Q et les statistiques ?"):
        ql_agent = QLearningAgent()
        _rl_update_grid_from_cells([""] * 9)
        _rl_refresh_stats()
        _rl_log("Table Q réinitialisée.")


def _rl_demo_step():
    if not ql_demo_active or not ql_agent.is_trained():
        return

    valid = ql_env.valid_actions()
    if not valid:
        ql_env.reset()
        _rl_update_grid_from_cells(ql_env.cells)
        if ql_demo_active:
            window_rl.after(int(rl_spin_speed.get()), _rl_demo_step)
        return

    state_key = board_to_key(ql_env.cells, ql_env.current)
    action = ql_agent.choose_best_action(state_key, valid)
    if action is None:
        _rl_stop_demo()
        return

    _, reward, done = ql_env.step(action)
    _rl_update_grid_from_cells(ql_env.cells)

    if done:
        w = check_winner_cells(ql_env.cells)
        _rl_log(f"Démo — fin de partie : {w} (r={reward:+.1f})")
        ql_env.reset()
        _rl_update_grid_from_cells(ql_env.cells)

    if ql_demo_active:
        window_rl.after(int(rl_spin_speed.get()), _rl_demo_step)


def _rl_start_demo():
    global ql_demo_active
    if not ql_agent.is_trained():
        messagebox.showwarning(
            "Table Q vide",
            "Entraînez l'agent ou chargez une table Q avant la démo.",
        )
        return
    if ql_demo_active:
        _rl_stop_demo()
        return
    ql_demo_active = True
    ql_demo_steps[0] = 0
    ql_env.reset()
    _rl_update_grid_from_cells(ql_env.cells)
    ql_btn_demo.config(text="⏹  ARRÊTER DÉMO")
    _rl_log("Démonstration IA vs IA (politique apprise)…")
    window_rl.after(int(rl_spin_speed.get()), _rl_demo_step)


def _rl_stop_demo():
    global ql_demo_active
    ql_demo_active = False
    ql_btn_demo.config(text="🎯  DÉMO (exploitation)")



window_login = tkinter.Tk()
window_login.title("CONNEXION")
window_login.config(background=COLOR_DEEP_BLACK)
window_login.geometry("400x520")

f_title, f_stats, f_btn, f_grid = get_custom_fonts()


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



window_main = tkinter.Toplevel()
window_main.title("MENU")
window_main.config(background=COLOR_DEEP_BLACK)
window_main.withdraw()
window_main.protocol("WM_DELETE_WINDOW", quit)
window_main.geometry("420x600")

frame_main = tkinter.Frame(window_main, background=COLOR_DEEP_BLACK)
frame_main.pack(expand=True, padx=40, fill="x")

tkinter.Label(frame_main, text="MENU", font=f_title, background=COLOR_DEEP_BLACK, foreground=COLOR_GREEN_NEON).pack(pady=10)
label_stats = tkinter.Label(frame_main, text="", font=f_stats, background=COLOR_DEEP_BLACK, foreground=COLOR_GOLD_VICTORY)
label_stats.pack(pady=(0, 30))

create_gaming_button(frame_main, "[ P2P ]  DUEL LOCAL", lambda: lancer_partie(False), COLOR_TILE_BG, "#171A21", f_btn, pady=8)
create_gaming_button(frame_main, "[ P2IA ]  AFFRONTER L'IA", lambda: lancer_partie(True), COLOR_TILE_BG, COLOR_TILE_HOVER, f_btn, fg_color=COLOR_GREEN_NEON, border_c=COLOR_GREEN_NEON, pady=8)
create_gaming_button(
    frame_main,
    "[ IA×IA ]  ENTRAÎNEMENT Q-LEARNING",
    ouvrir_entrainement_rl,
    "#1a237e",
    "#283593",
    f_btn,
    fg_color="#90caf9",
    border_c="#3949ab",
    pady=8,
)

tkinter.Frame(frame_main, height=2, bg=COLOR_INTERFACE_BORDER).pack(fill="x", pady=25)
create_gaming_button(frame_main, "DECONNEXION", logout, COLOR_DEEP_BLACK, COLOR_TILE_BG, ("Arial", 10, "bold"), fg_color=COLOR_TEXT_MUTED, pady=2)
create_gaming_button(frame_main, "ÉTEINDRE LE SYSTÈME", quit, "#73001C", "#4A0012", f_btn, pady=10)



window_game = tkinter.Toplevel()
window_game.title("JEU")
window_game.resizable(False, False)
window_game.withdraw()
window_game.config(background=COLOR_DEEP_BLACK)
window_game.protocol("WM_DELETE_WINDOW", quit)


label = tkinter.Label(window_game, text=f"TOUR : JOUEUR {curr_player}", font=("Impact", 18), background=COLOR_DEEP_BLACK, foreground=COLOR_RED_NEON)
label.pack(pady=20)


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



window_rl = tkinter.Toplevel()
window_rl.title("Q-Learning — IA vs IA")
window_rl.config(background=COLOR_DEEP_BLACK)
window_rl.geometry("920x580")
window_rl.resizable(False, False)
window_rl.withdraw()
window_rl.protocol("WM_DELETE_WINDOW", retour_menu_depuis_rl)

rl_main = tkinter.Frame(window_rl, background=COLOR_DEEP_BLACK)
rl_main.pack(fill="both", expand=True, padx=16, pady=16)

rl_left = tkinter.Frame(rl_main, background=COLOR_DEEP_BLACK)
rl_left.pack(side="left", padx=(0, 20))

tkinter.Label(
    rl_left,
    text="GRILLE D'ENTRAÎNEMENT",
    font=("Impact", 14),
    background=COLOR_DEEP_BLACK,
    foreground=COLOR_GOLD_VICTORY,
).pack(pady=(0, 8))

rl_grid_frame = tkinter.Frame(rl_left, background=COLOR_GRID_LINE)
rl_grid_frame.pack()

rl_board = [[None] * 3 for _ in range(3)]
for r in range(3):
    for c in range(3):
        b = tkinter.Label(
            rl_grid_frame,
            text="",
            font=f_grid,
            width=3,
            height=1,
            background=COLOR_TILE_BG,
            foreground=COLOR_TEXT_MUTED,
        )
        b.grid(row=r, column=c, padx=4, pady=4, ipadx=8, ipady=8)
        rl_board[r][c] = b

tkinter.Label(
    rl_left,
    text="🟥 X  vs  🟩 O  — auto-apprentissage",
    font=("Arial", 9),
    background=COLOR_DEEP_BLACK,
    foreground=COLOR_TEXT_MUTED,
).pack(pady=10)

rl_right = tkinter.Frame(rl_main, background=COLOR_DEEP_BLACK)
rl_right.pack(side="left", fill="both", expand=True)

ql_btn_train = create_gaming_button(
    rl_right,
    "▶  APPRENTISSAGE (Q-learning)",
    _rl_toggle_training,
    "#1565c0",
    "#0d47a1",
    f_btn,
)
ql_btn_demo = create_gaming_button(
    rl_right,
    "🎯  DÉMO (exploitation)",
    _rl_start_demo,
    "#2e7d32",
    "#1b5e20",
    f_btn,
)

hp_frame = tkinter.LabelFrame(
    rl_right,
    text=" Hyperparamètres ",
    font=("Arial", 9, "bold"),
    background=COLOR_DEEP_BLACK,
    foreground=COLOR_TEXT_MUTED,
)
hp_frame.pack(fill="x", pady=10)

for i, (lbl, default, from_, to, step) in enumerate([
    ("α (apprentissage)", 0.1, 0.01, 1.0, 0.01),
    ("γ (escompte)", 0.95, 0.1, 0.99, 0.01),
    ("Épisodes", 3000, 100, 50000, 500),
    ("Vitesse démo (ms)", 400, 50, 2000, 50),
]):
    tkinter.Label(
        hp_frame, text=lbl, font=("Arial", 9),
        background=COLOR_DEEP_BLACK, foreground="white",
    ).grid(row=i, column=0, sticky="w", padx=8, pady=4)
    sb = tkinter.Spinbox(
        hp_frame, from_=from_, to=to, increment=step,
        width=10, font=("Arial", 10),
        bg=COLOR_TILE_BG, fg="white",
    )
    sb.delete(0, tkinter.END)
    sb.insert(0, str(default))
    sb.grid(row=i, column=1, padx=8, pady=4)

rl_spin_alpha = hp_frame.grid_slaves(row=0, column=1)[0]
rl_spin_gamma = hp_frame.grid_slaves(row=1, column=1)[0]
rl_spin_episodes = hp_frame.grid_slaves(row=2, column=1)[0]
rl_spin_speed = hp_frame.grid_slaves(row=3, column=1)[0]

qt_frame = tkinter.Frame(rl_right, background=COLOR_DEEP_BLACK)
qt_frame.pack(fill="x", pady=6)
for txt, cmd in [
    ("Sauvegarder Q", _rl_save_qtable),
    ("Charger Q", _rl_load_qtable),
    ("Reset Q", _rl_reset_agent),
]:
    tkinter.Button(
        qt_frame, text=txt, font=("Arial", 9, "bold"),
        bg=COLOR_TILE_BG, fg="white", relief="flat",
        command=cmd, cursor="hand2",
    ).pack(side="left", expand=True, fill="x", padx=2, ipady=6)

rl_progress = ttk.Progressbar(rl_right, mode="determinate")

stats_frame = tkinter.LabelFrame(
    rl_right, text=" Statistiques ",
    font=("Arial", 9, "bold"),
    background=COLOR_DEEP_BLACK, foreground=COLOR_TEXT_MUTED,
)
stats_frame.pack(fill="x", pady=8)

rl_lbl_episode = tkinter.Label(stats_frame, text="0", font=("Arial", 10, "bold"),
    background=COLOR_DEEP_BLACK, foreground=COLOR_GOLD_VICTORY)
rl_lbl_epsilon = tkinter.Label(stats_frame, text="1.000", font=("Arial", 10),
    background=COLOR_DEEP_BLACK, foreground="white")
rl_lbl_wins = tkinter.Label(stats_frame, text="—", font=("Arial", 9),
    background=COLOR_DEEP_BLACK, foreground=COLOR_GREEN_NEON)
rl_lbl_rate = tkinter.Label(stats_frame, text="—", font=("Arial", 9),
    background=COLOR_DEEP_BLACK, foreground=COLOR_TEXT_MUTED)

for i, (t, w) in enumerate([
    ("Épisodes :", rl_lbl_episode),
    ("ε :", rl_lbl_epsilon),
    ("Résultats :", rl_lbl_wins),
    ("", rl_lbl_rate),
]):
    tkinter.Label(stats_frame, text=t, font=("Arial", 9),
        background=COLOR_DEEP_BLACK, foreground=COLOR_TEXT_MUTED,
    ).grid(row=i, column=0, sticky="w", padx=8, pady=2)
    w.grid(row=i, column=1, sticky="w", padx=8, pady=2)

rl_log = tkinter.Text(
    rl_right, height=8, font=("Consolas", 9),
    bg="#1e1e1e", fg="#d4d4d4", relief="flat",
)
rl_log.pack(fill="both", expand=True, pady=(8, 0))

create_gaming_button(
    rl_right, "RETOUR AU MENU", retour_menu_depuis_rl,
    COLOR_DEEP_BLACK, COLOR_TILE_BG, ("Arial", 10, "bold"),
    fg_color=COLOR_TEXT_MUTED, pady=4,
)

_default_qt = os.path.join(_SCRIPT_DIR, QTABLE_DEFAULT)
if os.path.exists(_default_qt):
    try:
        ql_agent.load_q_table(_default_qt, for_inference=True)
    except Exception:
        pass

window_login.mainloop()