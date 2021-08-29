from random import randrange
from sudoku_solving import sudoku_solver
from copy import deepcopy


def sudoku_checker(matrix):
    matrix_size = len(matrix) * len(matrix[0])
    i = 0
    while i < matrix_size:
        for row in matrix:
            for column in row:
                if column == 0:
                    return False
        i += 1
    return True


def generator_sudoku(completed_sudoku, difficulty_level=40):
    sudoku = deepcopy(completed_sudoku)
    while True:
        i = 0
        j = 0
        while i < difficulty_level:
            row_index = randrange(9)
            column_index = randrange(9)
            num = sudoku[row_index][column_index]
            if num != 0:
                sudoku[row_index][column_index] = 0
                solved_sudoku = sudoku_solver(sudoku)
                if sudoku_checker(solved_sudoku):
                    i += 1
                else:
                    sudoku[row_index][column_index] = num
                    j += 1
                    print(j)
                    if j == difficulty_level:
                        break
        return sudoku

