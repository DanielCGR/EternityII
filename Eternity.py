import math
from ortools.sat.python import cp_model

def read_puzzle(file):
    if isinstance(file, str):
        with open(file, 'r') as f:
            lines = f.readlines()
    else:
        lines = file.readlines()
    puzzle = []

    for line in lines:
        row_pieces = line.strip().split()
        row = []
        for piece in row_pieces:
            row.append(piece)
        puzzle.append(row)

    return puzzle


def solve_eternity(puzzle):
    n = len(puzzle)
    height = int(math.sqrt(n))
    width = int(n / height)

    model = cp_model.CpModel()

    # Variables
    cells = [[model.NewIntVar(1, width * height, f'cell_{i}_{j}') for j in range(width)] for i in range(height)]
    rotations = [[model.NewIntVar(0, 3, f'rot_{i}_{j}') for j in range(width)] for i in range(height)]

    # Constraints
    # Each piece is used exactly once
    model.AddAllDifferent([cells[i][j] for i in range(width) for j in range(height)])

    # Add edge constraints
    for i in range(width):
        for j in range(height):
            if i < width - 1:
                add_edge_constraint(model, puzzle, cells[i][j], rotations[i][j], cells[i + 1][j], rotations[i + 1][j], 2)
            if j < height - 1:
                add_edge_constraint(model, puzzle, cells[i][j], rotations[i][j], cells[i][j + 1], rotations[i][j + 1], 1)

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Extract solution
    if status == cp_model.OPTIMAL:
        solution = [[solver.Value(cells[i][j]) for j in range(width)] for i in range(height)]
        rotations = [[solver.Value(rotations[i][j]) for j in range(width)] for i in range(height)]
        return solution, rotations
    else:
        return [], []


def add_edge_constraint(model, puzzle, cell1, rotation1, cell2, rotation2, edge):
    allowed_assignments = []
    n = len(puzzle)
    height = n // int(math.sqrt(n))
    width = n // height

    for piece1 in range(width * height):
        for rot1 in range(4):
            for piece2 in range(width * height):
                for rot2 in range(4):
                    if (puzzle[piece1][(edge - rot1) % 4] == puzzle[piece2][(edge - rot2 + 2) % 4] and
                        (puzzle[piece1][(edge - rot1) % 4] != '-' or
                         (puzzle[piece1][(edge - rot1) % 4] == '-' and
                          (edge - rot2) % 4 < 2 and puzzle[piece2][(edge - 2 + rot2) % 4] == '-'))):

                        valid_rotation = True
                        for i in range(1, 4):
                            if (puzzle[piece1][(edge - rot1 + i) % 4] != '-' and puzzle[piece2][(edge - 2 + rot2 + i) % 4] != '-' and
                                puzzle[piece1][(edge - rot1 + i) % 4] == puzzle[piece2][(edge - 2 + rot2 + i) % 4]):
                                valid_rotation = False
                                break

                        if valid_rotation:
                            allowed_assignments.append((piece1 + 1, rot1, piece2 + 1, rot2))

    model.AddAllowedAssignments([cell1, rotation1, cell2, rotation2], allowed_assignments)