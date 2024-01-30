import telebot
import st
import sqlite3
import os
import random
import glob
from PIL import Image
from telebot import types  # для указание типов
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
bot = telebot.TeleBot('5103423151:AAFZ7o8Wd4O_LiDnTVpgWBYQgDxVqi11xDs')

#############################################################################

num_of_tables = 16
num_of_games = 1

# -------------------------ТО ЧТО КАСАЕТСЯ БАЗЫ ДАННЫХ--------------------------------------
conn = sqlite3.connect('tablebot2.db', check_same_thread=False)
cursor = conn.cursor()


def full_table_db(number: int, status: str, id: int):  # дополнение таблицы столов новым столов
    cursor.execute('INSERT INTO tables (num_of_table, status_of_table, id_of_game) VALUES (?, ?, ?, ?)',
                   (number, status, id))
    conn.commit()


def full_games_db(game: str, status: str):  # дополнение таблицы игр новой игрой
    cursor.execute('INSERT INTO games (num_of_game, game, status_of_game) VALUES (?, ?, ?)',
                   ((num_of_games + 1), game, status))
    conn.commit()


def update_num_games():  # обновление нумерации игр (полезно при удалении)
    cursor.execute("SELECT num_of_game FROM games")
    gamesdb = cursor.fetchall()
    global num_of_games
    i = 1
    for g in gamesdb:
        cursor.execute("Update games set num_of_game = ? where num_of_game = ?", (i, g[0]))
        i += 1
        conn.commit()
    num_of_games = i - 1


update_num_games()
print(num_of_games)


def nomoder(id): #пользователь не модер
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    for u in users:
        if u[0] == id and not u[2]:
            return True
    return False


# ретёрны всякие а ля ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ

def gamexist(game):  # существует ли игра с таким названием или номером в базе данных
    cursor.execute("SELECT * FROM games")
    gamesdb = cursor.fetchall()
    exist = False
    for gam in gamesdb:
        if gam[1] == game:
            exist = True
    return exist


def tableisfree(i):  # свободен ли стол под этим номером
    cursor.execute("SELECT * FROM tables")
    tabledb = cursor.fetchall()
    for tab in tabledb:
        if (tab[0] == i and tab[1] == st.yes_db):
            return True
    return False


def gameisfree(id):  # свободна ли игра с этим номером
    cursor.execute("SELECT * FROM games")
    gamesdb = cursor.fetchall()
    freedom = False
    for gam in gamesdb:
        if (gam[0] == id and gam[2] == st.yes_db):
            freedom = True
    return freedom


def gameiswait(i):
    cursor.execute("SELECT * FROM games")
    gamesdb = cursor.fetchall()
    for g in gamesdb:
        if (g[2] == st.wait_db and g[0] == i):
            return True
    return False


def tableiswait(i):
    cursor.execute("SELECT * FROM tables")
    tabledb = cursor.fetchall()
    for t in tabledb:
        if (t[1] == st.wait_db and t[0] == i):
            return True
    return False


def create_markup(n):  # создать клавиатуру с определённым количеством кнопок, пронумерованных от 1
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    b = [types.KeyboardButton('0')]
    for i in range(n):
        b.append(types.KeyboardButton(str(i + 1)))
    b.pop(0)
    markup.add(*b)
    return markup


def whatgameidattable(n):  # какая игра находится за столом
    cursor.execute("SELECT * FROM tables")
    tablesdb = cursor.fetchall()
    for t in tablesdb:
        if t[0] == n:
            return t[2]


def gameisontable(id):  # за каким столом игра
    cursor.execute("SELECT * FROM tables")
    tablesdb = cursor.fetchall()
    for t in tablesdb:
        if t[2] == id:
            return t[0]
    return 0


def findidgame(id):  # какая игра под этим номером
    cursor.execute("SELECT num_of_game, game FROM games")
    gamesdb = cursor.fetchall()
    for g in gamesdb:
        if g[0] == id:
            return g[1]
    return st.empty


def findgameid(game):  # какой номер у этой игры (да, тупые названия, знаю)
    cursor.execute("SELECT num_of_game, game FROM games")
    gamesdb = cursor.fetchall()
    for g in gamesdb:
        if g[1] == game:
            return g[0]
    return 0


