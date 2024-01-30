import telebot
bot = telebot.TeleBot('5103423151:AAFZ7o8Wd4O_LiDnTVpgWBYQgDxVqi11xDs')
from telebot import types  # для указание типов
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
import st
#import main
import Games

"""
@bot.message_handler(commands=['mod'])
def mod(message):
    markupmod = types.ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = types.KeyboardButton('/1')
    b2 = types.KeyboardButton('/2')
    b3 = types.KeyboardButton('/3')
    b4 = types.KeyboardButton('/4')
    b5 = types.KeyboardButton('/5')
    markupmod.add(b1, b2, b3, b4, b5)
    bot.send_message(message.chat.id, text=strings.mod.format(message.from_user), reply_markup=markupmod)
    modwork(message)

@bot.message_handler(commands=['1'or'2'or'3'or'4'])
def modwork(message):
    if message.text == '/1':
        bot.send_message(message.from_user.id, "Добавляем игру")
    elif message.text == '/2':
        bot.send_message(message.from_user.id, "Меняем статус игры")
    elif message.text == '/3':
        bot.send_message(message.from_user.id, "Удаляем игру")
    elif message.text == '/4':
        bot.send_message(message.from_user.id, "Смотрим список игр")
    elif message.text == '/5':
        start(message)
"""


def get_keyboard():
    # Генерация клавиатуры.
    buttons = []
    for item in Games.name:
        buttons.append(types.InlineKeyboardButton(text=item, callback_data=item))
    '''buttons = [
        types.InlineKeyboardButton(text="one", callback_data="one"),
        types.InlineKeyboardButton(text="two", callback_data="two"),
        types.InlineKeyboardButton(text="Подтвердить", callback_data="yes")
    ]'''
    # Благодаря row_width=2, в первом ряду будет две кнопки, а оставшаяся одна
    # уйдёт на следующую строку
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def checkgame(message):
    bot.send_message(message.chat.id, text="Список игр:", reply_markup=get_keyboard())


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    game = call.data
    status = Games.name[game]
    bot.send_message(call.message.chat.id, game+" - "+status)



"""
class tables:

    number = 0
    game = "Отсуствует"
    status = st.yes

    def gettable(self,number, game, status):
        self.number = number
        self.game = game
        self.status = status

class games:
    name = "No name"
    status = st.yes

    def getgame(self,name,status):
        self.name = name
        self.status = status"""




bot.polling(none_stop=True, interval=0)