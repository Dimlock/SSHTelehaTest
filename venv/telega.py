import socket

import telebot
from telebot import types
import re
import paramiko
import time

IP = None
login = None
port = None
password = None

bot = telebot.TeleBot('5531731640:AAFRXyEGK2kGDYFg7VZdkVU6DwM4oLgbNbo')

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("❓ Задать вопрос")
    btn2 = types.KeyboardButton("Адрес и порт компьютера")
    btn3 = types.KeyboardButton("Ввести команду для передачи:")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id,
                     text="Привет, {0.first_name}! Я тестовый бот для управлением твоим компьютером!".format(
                         message.from_user), reply_markup=markup)


@bot.message_handler(content_types=['text'])
def func(message):
    if (message.text == "❓ Задать вопрос"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Кто меня создал?")
        btn2 = types.KeyboardButton("Что я могу?")
        back = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, btn2, back)
        bot.send_message(message.chat.id, text="Задай мне вопрос", reply_markup=markup)

    elif (message.text == "Адрес и порт компьютера"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("IP адрес")
        btn2 = types.KeyboardButton("Порт")
        btn3 = types.KeyboardButton("Имя пользователя")
        btn4 = types.KeyboardButton("Пароль")
        back = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, btn2, btn3, btn4 ,back)
        bot.send_message(message.chat.id, text="Давайте заполнять поля!", reply_markup=markup)
    elif (message.text == "IP адрес"):
        bot.send_message(message.from_user.id, "Введите IP адрес:")
        bot.register_next_step_handler(message,get_ip)

    elif (message.text == "Порт"):
        bot.send_message(message.from_user.id, "Введите порт:")
        bot.register_next_step_handler(message,get_port)

    elif (message.text == "Имя пользователя"):
        bot.send_message(message.from_user.id, "Введите имя пользователя:")
        bot.register_next_step_handler(message, get_login)

    elif (message.text == "Пароль"):
        bot.send_message(message.from_user.id, "Введите пароль:")
        bot.register_next_step_handler(message, get_password)

    elif (message.text == "Кто меня создал?"):
        bot.send_message(message.chat.id, "Рощин Никита Владиславович :)")

    elif message.text == "Что я могу?":
        bot.send_message(message.chat.id, text="Управлять Вашим компьютером :)")

    elif message.text == "Ввести команду для передачи на удалённый сервер":
        bot.send_message(message.from_user.id, "Введите команду для удалённого доступа")
        bot.register_next_step_handler(message, command)

    elif (message.text == "Вернуться в главное меню"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("❓ Задать вопрос")
        btn2 = types.KeyboardButton("Адрес и порт компьютера")
        btn3 = types.KeyboardButton("Ввести команду для передачи на удалённый сервер")
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, text="Вы вернулись в главное меню", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, text="На такую комманду я не запрограммировал..")

def get_ip(message):
    global IP
    IP = str(message.text)
    pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    lst = []
    try:
        lst.append(pattern.search(IP)[0])
        bot.send_message(message.from_user.id, "IP адрес введён верно!")
    except:
        bot.send_message(message.from_user.id, "Неправильный IP адрес!")

def get_port(message):
    global port
    try:
        port = int(message.text)
        bot.send_message(message.from_user.id, "Порт введён правильно!")
    except:
        bot.send_message(message.from_user.id, "Неправильный порт!")

def get_login(message):
    global login
    try:
        login = str(message.text)
        bot.send_message(message.from_user.id, "Вы ввели логин!")
    except:
        bot.send_message(message.from_user.id, "Что-то не то Вы ввели!")

def get_password(message):
    global password
    try:
        password = str(message.text)
        bot.send_message(message.from_user.id, "Вы ввели пароль!")
    except:
        bot.send_message(message.from_user.id, "Что-то не то Вы ввели!")

def command(message):
    if test_perem(message) == 0:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(hostname=IP, username=login, password=password, port=port)
        except:
            bot.send_message(message.from_user.id, "Наш хост недоступен :(")
            return
        channel = client.invoke_shell()
        channel.send("enable\n")
        channel.send("cisco\n")
        time.sleep(1)
        channel.send("terminal length 0\n")
        time.sleep(1)
        channel.recv(60000)
        channel.send(str(message.text)+"\n")
        channel.settimeout(5)
        output = ""
        while True:
            try:
                part = channel.recv(60000).decode("cp866")
                output += part
                time.sleep(0.5)
            except socket.timeout:
                break
        bot.send_message(message.from_user.id, output)
        client.close()
    else:
        return

def test_perem(message):
    if IP is None:
        bot.send_message(message.from_user.id, "Вы не ввели IP адрес!")
        return 1
    elif login is None:
        bot.send_message(message.from_user.id, "Вы не ввели имя пользователя!")
        return 1
    elif port is None:
        bot.send_message(message.from_user.id, "Вы не ввели порт!")
        return 1
    elif password is None:
        bot.send_message(message.from_user.id, "Вы не ввели пароль!")
        return 1
    else:
        return 0

bot.polling(none_stop=True)