def isnewuser(id):  # существует ли пользователь в базе данных
    cursor.execute("SELECT id FROM users")
    ids = cursor.fetchall()
    for i in ids:
        if i[0] == id:
            return False
    return True


# -------------------------СТАРТОВОЕ ПРИВЕТСТВИЕ--------------------

@bot.message_handler(commands=['start'])
def start(message):
    id = message.from_user.id
    if isnewuser(id):
        print("Ты зачем сюда полез блин")
        bot.send_message(message.chat.id, st.begin)
        maysend(message, id)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        button1 = types.KeyboardButton('1️⃣')
        button2 = types.KeyboardButton('2️⃣')
        button3 = types.KeyboardButton('3️⃣')
        button4 = types.KeyboardButton('4️⃣')
        button5 = types.KeyboardButton('Меню')

        markup.add(button1, button2, button3, button4, button5)

        bot.send_message(message.chat.id, text=st.start.format(message.from_user), reply_markup=markup)


def sending(text):
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    for us in users:
        if us[1]:
            bot.send_message(us[0], text)


def sendall(text):
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    for us in users:
        bot.send_message(us[0], text)


def maysend(message, id):
    bot.send_message(message.chat.id, st.topush + st.choise, reply_markup=create_markup(2))
    bot.register_next_step_handler(message, tosend, id)
    print("Вызываю выбирающую")


def tosend(message, id):
    if message.text == '1':
        bot.send_message(message.chat.id, "Замечательно! Жди моих уведомлений!")
        makesend(id)
        start(message)
    elif message.text == '2':
        bot.send_message(message.chat.id, "Хорошо, не буду навязываться)")
        nomakesend(id)
        start(message)
    else:
        bot.send_message(message.from_user.id, st.error + "\nМожешь попровобать ещё раз выбрав нужный пункт в меню")
        start(message)


def makesend(id):
    if isnewuser(id):
        cursor.execute('INSERT INTO users (id, to_send) VALUES (?, ?)', (id, True))
        conn.commit()
    else:
        cursor.execute('Update  users set to_send = True where id = ?', (id,))
        conn.commit()


def nomakesend(id):
    if isnewuser(id):
        cursor.execute('INSERT INTO users (id, to_send) VALUES (?, ?)', (id, False))
        conn.commit()
    else:
        cursor.execute('Update users set to_send = False where id = ?', (id,))
        conn.commit()


# ------------------РЕЖИМ МОДЕРАТОРА-----------------------
@bot.message_handler(commands=['mod'])
def mod(message):
    if nomoder(message.from_user.id):
        bot.send_message(message.from_user.id, st.impostor)
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    b = [types.KeyboardButton('/0')]
    for i in range(8):
        b.append(types.KeyboardButton('/' + str(i + 1)))
    b.pop(0)
    b.append(types.KeyboardButton('/mod'))
    b.append(types.KeyboardButton('А как мне этим пользоваться?'))
    markup.add(*b)
    bot.send_message(message.chat.id, text=st.mod.format(message.from_user), reply_markup=markup)


# ----------------------ДОБАВЛЕНИЕ НОВОЙ ИГРЫ-----------------------
@bot.message_handler(commands=['1'])
def m1(message):  # стартовая функция добавления новой игры
    if nomoder(message.from_user.id):
        bot.send_message(message.from_user.id, st.impostor)
        return
    bot.send_message(message.from_user.id, "Введите название игры, которую желаете добавить",
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, putingame)  # переход к функции куда вводим название


def putingame(message):  # функция получающая названия и вызывающая добавление
    game = message.text
    addgame(message, game)  # вызов функции фактического добавления
    bot.send_message(message.from_user.id, st.goodchange)
    mod(message)


def addgame(message, game):  # функция которая добавляет игру
    full_games_db(game, st.yes_db)
    update_num_games()


