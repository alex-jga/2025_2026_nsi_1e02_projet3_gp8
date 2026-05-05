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