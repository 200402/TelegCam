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

import sqlite3
import requests
import bs4
import time


# создание всех таблиц
def create_table():
    with sqlite3.connect("mydatabase.db") as db:
        sql = db.cursor()
        sql.execute("""CREATE TABLE IF NOT EXISTS users (
                    id TEXT, 
                    cahnged TEXT)""")
    
        sql.execute("""CREATE TABLE IF NOT EXISTS cameras (
                    id TEXT, 
                    url TEXT, 
                    address TEXT)""")

        sql.execute("""CREATE TABLE IF NOT EXISTS users_cameras (
                    users_id TEXT NOT NULL,
                    cameras_id TEXT NOT NULL,
                    FOREIGN KEY (users_id) REFERENCES users(id)
                    FOREIGN KEY (cameras_id) REFERENCES cameras(id)
                    )""") 

        sql.execute("""CREATE TABLE IF NOT EXISTS crutch_antispam (
                    number_of_corrected_messages INTEGER DEFAULT 0
                    )""") 

        sql.execute(f"INSERT INTO crutch_antispam VALUES (?)", (0,))
        


# получить информацию о всех камерах
def get_information_about_cameras():
    with sqlite3.connect("mydatabase.db") as db:
        sql = db.cursor()
        url = 'http://maps.ufanet.ru/ufa'
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
                'Accept-Language': 'ru,en-US;q=0.9,en;q=0.8,ru-RU;q=0.7'
                }
        html_text = requests.get(url, headers=header) 
        sql.execute("""DELETE FROM cameras""")
        info = ["","","","", 0]
        for row in html_text.text.split('\n'):
            if not("e = ''" in row):
                if "marker.name" in row:
                    info[0] = row.strip(" ';").replace("marker.name = '", '')

                elif "marker.server" in row:
                    info[1] = row.strip(" ';").replace("marker.server = '", '')

                elif "marker.number" in row:
                    info[2] = row.strip(" ';").replace("marker.number = '", '')

                elif "marker.token" in row:
                    info[3] = row.strip(" ';").replace("marker.token = '", '')
                    info[4] += 1
                    if info[4] == 500:
                        if 1<10:
                            pass
                    id = str(info[4])
                    if info[4] < 10:
                        id = '0' + id
                    if info[4] < 100:
                        id = '0' + id
                    sql.execute(f"INSERT INTO cameras VALUES (?,?,?)", (id, 'http://' + info[1]+'/'+info[2]+'/preview.mp4?token='+info[3]+'&mute=true', info[0]))
                    info = ["","","","", info[4]]
            else:
                break


# получить ссылку на камеру
def get_camera_url(user_id):
    with sqlite3.connect("mydatabase.db") as db:
        sql = db.cursor()
        sql.execute(f"SELECT * FROM users_cameras WHERE users_id = '{user_id}'")
        if sql.fetchone() is None: 
            return "Вы не подписаны ни на одну камеру"
        else:
            ret_value = []
            for value in sql.execute(f"SELECT * FROM cameras INNER JOIN users_cameras ON cameras.id = users_cameras.cameras_id WHERE users_cameras.users_id = '{user_id}';"):
                ret_value.append(value)
            return ret_value



# получить адрес
def get_camera_info(user_id):
    with sqlite3.connect("mydatabase.db") as db:
        sql = db.cursor()
        for value in sql.execute(f"SELECT * FROM cameras WHERE id = '{checking_id_selected_camera(user_id)}'"):
            return f"Код: {value[0]}\nАдрес{value[1]}"


# получить ссылку на по id
def get_camera_url_using_id(camera_id):
    with sqlite3.connect("mydatabase.db") as db:
        sql = db.cursor()
        for value in sql.execute(f"SELECT url FROM cameras WHERE id = '{camera_id}'"):
            return value[0]


# создание юзера, если он новый
def new_user(user_id):
    with sqlite3.connect("mydatabase.db") as db:
        sql = db.cursor()
        sql.execute(f"SELECT id FROM users WHERE id = '{user_id}'")
        if sql.fetchone() is None:
            sql.execute(f"INSERT INTO users VALUES (?,?)", (user_id, "calmness"))
            return True
        else:
            return False


# изменение текущего действия пользователя
def change_status_user(user_id, state):
    with sqlite3.connect("mydatabase.db") as db:
        sql = db.cursor()
        sql.execute(f"UPDATE users SET cahnged = '{state}' WHERE id = '{user_id}'")


# что собирается делать юзер 
def get_status_user(user_id):
    with sqlite3.connect("mydatabase.db") as db:
        sql = db.cursor()
        for value in sql.execute(f"SELECT cahnged FROM users WHERE id = '{user_id}'"):
            return value[0]


# существует ли камера с введенным кодом
def camera_id_exists(camera_id):
    with sqlite3.connect("mydatabase.db") as db:
        sql = db.cursor()
        sql.execute(f"SELECT id FROM cameras WHERE id = '{camera_id}'")
        if sql.fetchone() is None: 
            return False
        else: 
            return True

# добавить подписка на камеру
def subscription(id_user, id_camera):
    with sqlite3.connect("mydatabase.db") as db:
        sql = db.cursor()
        sql.execute(f"SELECT * FROM cameras WHERE id = '{id_camera}'")
        if sql.fetchone() is None: 
            return "Нет камеры с таким номером" # вывести в отдельную функцию(?)
        else:
            sql.execute(f"SELECT * FROM users_cameras WHERE users_id = '{id_user}' AND cameras_id = '{id_camera}'")
            if sql.fetchone() is None:
                sql.execute(f"INSERT INTO users_cameras VALUES (?,?)", (id_user, id_camera,))
                return f"Вы успешно подписались на камеру с номером {id_camera}"
            else:
                return f"Вы уже подписаны на камеру с номером {id_camera}"