# --------------------СОЕДИНИТЕЛЬНЫЕ ФУНКЦИИ---------------------
def addnotfoundgame(message, game):  # если игра была не найдена тут принимается выбор, добавлять ли её
    if message.text == "1":
        addgame(message, game)
        bot.send_message(message.from_user.id, st.goodchange)
        mod(message)
    elif message.text == "2":
        mod(message)
    else:
        bot.send_message(message.from_user.id, st.error)
        mod(message)


def addnotfoundgame_t(message, i, game):  # тоже самое, только в случае, если мы работаем со столами
    if message.text == "1":
        addgame(message, game)
        bot.send_message(message.from_user.id, "Вы ждёте игроков или уже начинаете играть?" + st.waiting,
                         reply_markup=create_markup(2))
        bot.register_next_step_handler(message, towait, i, findgameid(game))
    elif message.text == "2":
        mod(message)
    else:
        bot.send_message(message.from_user.id, st.error)
        mod(message)


# --------------------------------ЗАНЯТЬ СТОЛ-------------------------
@bot.message_handler(commands=['2'])
def m2(message):  # стартовая функция занятия стола
    if nomoder(message.from_user.id):
        bot.send_message(message.from_user.id, st.impostor)
        return
    bot.send_message(message.from_user.id, text="За каким вы столом?", reply_markup=create_markup(num_of_tables))
    showtables(message)
    bot.send_message(message.from_user.id, "Ваш выбор: ")
    bot.register_next_step_handler(message,
                                   tablestatus)  # переход к функции, которая знает, занят ли стол и что с этим делать


def tablestatus(message):  # распределение по действиям в зависимости от того занят ли стол
    try:
        i = int(message.text)
    except ValueError:
        bot.send_message(message.from_user.id, st.error + " Недопустимый формат ввода.")
        mod(message)
        return
    if tableisfree(i):
        bot.send_message(message.from_user.id, 'Стол свобоводен.\n')
        gameoftable(message, i)  # если стол свободен сраззу переходим к добавлению игры
        return
    elif tableiswait(i):
        bot.send_message(message.from_user.id, 'Стол ждал игроков.\n Начнем играть?' + st.choise,
                         reply_markup=create_markup(2))
        bot.register_next_step_handler(message, startgame, i)
    elif i > 0 and i <= num_of_tables:
        bot.send_message(message.from_user.id, 'Стол занят.\nЖелаете освободить?\n1. Да\n2. Нет',
                         reply_markup=create_markup(2))
        bot.register_next_step_handler(message, whattodotable, i)  # но если он занят выясняем, освободить ли его,
        # а то мало ли вы именно сесть хотели
    else:
        bot.send_message(message.from_user.id, st.error + " Стол не существует!")
        mod(message)


def startgame(message, i):
    if message.text == '1':

        cursor.execute("Update games set status_of_game = ? where num_of_game = ?", (st.no_db, whatgameidattable(i)))
        cursor.execute("Update tables set status_of_table = ? where num_of_table = ?",
                       (st.no_db, i))
        sending("🔴 Только что началась игра " + findidgame(i) + " за столом " + str(gameisontable(i)))
        mod(message)
    elif message.text == '2':
        mod(message)
    else:
        bot.send_message(message.from_user.id, st.error)
        mod(message)


def whattodotable(message, i):  # выясняем собственно говоря
    if message.text == "1":  # если не освобождаем, то вообще ничего не делаем
        id = whatgameidattable(i)
        sending("🟢Игра " + findidgame(id) + " только что освободилась за столом " + str(i))
        cursor.execute("Update games set status_of_game = ? where num_of_game = ?", (st.yes_db, id))
        cursor.execute("Update tables set status_of_table = ?, id_of_game = ? where num_of_table = ?",
                       (st.yes_db, 0, i))

        conn.commit()
        mod(message)
    elif message.text == '2':
        mod(message)
    else:
        bot.send_message(message.from_user.id, st.error)
        mod(message)


def gameoftable(message, i):  # выясняем во что будем играт на свободном столи
    bot.send_message(message.from_user.id, "Какую игру вы взяли?" + st.youcandoit,
                     reply_markup=create_markup(num_of_games))
    print("Вот я перейду в функцию с именем")
    showgames(message)
    bot.send_message(message.from_user.id, "Ваш выбор:")
    bot.register_next_step_handler(message, setgameontable, i)  # и переходим к функции которая это будет знать


