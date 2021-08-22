from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
from copy import deepcopy
from string import ascii_letters
from generator_completed_sudoku import generator_completed_sudoku
from generator_sudoku import generator_sudoku, sudoku_solver
from matrix_filling import sudoku_drawer
import config


bot = Bot(config.TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['db'])
async def db_sender(message):
    if message.from_user.id == 484620905:
        with open('users.db', 'rb') as file:
            await bot.send_document(message.chat.id, ('users.db', file))


@dp.message_handler(commands=['start'])
async def starter(message):
    item = InlineKeyboardButton("✏️ Начать игру", callback_data='NewGame')
    markup = InlineKeyboardMarkup().add(item)
    await message.answer("Начать новую игру - /game\n\n"
                         "Все буквы латиницей!\n\n"
                         "Ввести изменение - *A4 8*\n"
                         "*A* - столбик, *4* - рядочек, *8* - цифра\n\n"
                         "Удалить цифру - *A4 0*\n\n"
                         "Посмотреть решение - /answer\n\n"
                         "Очистить поле - /clear\n\n"
                         "Правила судоку - /help\n\n"
                         "Поддержать пилупу - _4441114447909910_", parse_mode='Markdown', reply_markup=markup)


@dp.message_handler(commands=['help'])
async def helper(message):
    await message.answer("http://surl.li/xhnz")


@dp.message_handler(commands=['game'])
async def started_field(message):

    # this function sends starter field for sudoku
    # and saves started tab, user tab, solved tab, user id and message id in database

    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()

    # check id in database

    cursor.execute(f"SELECT id FROM sudoku_users WHERE id = {message.chat.id}")
    data = cursor.fetchone()
    connect.commit()
    if data is None:
        solved_sudoku = generator_completed_sudoku()
        sudoku = generator_sudoku(solved_sudoku, 50)
        starter_tab = deepcopy(sudoku)

        sudoku_drawer(sudoku, sudoku)

        with open(config.TABLE, 'rb') as file:
            msg = await bot.send_photo(message.chat.id, file)

        user_info = (message.chat.id, str(starter_tab), str(sudoku), msg.message_id)
        cursor.execute("INSERT INTO sudoku_users VALUES(?, ?, ?, ?);", user_info)
        connect.commit()
    else:
        item1 = InlineKeyboardButton("да", callback_data='game_True')
        item2 = InlineKeyboardButton("нет", callback_data='game_False')
        markup = InlineKeyboardMarkup().add(item1, item2)
        await message.answer("хочешь начать заново?", reply_markup=markup)
    connect.close()


@dp.message_handler(commands=['answer'])
async def answer(message):
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute(f"SELECT * FROM sudoku_users WHERE id = {message.chat.id}")
    data = cursor.fetchall()
    connect.commit()

    if data != []:
        item1 = InlineKeyboardButton("да", callback_data='answer_True')
        item2 = InlineKeyboardButton("нет", callback_data='answer_False')
        markup = InlineKeyboardMarkup().add(item1, item2)
        await message.answer("хочешь узнать ответ?", reply_markup=markup)
    connect.close()


@dp.message_handler(commands=['clear'])
async def clear_field(message):
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute(f"SELECT * FROM sudoku_users WHERE id = {message.chat.id}")
    data = cursor.fetchall()
    connect.commit()
    connect.close()

    if data != []:
        item1 = InlineKeyboardButton("да", callback_data='clear_True')
        item2 = InlineKeyboardButton("нет", callback_data='clear_False')
        markup = InlineKeyboardMarkup().add(item1, item2)
        await message.answer("хочешь очистить поле?", reply_markup=markup)


