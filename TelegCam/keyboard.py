#   This file is part of TelegCam.
#
#    TelegCam is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    TelegCam is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with TelegCam.  If not, see <https://www.gnu.org/licenses/>.

from telebot import types

def add_keyboard(type_information, addition=""):
    markup = types.ReplyKeyboardMarkup(True)
    if type_information == 'button_standart':
        markup = __button_standart();

    elif type_information == 'button_back':
        markup = __button_back()

    elif type_information == 'button_back_with_the_addition':
        markup = __button_back_with_the_addition(addition)
    return markup


def __button_standart():
    markup = types.ReplyKeyboardMarkup(True)
    markup.row(types.KeyboardButton("Получить информацию с камер"))
    markup.row(types.KeyboardButton("Получить список камер"))
    markup.row(types.KeyboardButton("Подписаться на камеру"))
    markup.row(types.KeyboardButton("Отписаться от камеры"))
    markup.row(types.KeyboardButton("Отправить жалобу"))
    return markup


def __button_back():
    markup = types.ReplyKeyboardMarkup(True)
    markup.row(types.KeyboardButton("Назад"))
    return markup


def __button_back_with_the_addition(addition):
    markup = types.ReplyKeyboardMarkup(True)
    for value in addition:
        markup.row(types.KeyboardButton(value))
    markup.row(types.KeyboardButton("Назад"))
    return markup