def setgameontable(message, i):  # функция получает номер или название и соединяет стол с игрой узами брака
    # (опасна на случай если игра имеет в названии число)
    print("Я вошёл")
    id = 0
    if message.text.isdigit():
        id = int(message.text)
    else:
        game = message.text
    if id == 0:  # если у нас было введено имя игры
        id = findgameid(game)
        if not gamexist(game):  # но игры этой нет в базе данных
            bot.send_message(message.from_user.id, text=(st.nosuchgame + st.quesadd).format(message.from_user),
                             reply_markup=create_markup(2))
            bot.register_next_step_handler(message, addnotfoundgame_t, i, game)  # сначала добавляем игру
        else:
            bot.send_message(message.from_user.id, "Вы ждёте игроков или уже начинаете играть?" + st.waiting,
                             reply_markup=create_markup(2))
            bot.register_next_step_handler(message, towait, i, id)
    else:  # если был введен номер
        if id < 1 or id > num_of_games:  # но номер отсутсвует в бд
            bot.send_message(message.from_user.id, st.error + st.nosuchgame)
            return
        if not gameisfree(id):
            bot.send_message(message.from_user.id, st.error + " Игра уже занята!")
            mod(message)
            return
        bot.send_message(message.from_user.id,
                         text=("Вы ждёте игроков или уже начинаете играть?" + st.waiting).format(message.from_user),
                         reply_markup=create_markup(2))
        bot.register_next_step_handler(message, towait, i,
                                       id)  # если присутствует, то идём соединять со столом но по номеру


def towait(message, i, id):
    if message.text == "1":
        addgameontable_id(message, i, id, st.wait_db)
    elif message.text == '2':
        addgameontable_id(message, i, id, st.no_db)
    else:
        bot.send_message(message.from_user.id, st.error)
        mod(message)


def addgameontable_id(message, i, id, stat):  # соединение со столом по номеру
    print(i, id, stat)
    cursor.execute(f"Update tables set status_of_table = ?, id_of_game = ? where num_of_table = ?",
                   (stat, id, i))
    cursor.execute(f"Update games set status_of_game = ? where num_of_game = ?", (stat, id))
    if stat == st.wait_db:
        sending("🟡 Игра " + findidgame(id) + " скоро начнётся за столом " + str(i) + "\nЖдём игроков!")
    else:
        sending("🔴 Только что началась игра " + findidgame(id) + " за столом " + str(i) + "!")
    conn.commit()
    bot.send_message(message.from_user.id, "Стол успешно занят!")
    mod(message)


# --------------------------------ЗАНЯТЬ ИГРУ--------------------------------
@bot.message_handler(commands=['3'])
def m3(message):  # стартовая функция для занятия игры
    if nomoder(message.from_user.id):
        bot.send_message(message.from_user.id, st.impostor)
        return
    bot.send_message(message.from_user.id, "У какой игры вы собираетесь поменять статус?" + st.youcandoit,
                     reply_markup=create_markup(num_of_games))
    showgames(message)
    bot.send_message(message.from_user.id, "Ваш выбор:")
    bot.register_next_step_handler(message,
                                   changegame1)  # переходим к функции, которая будет знать какую игру мы меняем