# убрать подписку на камеру
def unsubscription(id_user, id_camera):
    with sqlite3.connect("mydatabase.db") as db:
        sql = db.cursor()
        sql.execute(f"DELETE FROM users_cameras WHERE users_id = '{id_user}' AND cameras_id = '{id_camera}'")


# список камер на которые подписан пользователь
def subscription_list_with_address(id_user):
    with sqlite3.connect("mydatabase.db") as db:
        sql = db.cursor()
        sql.execute(f"SELECT * FROM users_cameras WHERE users_id = '{id_user}'")
        if sql.fetchone() is None: 
            return "Вы не подписаны ни на одну камеру"
        else:
            ret_value = []
            for value in sql.execute(f"SELECT * FROM cameras INNER JOIN users_cameras ON cameras.id = users_cameras.cameras_id;"):
                ret_value.append(f"\nКод: {value[0]}\nАдрес: {value[2]}")
                print(f"\nКод: {value[0]}\nАдрес: {value[2]}")
            return ret_value


# подписан ли пользователь с на камеру с такой то айди
def subscription_on_this_camera(id_user, camera_id):
    with sqlite3.connect("mydatabase.db") as db:
        sql = db.cursor()
        sql.execute(f"SELECT * FROM cameras INNER JOIN users_cameras ON cameras.id = users_cameras.cameras_id WHERE users_cameras.cameras_id = '{camera_id}'")
        if sql.fetchone() is None: 
            return False
        else: 
            return True
        

# сколько существует камер с введенным адресом
def number_of_camera_adress_exists(address_input):
    with sqlite3.connect("mydatabase.db") as db:
        sql = db.cursor() 
        db.create_function("mylower", 1, lower_string)
        for value in sql.execute(f"SELECT COUNT(*) FROM cameras WHERE mylower(address) LIKE '%{address_input.lower()}%'"):
            return value[0]


# список камер с введенным адресом
def camera_adress_exists(address_input):
    with sqlite3.connect("mydatabase.db") as db:
        sql = db.cursor() 
        ret_value = ""
        db.create_function("mylower", 1, lower_string)
        for value in sql.execute(f"SELECT * FROM cameras WHERE mylower(address) LIKE '%{address_input.lower()}%'"):
            ret_value += f"\n\nкод камеры: {value[0]};     адрес: {value[2]}" 
        return ret_value


# подписаться на камеру
def subscribe_to_camera(message_text, user_id):
    with sqlite3.connect("mydatabase.db") as db:
        sql.execute(f"SELECT * FROM users_cameras WHERE users_id = '{id_user}' AND cameras_id = '{id_camera}'")
        if sql.fetchone() is None:
            sql.execute(f"INSERT INTO users_cameras VALUES (?,?)", (id_user, id_camera,))
            return f"Вы успешно подписались на камеру с номером {id_camera}"
        else:
            return f"Вы уже подписаны на камеру с номером {id_camera}"



# айди выбранной камеры
def checking_id_selected_camera(message_chat_id):
    with sqlite3.connect("mydatabase.db") as db:
        sql = db.cursor()
        for value in sql.execute(f"SELECT camera_id FROM users WHERE id = '{message_chat_id}'"):
            return value[0]


# список камер по адресу
def get_list_camera(substring = ''):
    with sqlite3.connect("mydatabase.db") as db:
        list = "Список камер: "
        sql = db.cursor() 
        return sql.execute(f"SELECT (*) FROM cameras WHERE INSTR(address, '{substring}') > 0;")


# список камер
def create_txt(): 
    with sqlite3.connect("mydatabase.db") as db:
        string = f"Расположение Всех камер на карте можно посмотреть на сайте http://maps.ufanet.ru/ufa#\n\nСписок камер: "
        sql = db.cursor() 
        f = open('text.txt', 'w')
        for value in sql.execute(f"SELECT * FROM cameras"):
            string += f"\n\nкод камеры: {value[0]};   адрес: {value[2]}"
        f.write(string)
        f.close()


# инфа о камере по id
def get_camerasrmation(camera_id):
    with sqlite3.connect("mydatabase.db") as db:
        sql = db.cursor()
        for value in sql.execute(f"SELECT * FROM cameras WHERE id = '{camera_id}'"):
            return value


def lower_string(stri):
    return stri.lower()


# антиспамер; 
# можно ли отправить еще сообщение 
def is_it_possible_to_send_another_message_to_the_user():
    with sqlite3.connect("mydatabase.db") as db:
        sql = db.cursor()
        for value in sql.execute(f"SELECT * FROM crutch_antispam"):
            print(value[0])
            if value[0] >=15:
                return False
            else:
                return True
        
# изменение количества отправленных  сообщений
def change_the_number_of_sent_messages(act = ""):
    with sqlite3.connect("mydatabase.db") as db:
        sql = db.cursor()
        if act == "add":
            sql.execute(f"UPDATE crutch_antispam SET number_of_corrected_messages = number_of_corrected_messages + 1")
        else:
            sql.execute(f"UPDATE crutch_antispam SET number_of_corrected_messages = 0")

def antispam():
    with sqlite3.connect("mydatabase.db") as db:
        sql = db.cursor()
        for value in sql.execute(f"SELECT number_of_corrected_messages FROM crutch_antispam"):
            if value[0] >10:
                time.sleep(1)
                change_the_number_of_sent_messages()





#def test():
#    with sqlite3.connect("mydatabase.db") as db:
#        sql = db.cursor()
#        for value in sql.execute(f"SELECT * FROM cameras WHERE id = '500'"):
#            print(value)