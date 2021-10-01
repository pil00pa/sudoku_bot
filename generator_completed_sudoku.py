from random import randrange


def transposing(matrix):
    return list(map(list, zip(*matrix)))


def swap_rows(matrix):
    row1 = randrange(9)
    area = row1 // 3
    row2 = randrange(area * 3, area * 3 + 3)
    while row1 == row2:
        row2 = randrange(area * 3, area * 3 + 3)
    matrix[row1], matrix[row2] = matrix[row2], matrix[row1]


def swap_columns(matrix):
    column1 = randrange(9)
    area = column1 // 3
    column2 = randrange(area * 3, area * 3 + 3)
    while column1 == column2:
        column2 = randrange(area * 3, area * 3 + 3)
    for row_index in range(len(matrix)):
        matrix[row_index][column1], matrix[row_index][column2] = matrix[row_index][column2], matrix[row_index][column1]


def swap_rows_area(matrix):
    area1 = randrange(3)
    area2 = randrange(3)
    while area1 == area2:
        area2 = randrange(3)
    for row_index in range(3):
        matrix[row_index + area1*3], matrix[row_index + area2*3] = \
            matrix[row_index + area2*3], matrix[row_index + area1*3]


def generator_completed_sudoku():
    n = 3
    table = [[((i * n + i // n + j) % (n * n) + 1) for j in range(n * n)] for i in range(n * n)]
    for i in range(200):
        j = randrange(4)
        if j == 0:
            table = transposing(table)
        elif j == 1:
            swap_rows(table)
        elif j == 2:
            swap_columns(table)
        elif j == 3:
            swap_rows_area(table)
    return table

n = 3
for i in [[((i * n + i // n + j) % (n * n) + 1) for j in range(n * n)] for i in range(n * n)]:
    print(i)