def changegame1(message):  # долгая обработка всех возможных случаев, чтобы изменить статус игры на противоположный
    i = 0
    if message.text.isdigit():
        i = int(message.text)
    else:
        game = message.text
    if i == 0:  # если было введено название
        i = findgameid(game)
        if not gamexist(game):  # если игра не существует
            bot.send_message(message.from_user.id, text=(st.nosuchgame + st.quesadd +
                                                         "\nДобавленная игра будет не занята").format(
                message.from_user),
                             reply_markup=create_markup(2))
            bot.register_next_step_handler(message, addnotfoundgame,
                                           game)  # выясняем добавить ли игру (в незанятом состоянии)
            return


    if i > 0 and i <= num_of_games:  # проверка на корректность, далее аналогично верхней части

        num_tab = gameisontable(i)
        if gameisfree(i):
            bot.send_message(message.chat.id, "Игра была свободна. Сразу начнем играть?" + st.waiting,
                             reply_markup=create_markup(2))
            bot.register_next_step_handler(message, towaitgame, i)
        elif num_tab != 0:
            if tableiswait(num_tab):
                bot.send_message(message.chat.id, "Игра ожидала игроков за столом " + str(num_tab) +
                                 ".\nТеперь начинаем играть.")

                cursor.execute(f"Update games set status_of_game = ? where num_of_game = ?",
                               (st.no_db, i))
                cursor.execute(f"Update tables set status_of_table = ? where id_of_game = ?",
                               (st.no_db, i))
                sending("🔴 Только что началась игра " + findidgame(i) + " за столом " + str(gameisontable(i)))
                conn.commit()
                mod(message)
            else:
                bot.send_message(message.chat.id, st.error + " Игра находится за столом " +
                                 str(num_tab) + ". Осободить стол?" + st.choise, reply_markup=create_markup(2))
                bot.register_next_step_handler(message, whattodotable, num_tab)
        else:
            if gameiswait(i):
                bot.send_message(message.chat.id, "Игра ожидала игроков вне стола.\nТеперь начинаем играть.")
                sending("🔴 Только что началась игра " + findidgame(i) + " за пределами столов!")
                cursor.execute(f"Update games set status_of_game = ? where num_of_game = ?",
                               (st.no_db, i))
                conn.commit()
                mod(message)
            else:
                bot.send_message(message.chat.id, "Игра была занята. Теперь нет")
                sending("🟢 Спешу порадовать, что игра " + findidgame(i) + " только что освободилась!")
                cursor.execute(f"Update games set status_of_game = ? where num_of_game = ?",
                               (st.yes_db, i))
                conn.commit()
                mod(message)
    else:
        bot.send_message(message.from_user.id, st.error)
        mod(message)


def towaitgame(message, i):
    if message.text == '1':
        cursor.execute(f"Update games set status_of_game = ? where num_of_game = ?", (st.wait_db, i))
        sending("🟡Скоро начнется игра " + findidgame(i) + " за пределами столов!\nЖдём игроков!")
        conn.commit()
        bot.send_message(message.from_user.id, st.goodchange)
        mod(message)
    elif message.text == '2':
        cursor.execute(f"Update games set status_of_game = ? where num_of_game = ?", (st.no_db, i))
        sending("🔴Только что начали играть в " + findidgame(i) + " за пределами столов!")
        conn.commit()
        bot.send_message(message.from_user.id, st.goodchange)
        mod(message)
    else:
        bot.send_message(message.from_user.id, st.error)
        mod(message)

# --------------------------------УДАЛИТЬ ИГРУ-------------------------------
@bot.message_handler(commands=['4'])
def m4(message):  # стартовая функция по удалению игры
    if nomoder(message.from_user.id):
        bot.send_message(message.from_user.id, st.impostor)
        return
    bot.send_message(message.from_user.id, "Какую игру вы желаете удалить?"
                     + st.youcandoit,
                     reply_markup=create_markup(num_of_games))
    print(num_of_games)
    showgames(message)
    bot.send_message(message.from_user.id, "Ваш выбор:")
    bot.register_next_step_handler(message, delgame)


