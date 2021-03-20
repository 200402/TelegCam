
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

import keyboard
import telebot 
import database
import get_frame_from_camera
import time
from config import token

bot = telebot.TeleBot(token)
database.create_table()
database.get_information_about_cameras()
database.create_txt()

@bot.message_handler(commands = ['start'])
def statring(message):
    database.new_user(message.chat.id)
      
     
    bot.send_message(message.chat.id, "Первым делом рекомендуется выбрать предпочитаемую камеру", reply_markup = keyboard.add_keyboard('button_standart')) # додумать


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message): 
    if database.new_user(message.chat.id):
        bot.send_message(message.chat.id, "Первым делом рекомендуется выбрать предпочитаемую камеру", reply_markup = keyboard.add_keyboard('button_standart'))

    if message.text == 'Назад':
        database.change_status_user(message.chat.id, "calmness")
        text = "возвращение в меню"
        bot.send_message(message.chat.id, text, reply_markup = keyboard.add_keyboard("button_standart"))

    elif message.text == 'Получить информацию с камер': 
        list = database.get_camera_url(message.chat.id)
        database.change_status_user(message.chat.id, "calmness")
        if list == "Вы не подписаны ни на одну камеру":
            text = 'Вы не подписаны ни на одну камеру'
            bot.send_message(message.chat.id, text, reply_markup = keyboard.add_keyboard("button_standart"))
        else:
            bot.send_message(message.chat.id, "Начало отправки")
            for url_list in database.get_camera_url(message.chat.id):
                time.sleep(0.1)
                if get_frame_from_camera.get_frame(url_list[1]) == "successfully":
                    bot.send_photo(message.chat.id, open('image1.jpg', 'rb'), caption=f'Код камеры: {url_list[0]}, адрес: {url_list[2]}')
                else:
                    database.get_information_about_cameras()
                    database.create_txt()
                    if get_frame_from_camera.get_frame(url_list[1]) == "successfully":
                        bot.send_message(message.chat.id, f"{url_list[2]}")
                        bot.send_photo(message.chat.id, open('image1.jpg', 'rb'))
                    else:
                        bot.send_message(message.chat.id, "В данный момент у бота нет доступа к данной камере, приносим извенения за неудобства")
            text = 'Конец отправки'
            bot.send_message(message.chat.id, text, reply_markup = keyboard.add_keyboard("button_standart"))

    elif message.text == 'Получить список камер':
        database.change_status_user(message.chat.id, "list")
        addition = ["Список всех камер","Найти камеру по части адреса"]
        text = f"Список всех камер - бот отправит txt файлик содержащий код и адрес всех камер подключенных к боту\nНайти камеру по части адреса - поиск камеры, адрес которой содержит веденное слово\n\nСписок всех камер на карте города можно посмотреть на сайте http://maps.ufanet.ru/ufa"
        bot.send_message(message.chat.id, text, reply_markup = keyboard.add_keyboard('button_back_with_the_addition', addition))
    


    elif message.text == 'Подписаться на камеру':
        database.change_status_user(message.chat.id, "subscribe")
        bot.send_message(message.chat.id, "Пожалуйста введите код камеры на которую хотите подписаться", reply_markup = keyboard.add_keyboard("button_back"))
    
    
    elif message.text == 'Отписаться от камеры':
        addition = database.subscription_list_with_address(message.chat.id)
        if addition == 'Вы не подписаны ни на одну камеру':
            bot.send_message(message.chat.id, addition)
        else:
            database.change_status_user(message.chat.id, "unsubscribe")
            text = f"Пожалуйста введите код камеры от которой хотите отписаться или выберите ее в списке на клавиатуре"
            bot.send_message(message.chat.id, text, reply_markup = keyboard.add_keyboard('button_back_with_the_addition', addition))


    elif message.text == 'Отправить жалобу':
        addition = database.subscription_list_with_address(message.chat.id)
        if addition == 'Вы не подписаны ни на одну камеру':
            bot.send_message(message.chat.id, addition)
        else:
            database.change_status_user(message.chat.id, "report")
            text = f"Пожалуйста введите код камеры на которую хотите пожаловаться или выберите ее в списке на клавиатуре"
            bot.send_message(message.chat.id, text, reply_markup = keyboard.add_keyboard('button_back_with_the_addition', addition))


    elif message.text == 'Список всех камер':
        database.create_txt()
        text = f"расположение всех камер на карте можно по ссылке http://maps.ufanet.ru/ufa"
        bot.send_message(message.chat.id, text)
        file = open("text.txt","rb")
        bot.send_document(message.chat.id, file, reply_markup = keyboard.add_keyboard('button_standart'))


    elif message.text == 'Найти камеру по части адреса':
        database.change_status_user(message.chat.id, "camera_id_by_address")
        text = "Пожалуйста введите адрес или часть адреса камеры (расположение всех камер на карте можно по ссылке http://maps.ufanet.ru/ufa)"
        bot.send_message(message.chat.id, text, reply_markup = keyboard.add_keyboard("button_back"))


    else:
        if database.get_status_user(message.chat.id) == "camera_id_by_address":
            number = database.number_of_camera_adress_exists(message.text)
            if number < 1:
                text = "Не было найдено ни одной камеры с таким адресом (расположение всех камер на карте можно по ссылке http://maps.ufanet.ru/ufa)"
                bot.send_message(message.chat.id, text)
            elif number > 10:
                text = "Извините, но было найдено слишком много камер с таким адресом, пожалуйста уточните адрес (расположение всех камер на карте можно по ссылке http://maps.ufanet.ru/ufa)"
                bot.send_message(message.chat.id, text)
            else:
                bot.send_message(message.chat.id, f"{database.camera_adress_exists(message.text)}")
        
        elif database.get_status_user(message.chat.id) == "subscribe":
            message_text = message.text
            if len(message_text) < 3:
                message_text = '0' + message_text 
                if len(message_text) < 3:
                    message_text = '0' + message_text
            if database.camera_id_exists(message_text):
                database.subscription(message.chat.id, message_text)
                text = f"Вы успешно подписались на камеру с кодом {message_text}"
                bot.send_message(message.chat.id, text)
            else:
                text = "Извините, но камеры с таким номером не существует"
                bot.send_message(message.chat.id, text)

        elif database.get_status_user(message.chat.id) == "report":
            message_text = message.text
            if len(message_text) < 3:
                message_text = '0' + message_text 
                if len(message_text) < 3:
                    message_text = '0' + message_text
            if not len(message_text) == 3:
                message_text = message_text[5] + message_text[6] + message_text[7]
            if database.subscription_on_this_camera(message.chat.id, message_text):
                text = f"Спасибо за ваш фидбэк"
                bot.send_message(message.chat.id, text, reply_markup = keyboard.add_keyboard('button_standart'))
                database.change_status_user(message.chat.id, "report_info")
                bot.send_message(454054254, f"Пользователь номер {message.chat.id}   жалуется на камеру {message_text}")
            else:
                text = "Вы не подписаны на данную камеру"


        elif database.get_status_user(message.chat.id) == "unsubscribe":
            message_text = message.text
            if len(message_text) < 3:
                message_text = '0' + message_text 
                if len(message_text) < 3:
                    message_text = '0' + message_text
            if not len(message_text) == 3:
                message_text = message_text[5] + message_text[6] + message_text[7]
            if database.camera_id_exists(message_text):
                text = ''
                if database.subscription_on_this_camera(message.chat.id, message_text):
                    if len(message_text) == 3:
                        database.unsubscription(message.chat.id, message_text)
                    else:
                        database.unsubscription(message.chat.id, message_text[5] + message_text[6] + message_text[7])
                    text = f"Вы успешно отписались от камеры с кодом {message_text}"
                    addition = database.subscription_list_with_address(message.chat.id)
                    if not addition == 'Вы не подписаны ни на одну камеру':
                        bot.send_message(message.chat.id, text, reply_markup = keyboard.add_keyboard('button_back_with_the_addition', addition))
                    else:
                        bot.send_message(message.chat.id, text, reply_markup = keyboard.add_keyboard('button_back'))
                else:
                    text = "Вы не были подписаны на данную камеру"
                    bot.send_message(message.chat.id, text)
            else:
                text = "Извините, но камеры с таким номером не существует"
                bot.send_message(message.chat.id, text)
        else: 
            bot.send_message(message.chat.id, "Извините, я не знаю данную команду")
# это должно быть в конце
bot.polling(none_stop=True)