import math

import telebot
from telebot import types
from datetime import date
import psycopg2

token = "5936792294:AAFzGEIdZo3PffLKUzmP2K3FNi2Nm61b1VA"
bot = telebot.TeleBot(token, parse_mode="HTML")


connection = psycopg2.connect(
    dbname='telebot',
    user='postgres',
    password='Aat8912000!',
    host='localhost',
    port='5432'
)
cursor = connection.cursor()

start_training = date(2023, 1, 30)
current_date = date.today()
weekday = current_date.weekday()
delta = current_date - start_training
week = 0 if math.ceil(delta.days / 7) % 2 == 0 else 1
num_week = round(delta.days / 7)

weekday_dict = {0: 'понедельник', 1: 'вторник', 2: 'среда', 3: 'четверг', 4: 'пятница', 5: 'суббота',
                6: 'воскресенье'}


def get_subject(i, subject, room_numb, start_time, teacher):
    return f'{i}. <b>{subject}</b> | <i>{room_numb} Каб.</i> | {str(start_time)} | {teacher} \n'


def message_day_schedule(day, week_f=week):
    cursor.execute(
        """
        SELECT day, subject.name, room_numb, start_time, teacher.full_name, week
        FROM timetable
        INNER JOIN teacher
        ON teacher.subject = timetable.subject
        INNER JOIN subject
        ON subject.id = timetable.subject
        WHERE day = %s AND week = %s
        ORDER BY start_time ASC
        """, (day, week_f)
    )
    records = list(cursor.fetchall())
    res_str = f'{day.upper()}: \n' \
              '---------------------- \n'
    if records:
        for i in range(len(records)):
            res_str += get_subject(i + 1, records[i][1], records[i][2], records[i][3], records[i][4])
    else:
        res_str += 'Занятий нет!\n'
    res_str += '---------------------- \n'
    return res_str


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row("Сегодня", "Завтра")
    keyboard.row("Понедельник", "Вторник", "Среда")
    keyboard.row("Четверг", "Пятница", "Суббота")
    keyboard.row("Расписание на текущую неделю", "Расписание на следущую неделю", "Help")
    bot.send_message(message.chat.id, 'Привет хочешь узнать своё расписание? \n'
                                      'Чтобы узнать полный перечень команд введите /help',
                     reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id, 'Мой функционал:\n'
                                      '\n'
                                      '/start - запуск приложения\n'
                                      '/help - список команд\n'
                                      '/monday - расписание на понедельник\n'
                                      '/tuesday - расписание на вторник\n'
                                      '/wednesday - расписание на среду\n'
                                      '/thursday - расписание на четверг\n'
                                      '/friday - расписание на пятницу\n'
                                      '/satuday - расписание на субботу\n'
                                      '/nextweek - расписание на следующую неделю\n'
                                      '/thisweek - расписание на текущую неделю\n'
                                      '/today - расписание на сегодня\n'
                                      '/tomorrow - расписание на завтра\n'
                                      '/week - какая сейчас неделя\n'
                                      '/mtuci - ссылка на сайт МТУСИ\n')


@bot.message_handler(commands=['week'])
def message_num_week(message):
    bot.send_message(message.chat.id, f'Неделя: №{num_week}, {"чётная" if week == "ch" else "нечётная"}')


@bot.message_handler(commands=['mtuci'])
def message_mtuci_link(message):
    bot.send_message(message.chat.id, 'Официальный сайт МТУСИ - https://mtuci.ru/')


@bot.message_handler(commands=['today'])
def today_schedule(message):
    days = message_day_schedule(weekday_dict[weekday],)
    bot.send_message(message.chat.id, days)


@bot.message_handler(commands=['tomorrow'])
def tomorrow_schedule(message):
    days = message_day_schedule(weekday_dict[weekday + 1])
    bot.send_message(message.chat.id, days)


@bot.message_handler(commands=['currentweek'])
def current_week(message):
    res_str = f'Неделя: №{num_week}, {"чётная" if week == 0 else "нечётная"}\n'
    for i in range(6):
        res_str += message_day_schedule(weekday_dict[i], week)
    bot.send_message(message.chat.id, res_str)


@bot.message_handler(commands=['nextweek'])
def next_week(message):
    global week
    week = 1 if week == 0 else 0
    res_str = f'Неделя: №{num_week + 1}, {"нечётная" if week == 0 else "чётная"}\n'
    for i in range(6):
        res_str += message_day_schedule(weekday_dict[i], week)
    bot.send_message(message.chat.id, res_str)


@bot.message_handler(commands=['monday'])
def monday_schedule(message):
    days = message_day_schedule('понедельник', )
    bot.send_message(message.chat.id, days)


@bot.message_handler(commands=['tuesday'])
def tuesday_schedule(message):
    days = message_day_schedule('вторник', )
    bot.send_message(message.chat.id, days)


@bot.message_handler(commands=['wednesday'])
def wednesday_schedule(message):
    days = message_day_schedule('среда', )
    bot.send_message(message.chat.id, days)


@bot.message_handler(commands=['thursday'])
def thursday_schedule(message):
    days = message_day_schedule('четверг', )
    bot.send_message(message.chat.id, days)


@bot.message_handler(commands=['friday'])
def friday_schedule(message):
    days = message_day_schedule('пятница', )
    bot.send_message(message.chat.id, days)


@bot.message_handler(commands=['satuday'])
def satuday_schedule(message):
    days = message_day_schedule('суббота', )
    bot.send_message(message.chat.id, days)


@bot.message_handler(content_types=['text'])
def answer(message):
    if message.text.lower() == "help":
        start_message(message)
    elif message.text.lower() == "понедельник":
        monday_schedule(message)
    elif message.text.lower() == "вторник":
        tuesday_schedule(message)
    elif message.text.lower() == "среда":
        wednesday_schedule(message)
    elif message.text.lower() == "четверг":
        thursday_schedule(message)
    elif message.text.lower() == "пятница":
        friday_schedule(message)
    elif message.text.lower() == "суббота":
        satuday_schedule(message)
    elif message.text.lower() == "расписание на текущую неделю":
        current_week(message)
    elif message.text.lower() == "расписание на следущую неделю":
        next_week(message)
    elif message.text.lower() == "сегодня":
        today_schedule(message)
    elif message.text.lower() == "завтра":
        tomorrow_schedule(message)
    else:
        bot.send_message(message.chat.id, 'Извините, я вас не понимаю')


bot.polling(none_stop=True)