def delgame(message):
    i = 0
    if message.text.isdigit():
        i = int(message.text)
    else:
        game = message.text
    if i == 0:
        i = findgameid(game)
        if not gamexist(game):
            bot.send_message(message.from_user.id, st.error + " Данная игра отсутсвует в базе данных!")
            mod(message)
            return
        num_tab = gameisontable(i)
        if num_tab != 0:
            bot.send_message(message.from_user.id,
                             "Данная игра была удалена и снята со стола " + str(num_tab) + "!")
            cursor.execute("Update tables set status_of_table = ?, id_of_game = ? where num_of_table = ?",
                           (st.yes_db, 0, num_tab))
            conn.commit()
        if not gameisfree(i):
            bot.send_message(message.from_user.id,
                             "Данная игра была занята перед удалением!")
        cursor.execute("DELETE from games where num_of_game = ?", (i,))
        cursor.execute("DELETE from games where num_of_game = ?", (i,))
        update_num_games()
        conn.commit()
        bot.send_message(message.from_user.id, st.goodchange)
    elif i > 0 and i <= num_of_games:
        num_tab = gameisontable(i)
        if num_tab != 0:
            bot.send_message(message.from_user.id,
                             "Данная игра была удалена и снята со стола " + str(num_tab) + "!")
            cursor.execute("Update tables set status_of_table = ?, id_of_game = ? where num_of_table = ?",
                           (st.yes_db, 0, num_tab))
            conn.commit()
        cursor.execute("DELETE from games where num_of_game = ?", (i,))
        cursor.execute("DELETE from games where num_of_game = ?", (i,))
        update_num_games()
        conn.commit()
        bot.send_message(message.from_user.id, st.goodchange)
    else:
        bot.send_message(message.from_user.id, st.error)
    mod(message)


# --------------------------------ВЫВОДЫ И ВЫХОДЫ----------------------------------
@bot.message_handler(commands=['5'])
def m5(message):
    if nomoder(message.from_user.id):
        bot.send_message(message.from_user.id, st.impostor)
        return
    showgames(message)
    mod(message)


@bot.message_handler(commands=['6'])
def m6(message):
    if nomoder(message.from_user.id):
        bot.send_message(message.from_user.id, st.impostor)
        return
    showtables(message)
    mod(message)


@bot.message_handler(commands=['7'])
def m7(message):
    if nomoder(message.from_user.id):
        bot.send_message(message.from_user.id, st.impostor)
        return
    bot.send_message(message.from_user.id,
                     "Кому вы желаете отправить сообщение?\n1. Всем \n2. Тем, у котого разрешены уведомления",
                     reply_markup=create_markup(2))
    bot.register_next_step_handler(message, sendbyhand)


def sendbyhand(message):
    if message.text == '1':
        bot.send_message(message.from_user.id, "Что вы хотите отправить?")
        bot.register_next_step_handler(message, inputtosendall)
    if message.text == '2':
        bot.send_message(message.from_user.id, "Что вы хотите отправить?")
        bot.register_next_step_handler(message, inputtosend)


def inputtosendall(message):
    sendall(message.text)
    mod(message)

def inputtosend(message):
    sending(message.text)
    mod(message)


@bot.message_handler(commands=['8'])
def m8(message):
    if nomoder(message.from_user.id):
        bot.send_message(message.from_user.id, st.impostor)
        return
    start(message)



# ------------------ФУНКЦИИ ВЫВОДА--------------------------------

def showgames(message):
    cursor.execute("SELECT * FROM games")
    games = cursor.fetchall()
    text = "Вот список игр:\n"
    for g in games:
        if g[2] == st.yes_db:
            s = st.cy
            tab = ' '
        elif g[2] == st.no_db:
            s = st.cn
            if gameisontable(g[0]) == 0:
                tab = "\nИгра вне стола"
            else:
                tab = '\nСтол: '+str(gameisontable(g[0]))
        else:
            s = st.cw
            if gameisontable(g[0]) == 0:
                tab = "\nИгра вне стола"
            else:
                tab = '\nСтол: ' + str(gameisontable(g[0]))
        text += '\n'+str(g[0])+'. '+g[1]+" "+s+tab+'\n'
    bot.send_message(message.from_user.id, text+st.explane)

def getgames(message):
    cursor.execute("SELECT * FROM games")
    games = cursor.fetchall()
    for game in games:
        if game[2] == st.yes_db:
            stat = st.yes
            sto = "\nЖдёт быть сыгранной!"
        else:
            if game[2] == st.no_db:
                stat = st.no
            else:
                stat = st.wait
            nt = gameisontable(game[0])
            if nt == 0:
                sto = '\nИгра находится вне стола'
            else:
                sto = "\nИгра находится за столом " + st.numbers[nt]
        bot.send_message(message.from_user.id, str(game[0]) + '. ' + game[1] + " - " + stat + sto)

