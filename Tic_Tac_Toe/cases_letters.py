coord_case = [
    ["A1", "A2", "A3"],
    ["B1", "B2", "B3"],
    ["C1", "C2", "C3"]
]

def create_cases(board):
    cases = {}

    for row in range(3):
        for column in range(3):
            case = coord_case[row][column]
            cases[case] = board[row][column]

    return cases

def get_cases_libres(cases):
    cases_libres = []

    for coord, valeur in cases.items():
        if valeur == " ":   # case vide
            cases_libres.append(coord)

    return cases_libres

import random

def get_libres():
    libres = []

    mapping = {
        "A1": (0,0), "A2": (0,1), "A3": (0,2),
        "B1": (1,0), "B2": (1,1), "B3": (1,2),
        "C1": (2,0), "C2": (2,1), "C3": (2,2)
    }

    for coord, (r, c) in mapping.items():
        if board[r][c]["text"] == "":
            libres.append(coord)

    return libres


def ia_joue():
    global curr_player, game_over

    if game_over:
        return

    libres = get_libres()

    if not libres:
        return

    choix = random.choice(libres)

    mapping = {
        "A1": (0,0), "A2": (0,1), "A3": (0,2),
        "B1": (1,0), "B2": (1,1), "B3": (1,2),
        "C1": (2,0), "C2": (2,1), "C3": (2,2)
    }

    r, c = mapping[choix]

    board[r][c]["text"] = playerO

    check_winner()

    if not game_over:
        curr_player = playerX
        label["text"] = "Au tour de " + curr_player