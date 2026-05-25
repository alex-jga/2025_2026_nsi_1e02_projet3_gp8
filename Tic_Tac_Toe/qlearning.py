"""
Q-Learning — Morpion (Tic Tac Toe)
==================================
Apprentissage par renforcement tabulaire pour le morpion 3×3.
État = plateau + joueur courant ; actions = cases libres (0..8).
"""

import json
import random

playerX = "X"
playerO = "O"
EMPTY_CELL = " "  # marqueur fixe pour une case vide (9 caractères toujours)
N_ACTIONS = 9

R_WIN = 10.0
R_LOSE = -10.0
R_TIE = 1.0
R_STEP = -0.1

QTABLE_DEFAULT = "qtable_morpion.json"


def _encode_cell(cell):
    """Encode une case : X, O ou espace (vide)."""
    return cell if cell in (playerX, playerO) else EMPTY_CELL


def board_to_key(cells, current_player):
    """Clé d'état : exactement 9 cases encodées + '|' + joueur courant."""
    board = "".join(_encode_cell(c) for c in cells[:9])
    if len(board) < 9:
        board = board.ljust(9, EMPTY_CELL)
    return board + "|" + current_player


def key_to_cells(state_key):
    """Décode la partie plateau d'une clé d'état."""
    board_part = state_key.rsplit("|", 1)[0] if "|" in state_key else state_key[:9]
    board_part = board_part.ljust(9, EMPTY_CELL)[:9]
    return [c if c in (playerX, playerO) else "" for c in board_part]


def index_to_rc(action):
    return action // 3, action % 3


def rc_to_index(row, col):
    return row * 3 + col


def check_winner_cells(cells):
    """Retourne 'X', 'O', 'Tie' ou None."""
    lines = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6),
    ]
    for a, b, c in lines:
        if cells[a] and cells[a] == cells[b] == cells[c]:
            return cells[a]
    if all(cells[i] for i in range(9)):
        return "Tie"
    return None


class TicTacToeEnv:
    """Environnement morpion pour l'entraînement."""

    def __init__(self):
        self.cells = [""] * 9
        self.current = playerX

    def reset(self, first_player=None):
        self.cells = [""] * 9
        self.current = first_player or random.choice([playerX, playerO])
        return board_to_key(self.cells, self.current)

    def valid_actions(self, cells=None, player=None):
        c = cells if cells is not None else self.cells
        return [i for i in range(9) if c[i] == ""]

    def step(self, action):
        """
        Joue l'action pour le joueur courant.
        Retourne (next_state, reward, done) du point de vue du joueur qui a joué.
        """
        if self.cells[action] != "":
            return board_to_key(self.cells, self.current), R_LOSE, True

        mover = self.current
        self.cells[action] = mover
        result = check_winner_cells(self.cells)

        if result == mover:
            return board_to_key(self.cells, self.current), R_WIN, True
        if result == "Tie":
            return board_to_key(self.cells, self.current), R_TIE, True
        if result and result != mover:
            return board_to_key(self.cells, self.current), R_LOSE, True

        self.current = playerO if mover == playerX else playerX
        return board_to_key(self.cells, self.current), R_STEP, False

    def cells_from_key(self, state_key):
        return key_to_cells(state_key)

    def player_from_key(self, state_key):
        if "|" in state_key:
            return state_key.rsplit("|", 1)[1]
        return state_key[-1]