def showtables(message):
    cursor.execute("SELECT num_of_table, status_of_table, id_of_game FROM tables")
    tables = cursor.fetchall()
    text = "Список столов:\n"
    for t in tables:
        if t[1] == st.no_db:
            stat = st.cn
        elif t[1] == st.wait_db:
            stat = st.cw
        else:
            stat = st.cy
        text += '\n'+st.numbers[t[0]]+" стол "+stat+"\nИгра: "+str(findidgame(whatgameidattable(t[0])))+'\n'
    bot.send_message(message.from_user.id, text+st.explane)


def gettables(message):
    cursor.execute("SELECT num_of_table, status_of_table, id_of_game FROM tables")
    tables = cursor.fetchall()
    for tab in tables:
        if tab[1] == st.no_db:
            stat = st.no
        elif tab[1] == st.wait_db:
            stat = st.wait
        else:
            stat = st.yes
        bot.send_message(message.from_user.id, st.numbers[tab[0]] + " - " + stat + "\nИгра: " +
                         findidgame(tab[2]))



def toreview(message):
    if message.text == 'Отзыв':
        bot.send_message(message.from_user.id, "Напиши всё, что хочешь в своем сообщении. Ты в любой момент можешь написать "
                                               "новый отзыв - он заменит старый.", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, review)
    elif message.text == 'Позже':
        bot.send_message(message.from_user.id, "Как скажешь...")
        start(message)
    else:
        bot.send_message(message.from_user.id, "Получается, я зря кнопочки включал?(")
        start(message)


def review(message):
    cursor.execute("Update users set review = ? where id = ?", (message.text, message.from_user.id))
    conn.commit()
    bot.send_message(message.from_user.id, "Спасибо за отзыв!")
    start(message)


def foundeaster(id):
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    for u in users:
        if u[0] == id and u[4]:
            return True
    return False

def congrat(id):
    cursor.execute("Update users set easter = ? where id = ?", (True, id))
    conn.commit()
    bot.send_message(st.batid, "🤡Тебя нашли🤡")
    bot.send_message(id, "Вау! Ты разгадал мою пасхалку!) Это было сложно? Нет? В любом случае"
                                           " я очень рад за тебя! Теперь у тебя есть доступ к НЕбесконечному запасу "
                                           "картинок с Бэтменом"
                                           " всякий раз, когда ты пишешь Бэтмен. Зачем? Потому что я Бэтмен!")
    bot.send_photo(id, photo=open('C:\\Users\\maya1\\Pictures\\telebot\\good.jpg', 'rb'))




def sendrandpic(id):
    img = random.choice(glob.glob('C:\\Users\\maya1\\Pictures\\telebot\\*.jpg'))
    png = Image.open(img, 'r')
    DIR = 'C:\\Users\\maya1\\Pictures\\telebot'
    bot.send_photo(id, photo=png)








# ------------------------------------ТИПА МЭЙН--------------------------------------------
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привет":
        bot.send_message(message.from_user.id, st.hello)
    elif message.text == "1️⃣":
        showtables(message)
        start(message)
    elif message.text == "2️⃣":
        showgames(message)
        start(message)
    elif message.text == "3️⃣":
        markupyn = types.ReplyKeyboardMarkup(resize_keyboard=True)
        b = [types.KeyboardButton('Отзыв'), types.KeyboardButton('Позже')]
        markupyn.add(*b)
        bot.send_message(message.from_user.id, st.whoarewe, reply_markup=markupyn)
        bot.register_next_step_handler(message, toreview)
    elif message.text == "4️⃣":
        maysend(message, message.from_user.id)
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши Меню")
    elif message.text == "Меню":
        start(message)
    elif message.text == 'А как мне этим пользоваться?':
        if nomoder(message.from_user.id):
            bot.send_message(message.from_user.id, st.impostor)
            return
        bot.send_message(message.from_user.id, st.explainmod)
    elif message.text == 'Бэтмен':
        if foundeaster(message.from_user.id):
            sendrandpic(message.from_user.id)
        else:
            congrat(message.from_user.id)
    else:
        bot.send_message(message.from_user.id, "По любым другим вопросам обращайся к организаторам.")



conn.commit()
bot.polling(none_stop=True, interval=0)
