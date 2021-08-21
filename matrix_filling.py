from PIL import Image, ImageDraw, ImageFont
import config


def sudoku_drawer(sudoku, starter_tab):
    sud_tab = Image.open(config.STARTER_TABLE)
    draw = ImageDraw.Draw(sud_tab)

    headline = ImageFont.truetype(config.FONT, size=72)

    row_index = 0
    for row in sudoku:
        column_index = 0
        for el in row:
            if el != 0:
                x = column_index * 100 + 132
                y = row_index * 100 + 116
                if starter_tab[row_index][column_index] == el:
                    draw.text((x, y), str(el), (32, 0, 46), font=headline)
                else:
                    draw.text((x, y), str(el), (65, 105, 225), font=headline)
            column_index += 1
        row_index += 1
        sud_tab.save(config.TABLE)
    return 0

