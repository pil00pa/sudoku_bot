from copy import deepcopy


def nums_in_row(matrix, row):

    # counting elements in the row

    num = matrix[row]
    return num


def nums_in_column(matrix, column):

    # counting elements in the column

    num = []
    for i in range(len(matrix)):
        num.append(matrix[i][column])
    return num


def nums_in_cube(matrix, row, column):

    # counting elements in the cube

    num = []
    part_row = int(row/3)
    part_column = int(column/3)
    for row_index in range(part_row * 3, (part_row + 1) * 3):
        for column_index in range(part_column * 3, (part_column + 1) * 3):
            num.append(matrix[row_index][column_index])
    return num


def list_of_unused_nums(matrix, row, column):

    # counting possible options for this cell

    used_nums = nums_in_column(matrix, column) + nums_in_row(matrix, row) + nums_in_cube(matrix, row, column)
    unused_nums = []
    for dig in range(1, 10):
        if dig in used_nums:
            pass
        else:
            unused_nums.append(dig)
    return unused_nums


def sudoku_solver(matrix):

    # solves sudoku

    matrix = deepcopy(matrix)
    matrix_size = len(matrix) * len(matrix[0])
    s = 0
    while s < matrix_size:
        row_index = 0
        for row in matrix:
            column_index = 0
            for el in row:
                if (el == 0) and (len(list_of_unused_nums(matrix, row_index, column_index)) == 1):
                    unused_num = list_of_unused_nums(matrix, row_index, column_index)
                    row[column_index] = unused_num[0]
                    s = 0
                else:
                    s += 1
                column_index += 1
            row_index += 1
    return matrix
