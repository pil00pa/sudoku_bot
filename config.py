import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = str(os.getenv('TOKEN'))
STARTER_TABLE = 'table_for_sudoku.jpg'
TABLE = 'sudoku.jpg'
FONT = 'CeraPro-Light.ttf'