@dp.message_handler(content_types=['text'])
async def tab_change(message):
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute(f"SELECT * FROM sudoku_users WHERE id = {message.chat.id}")
    data = cursor.fetchall()
    connect.commit()
    if data != []:
        user_info = data[0]
        starter_tab, sudoku, last_message_id = eval(user_info[1]), eval(user_info[2]), int(user_info[3])
        text = message.text
        if (text[0] in ascii_letters) and text[1].isdigit() and (text[2] == ' ') and text[3].isdigit() \
                and (len(text) == 4):
            column = ord(text[0].lower()) - 97
            row = int(text[1]) - 1
            num = int(text[3])
            if starter_tab[row][column] != 0:
                item1 = InlineKeyboardButton('да', callback_data='deception_True')
                item2 = InlineKeyboardButton("нет", callback_data='deception_False')
                markup = InlineKeyboardMarkup().add(item1, item2)
                await message.answer("хочешь меня надурить?", reply_markup=markup)
            else:
                sudoku[row][column] = num
                sudoku_drawer(sudoku, starter_tab)
                with open(config.TABLE, 'rb') as file:
                    msg = await bot.send_photo(message.chat.id, file)
                await bot.delete_message(message.chat.id, last_message_id)

                cursor.execute(f"DELETE FROM sudoku_users WHERE id = {message.chat.id}")
                user_info = (message.chat.id, str(starter_tab), str(sudoku), msg.message_id)
                cursor.execute("INSERT INTO sudoku_users VALUES(?, ?, ?, ?);", user_info)
                connect.commit()
                if sudoku == sudoku_solver(starter_tab):
                    item = InlineKeyboardButton("✏️ Начать новую игру", callback_data='NewGame')
                    markup = InlineKeyboardMarkup().add(item)
                    await message.reply('Победа!', reply_markup=markup)
                    cursor.execute(f"DELETE FROM sudoku_users WHERE id = {message.chat.id}")
                    connect.commit()
        connect.close()


@dp.callback_query_handler()
async def callback_inline(call):
    if call.data == 'deception_True':
        await bot.send_message(call.message.chat.id, "у тебя ничего не выйдет")
    if call.data == 'deception_False':
        await bot.send_message(call.message.chat.id, "случайность, со всеми бывает")

    if call.data == 'game_True':
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()

        cursor.execute(f"DELETE FROM sudoku_users WHERE id = {call.message.chat.id}")

        solved_sudoku = generator_completed_sudoku()
        sudoku = generator_sudoku(solved_sudoku, 50)
        starter_tab = deepcopy(sudoku)

        sudoku_drawer(sudoku, sudoku)

        with open(config.TABLE, 'rb') as file:
            msg = await bot.send_photo(call.message.chat.id, file)

        user_info = (call.message.chat.id, str(starter_tab), str(sudoku), msg.message_id)
        cursor.execute("INSERT INTO sudoku_users VALUES(?, ?, ?, ?);", user_info)

        connect.commit()
        connect.close()
    if call.data == 'game_False':
        await bot.send_message(call.message.chat.id, "будь осторежнее")

    if call.data == 'answer_True':
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute(f"SELECT * FROM sudoku_users WHERE id = {call.message.chat.id}")
        user_info = cursor.fetchall()[0]
        connect.commit()

        starter_tab, last_message_id = eval(user_info[1]), int(user_info[3])
        sudoku_drawer(sudoku_solver(starter_tab), starter_tab)
        with open(config.TABLE, 'rb') as file:
            await bot.send_photo(call.message.chat.id, file)

        cursor.execute(f"DELETE FROM sudoku_users WHERE id = {call.message.chat.id}")
        connect.commit()
        connect.close()
    if call.data == 'answer_False':
        await bot.send_message(call.message.chat.id, "хорошо что я спросил")

    if call.data == 'clear_True':
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute(f"SELECT * FROM sudoku_users WHERE id = {call.message.chat.id}")
        user_info = cursor.fetchall()[0]
        connect.commit()

        starter_tab, sudoku, last_message_id = eval(user_info[1]), eval(user_info[2]), int(user_info[3])
        sudoku_drawer(starter_tab, starter_tab)
        with open(config.TABLE, 'rb') as file:
            msg = await bot.send_photo(call.message.chat.id, file)

        cursor.execute(f"DELETE FROM sudoku_users WHERE id = {call.message.chat.id}")

        user_info = (call.message.chat.id, str(starter_tab), str(sudoku), msg.message_id)
        cursor.execute("INSERT INTO sudoku_users VALUES(?, ?, ?, ?);", user_info)
        connect.commit()
        connect.close()
        await bot.delete_message(call.message.chat.id, last_message_id)
    if call.data == 'clear_False':
        await bot.send_message(call.message.chat.id, "тогда продолжай")

    if call.data == 'NewGame':
        await started_field(call.message)

    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text=call.message.text)


async def set_commands(dp):
    await bot.set_my_commands([types.BotCommand("/start", "начать"), types.BotCommand("/game", "новая игра"),
                               types.BotCommand("/clear", "очистить поле"), types.BotCommand("/answer", "решение"),
                               types.BotCommand("/help", "правила")])


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=set_commands)