class QLearningAgent:
    """Agent Q-learning avec table Q en dictionnaire."""

    def __init__(self, alpha=0.1, gamma=0.95, epsilon=1.0):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = {}
        self.episode_count = 0
        self.win_x = 0
        self.win_o = 0
        self.ties = 0

    def _q_row(self, state):
        if state not in self.q_table:
            self.q_table[state] = [0.0] * N_ACTIONS
        return self.q_table[state]

    def choose_action_epsilon_greedy(self, state, valid_actions):
        if not valid_actions:
            return None
        if random.random() < self.epsilon:
            return random.choice(valid_actions)
        return self.choose_best_action(state, valid_actions)

    def choose_best_action(self, state, valid_actions):
        if not valid_actions:
            return None
        q = self._q_row(state)
        best_val = max(q[a] for a in valid_actions)
        best = [a for a in valid_actions if q[a] == best_val]
        return random.choice(best)

    def update_q_value(self, state, action, reward, next_state, next_valid):
        q = self._q_row(state)
        current_q = q[action]
        if next_valid:
            next_q = self._q_row(next_state)
            best_next = max(next_q[a] for a in next_valid)
        else:
            best_next = 0.0
        target = reward + self.gamma * best_next
        q[action] += self.alpha * (target - current_q)

    def decay_epsilon(self, min_epsilon=0.05, decay_rate=0.995):
        self.epsilon = max(min_epsilon, self.epsilon * decay_rate)

    def save_q_table(self, filepath):
        data = {
            "q_table": self.q_table,
            "alpha": self.alpha,
            "gamma": self.gamma,
            "epsilon": self.epsilon,
            "episode_count": self.episode_count,
            "win_x": self.win_x,
            "win_o": self.win_o,
            "ties": self.ties,
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_q_table(self, filepath, for_inference=False):
        """
        Charge une table Q sauvegardée.

        for_inference=True : epsilon=0 (démo / partie vs humain, pas d'exploration).
        for_inference=False : conserve epsilon du fichier (reprise d'entraînement).
        """
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.q_table = {k: list(v) for k, v in data["q_table"].items()}
        self.alpha = data.get("alpha", self.alpha)
        self.gamma = data.get("gamma", self.gamma)
        if for_inference:
            self.epsilon = 0.0
        else:
            self.epsilon = data.get("epsilon", self.epsilon)
        self.episode_count = data.get("episode_count", 0)
        self.win_x = data.get("win_x", 0)
        self.win_o = data.get("win_o", 0)
        self.ties = data.get("ties", 0)

    def is_trained(self):
        return len(self.q_table) > 0


def run_training_episode(agent, env):
    """
    Un épisode d'auto-apprentissage (IA vs IA) : le même agent joue X et O.
    Retourne (total_reward_x_perspective, winner, path_cells_list).
    """
    state = env.reset()
    path = [list(env.cells)]
    total_reward = 0.0
    mover = env.current

    for _ in range(9):
        valid = env.valid_actions()
        action = agent.choose_action_epsilon_greedy(state, valid)
        if action is None:
            break

        next_state, reward, done = env.step(action)
        next_valid = env.valid_actions() if not done else []
        agent.update_q_value(state, action, reward, next_state, next_valid)

        total_reward += reward
        path.append(list(env.cells))
        state = next_state
        mover = env.current

        if done:
            result = check_winner_cells(env.cells)
            if result == playerX:
                agent.win_x += 1
            elif result == playerO:
                agent.win_o += 1
            elif result == "Tie":
                agent.ties += 1
            return total_reward, result, path

    return total_reward, None, path


def board_from_env_cells(cells):
    """Convertit la liste plate en grille 3×3 de caractères."""
    return [[cells[r * 3 + c] or " " for c in range(3)] for r in range(3)]


def q_move_for_player(agent, board_buttons, player):
    """
    Coup greedy pour le joueur donné à partir de l'état du plateau UI.
    board_buttons : grille 3×3 de widgets tkinter Button.
    """
    cells = []
    for r in range(3):
        for c in range(3):
            t = board_buttons[r][c]["text"]
            cells.append(t if t in (playerX, playerO) else "")
    state = board_to_key(cells, player)
    valid = [i for i in range(9) if cells[i] == ""]
    if not valid or not agent.is_trained():
        return None
    action = agent.choose_best_action(state, valid)
    if action is None:
        return None
    return index_to_rc(action)
