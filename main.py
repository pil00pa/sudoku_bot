from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageCantBeDeleted, ChatNotFound
import sqlite3
from string import ascii_letters
from generator_sudoku import generator_sudoku, sudoku_solver
from matrix_filling import sudoku_drawer
import config

try:
    bot = Bot(config.TOKEN)
    dp = Dispatcher(bot)


    @dp.message_handler(commands=['db'])
    async def db_sender(message):
        if message.from_user.id == 484620905:
            with open('users.db', 'rb') as file:
                await bot.send_document(message.chat.id, ('users.db', file))


    @dp.message_handler(commands=['start_mailing'])
    async def add_sender(message):
        if message.from_user.id == 484620905:
            connect = sqlite3.connect('users.db')
            cursor = connect.cursor()
            cursor.execute("SELECT id FROM id_n_dif_n_wins")
            data = cursor.fetchall()
            connect.close()
            for user_id in data:
                add_photo = open('uebak_image.jpg', 'rb')
                try:
                    await bot.send_photo(user_id[0], photo=add_photo, caption=
                    """*Нужны аккаунты в телеграме, инстаграме, ютубе,вк, фейсбуке, ватсап, одноклассниках и других соцсетях, но нету симкарты?🧐*
Покупайте виртуальные аккаунты [здесь](https://t.me/ActVisionbot)👇🔥

Лучший бот по приёму СМС - @ActVisionbot

У нас самые низкие цены ✅
Более 20 популярных сервисов 🛍️
Пополнение через QIWI и Юмани  🏦

[Переходи](https://t.me/ActVisionbot) *и убедись, что мы лучшие!*""", parse_mode='Markdown')
                except:
                    pass
                add_photo.close()


    @dp.message_handler(commands=['start'])
    async def starter(message):
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute(f"SELECT id FROM id_n_dif_n_wins WHERE id = {message.chat.id}")
        data = cursor.fetchone()
        if data is None:
            cursor.execute("INSERT INTO id_n_dif_n_wins VALUES(?, ?, ?);", [message.chat.id, 2, 0])
        connect.commit()
        connect.close()

        markup = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("✏️ Начать игру", callback_data='NewGame'))
        await message.answer("Начать новую игру - /game\n\n"
                             "Все буквы латиницей!\n\n"
                             "Ввести изменение - *G4 8*\n"
                             "*G* - столбик, *4* - рядочек, *8* - цифра\n\n"
                             "Удалить цифру - *G4 0*\n\n"
                             "Поменять сложность - /change\_level\n"
                             "Посмотреть решение - /answer\n"
                             "Очистить поле - /clear\n"
                             "Правила судоку - /rules\n\n"
                             "*📩Купить виртуальный аккаунт -* @ActVisionbot\n"
                             "*🤖Накрутка бот🤖* - @likeasubscriberboss\_bot",
                             parse_mode='Markdown', reply_markup=markup)


    @dp.message_handler(commands=['rules'])
    async def helper(message):
        await message.answer("От игрока требуется заполнить свободные клетки цифрами от 1 до 9 так, чтобы в каждой "
                             "строке, в каждом столбце и в каждом из 9 квадратов 3×3 все цифры встречалась бы "
                             "единожды.")


    @dp.message_handler(commands=['change_level'])
    async def level_changer(message):
        level_1 = InlineKeyboardButton("1", callback_data='Level_1')
        level_2 = InlineKeyboardButton("2", callback_data='Level_2')
        level_3 = InlineKeyboardButton("3", callback_data='Level_3')
        level_4 = InlineKeyboardButton("4", callback_data='Level_4')
        level_5 = InlineKeyboardButton("5", callback_data='Level_5')
        markup = InlineKeyboardMarkup(row_width=5).add(level_1, level_2, level_3, level_4, level_5)
        await message.answer("Выбери уровень сложности", reply_markup=markup)


    @dp.callback_query_handler(lambda c: "Level" in c.data)
    async def callback_new_game(call):
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute("UPDATE id_n_dif_n_wins SET dif == ? WHERE id == ?;", (int(call.data[-1]) - 1,
                                                                              call.message.chat.id))
        connect.commit()
        connect.close()
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            reply_markup=None)
        markup = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("✏️ Начать игру", callback_data='NewGame'))

        await call.message.answer('Уровень изменен ✅', reply_markup=markup)


    @dp.message_handler(commands=['game'])
    async def started_field(message):
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute(f"SELECT id FROM users_info WHERE id = {message.chat.id}")
        data = cursor.fetchone()
        connect.commit()
        if data is None:
            cursor.execute(f"SELECT dif FROM id_n_dif_n_wins WHERE id = {message.chat.id}")

            dif_lev = cursor.fetchone()[0]
            sudoku = generator_sudoku(difficulty_level=(15 + dif_lev * 10))

            sudoku_drawer(sudoku, sudoku)

            with open(config.TABLE, 'rb') as file:
                msg = await bot.send_photo(message.chat.id, file)

            user_info = (message.chat.id, str(sudoku), str(sudoku), msg.message_id)
            cursor.execute("INSERT INTO users_info VALUES(?, ?, ?, ?);", user_info)
            connect.commit()
        else:
            item1 = InlineKeyboardButton("да", callback_data='game_True')
            item2 = InlineKeyboardButton("нет", callback_data='game_False')
            markup = InlineKeyboardMarkup(row_width=2).add(item1, item2)
            await message.answer("хочешь начать заново?", reply_markup=markup)
        connect.close()


    @dp.callback_query_handler(lambda c: c.data == "NewGame")
    async def callback_new_game(call):
        await started_field(call.message)
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            reply_markup=None)


    @dp.callback_query_handler(lambda c: "game" in c.data)
    async def callback_game(call):
        if call.data == 'game_True':
            connect = sqlite3.connect('users.db')
            cursor = connect.cursor()

            cursor.execute(f"SELECT dif FROM id_n_dif_n_wins WHERE id = {call.message.chat.id}")
            dif_lev = cursor.fetchone()[0]
            sudoku = generator_sudoku(difficulty_level=(15 + dif_lev * 10))

            sudoku_drawer(sudoku, sudoku)

            with open(config.TABLE, 'rb') as file:
                msg = await bot.send_photo(call.message.chat.id, file)

            cursor.execute("UPDATE users_info SET starter_sudoku == ?, user_tab == ?, last_message_id == ? "
                           "WHERE id == ?;", (str(sudoku), str(sudoku), msg.message_id, call.message.chat.id))
            connect.commit()
            connect.close()
        if call.data == 'game_False':
            await bot.send_message(call.message.chat.id, "будь осторежнее")
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            reply_markup=None)


    @dp.message_handler(commands=['answer'])
    async def answer(message):
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute(f"SELECT id FROM users_info WHERE id = {message.chat.id}")
        data = cursor.fetchone()
        connect.commit()
        connect.close()

        if data is None:
            item = InlineKeyboardButton("✏️ Начать игру", callback_data='NewGame')
            markup = InlineKeyboardMarkup(row_width=1).add(item)
            await message.answer("Ты не начал игру 😢", reply_markup=markup)
        else:
            item1 = InlineKeyboardButton("да", callback_data='answer_True')
            item2 = InlineKeyboardButton("нет", callback_data='answer_False')
            markup = InlineKeyboardMarkup(row_width=2).add(item1, item2)
            await message.answer("хочешь узнать ответ?", reply_markup=markup)


    @dp.callback_query_handler(lambda c: "answer" in c.data)
    async def callback_answer(call):
        if call.data == 'answer_True':
            connect = sqlite3.connect('users.db')
            cursor = connect.cursor()
            cursor.execute(f"SELECT starter_sudoku, last_message_id FROM users_info WHERE id = {call.message.chat.id}")
            user_info = cursor.fetchone()
            connect.commit()

            starter_tab, last_message_id = eval(user_info[0]), user_info[1]
            sudoku_drawer(sudoku_solver(starter_tab), starter_tab)
            with open(config.TABLE, 'rb') as file:
                await bot.send_photo(call.message.chat.id, file)

            cursor.execute(f"DELETE FROM users_info WHERE id = {call.message.chat.id}")
            connect.commit()
            connect.close()
        if call.data == 'answer_False':
            await bot.send_message(call.message.chat.id, "хорошо что я спросил")
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            reply_markup=None)


    @dp.message_handler(commands=['clear'])
    async def clear_field(message):
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute(f"SELECT id FROM users_info WHERE id = {message.chat.id}")
        data = cursor.fetchone()
        connect.commit()
        connect.close()

        if data is None:
            item = InlineKeyboardButton("✏️ Начать игру", callback_data='NewGame')
            markup = InlineKeyboardMarkup(row_width=1).add(item)
            await message.answer("Ты не начал игру", reply_markup=markup)
        else:
            item1 = InlineKeyboardButton("да", callback_data='clear_True')
            item2 = InlineKeyboardButton("нет", callback_data='clear_False')
            markup = InlineKeyboardMarkup(row_width=2).add(item1, item2)
            await message.answer("хочешь очистить поле?", reply_markup=markup)


    @dp.callback_query_handler(lambda c: "clear" in c.data)
    async def callback_clear(call):
        if call.data == 'clear_True':
            connect = sqlite3.connect('users.db')
            cursor = connect.cursor()
            cursor.execute(f"SELECT starter_sudoku FROM users_info WHERE id = {call.message.chat.id}")
            starter_tab = eval(cursor.fetchone()[0])
            connect.commit()

            sudoku_drawer(starter_tab, starter_tab)
            with open(config.TABLE, 'rb') as file:
                await bot.send_photo(call.message.chat.id, file)

            cursor.execute("UPDATE users_info SET user_tab == ? WHERE id == ?;", (str(starter_tab),
                                                                                  call.message.chat.id))
            connect.commit()
            connect.close()
        if call.data == 'clear_False':
            await bot.send_message(call.message.chat.id, "тогда продолжай")
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            reply_markup=None)


    @dp.message_handler(content_types=['text'])
    async def tab_change(message):
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute(f"SELECT starter_sudoku, user_tab, last_message_id FROM users_info WHERE id = {message.chat.id}")
        user_info = cursor.fetchone()
        connect.commit()
        if user_info is not None:
            starter_tab, sudoku, last_message_id = eval(user_info[0]), eval(user_info[1]), user_info[2]
            text = message.text
            if (len(text) == 4) and (text[0] in ascii_letters) and text[1].isdigit() and (text[2] == ' ') \
                    and text[3].isdigit():
                column = ord(text[0].lower()) - 97
                row = int(text[1]) - 1
                num = int(text[3])
                if starter_tab[row][column] != 0:
                    item1 = InlineKeyboardButton('да', callback_data='deception_True')
                    item2 = InlineKeyboardButton("нет", callback_data='deception_False')
                    markup = InlineKeyboardMarkup(row_width=2).add(item1, item2)
                    await message.answer("хочешь меня надурить?", reply_markup=markup)
                else:
                    sudoku[row][column] = num
                    sudoku_drawer(sudoku, starter_tab)
                    with open(config.TABLE, 'rb') as file:
                        msg = await bot.send_photo(message.chat.id, file)
                    try:
                        await bot.delete_message(message.chat.id, last_message_id)
                    except MessageCantBeDeleted:
                        pass
                    cursor.execute("UPDATE users_info SET user_tab == ?, last_message_id == ? WHERE id == ?",
                                   (str(sudoku), msg.message_id, message.chat.id))
                    connect.commit()
                    if sudoku == sudoku_solver(starter_tab):
                        cursor.execute(f"SELECT dif, wins FROM id_n_dif_n_wins WHERE id = {message.chat.id}")
                        dif, wins = cursor.fetchone()
                        cursor.execute("UPDATE id_n_dif_n_wins SET wins == ? WHERE id == ?;",
                                       (wins + dif + 1, message.chat.id))

                        markup = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("✏️ Начать новую игру",
                                                                                            callback_data='NewGame'))
                        await message.answer('*Победа!*', reply_markup=markup, parse_mode='Markdown')
                        cursor.execute(f"DELETE FROM users_info WHERE id = {message.chat.id}")
                        connect.commit()
            connect.close()


    @dp.callback_query_handler(lambda c: "deception" in c.data)
    async def callback_deception(call):
        if call.data == 'deception_True':
            await bot.send_message(call.message.chat.id, "у тебя ничего не выйдет")
        if call.data == 'deception_False':
            await bot.send_message(call.message.chat.id, "случайность, со всеми бывает")
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            reply_markup=None)


    async def set_commands(dp):
        await bot.set_my_commands([types.BotCommand("/start", "начать"), types.BotCommand("/game", "новая игра"),
                                   types.BotCommand("/change_level", "поменять сложность"),
                                   types.BotCommand("/clear", "очистить поле"), types.BotCommand("/answer", "решение"),
                                   types.BotCommand("/rules", "правила")])
except Exception as ex:
    print(ex)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=set_commands)
