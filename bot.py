import logging
import aiogram
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import sqlite3
from aiogram.dispatcher.webhook import SendMessage
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
import json
import datetime

from bot_token import bot_token

#http://t.me/liceum_schedule_bot
bot = Bot(bot_token)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

WEBHOOK_PORT = 5000
WEBHOOK_HOST = "127.0.0.1"
WEBHOOK_URL = 'https://688b-46-73-138-171.ngrok.io'
WEBHOOK_PATH = ''
WEBAPP_PORT = 5000

grade = 0
letter = ''
group = 0
full_class = ''
lessons = []
command = ''


db = sqlite3.connect('bot.db')
sql = db.cursor()
sql.execute("""CREATE TABLE IF NOT EXISTS users_data (
    id INT,
    class   TEXT)
    """)

#------------------START--------
@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    global command
    command = 'start'
    await bot.send_message(message.chat.id, 'Привет, лицеист')
    create_grade_buttons()
    await bot.send_message(message.chat.id, 'Сейчас от тебя требуется выбрать класс, в котором ты учишься')
    await bot.send_message(message.chat.id, 'Выбери класс', reply_markup=grade_buttons)


#------------------RESET_CLASS---------
@dp.message_handler(commands=['reset_grade'])
async def reset_grade(message: types.Message):
    global command
    command = 'reset_grade'
    create_grade_buttons()
    await bot.send_message(message.chat.id, 'Выбери класс', reply_markup=grade_buttons)

#------------------ONE_DAY_LESSONS--------
@dp.message_handler(commands=['one_day_lessons'])
async def one_day_lessons(message: types.Message):
    global grade_buttons, command
    command = 'one_day_lessons'
    create_grade_buttons()
    await bot.send_message(message.chat.id, 'Выбери класс', reply_markup=grade_buttons)


#--------------------ALL_WEEK_LESSONS-----------------

@dp.message_handler(commands=['all_week_lessons'])
async def schedule(message: types.Message):
    global grade_buttons, command
    command = 'all_week_lessons'
    create_grade_buttons()
    await bot.send_message(message.chat.id, 'Выбери класс', reply_markup=grade_buttons)


#------------------TODAY_LESSONS--------
@dp.message_handler(commands=['today_lessons'])
async def today_lessons(message: types.Message):
    global lessons
    today = datetime.datetime.today()
    weekday = today.weekday()

    rows_id = sql.execute('''SELECT id FROM users_data''').fetchall()
    rows_idnew = []
    for i in rows_id:
        rows_idnew.append(i[0])

    rows_class = sql.execute('''SELECT class FROM users_data''').fetchall()
    rows_classnew = []
    for i in rows_class:
        rows_classnew.append(i[0])

    for i in range(len(rows_idnew)):
        if rows_idnew[i] == message.chat.id:
            my_class = rows_classnew[i]

    if weekday == 0:
        weekday = 'Понедельник'
    elif weekday == 1:
        weekday = 'Вторник'
    elif weekday == 2:
        weekday = 'Среда'
    elif weekday == 3:
        weekday = 'Четверг'
    elif weekday == 4:
        weekday = 'Пятница'
    elif weekday == 5:
        weekday = 'Суббота'
    elif weekday == 6:
        await bot.send_message(message.chat.id, 'Сегодня уроков нет, отдыхаем')
    if weekday != 6:
        open_schedule(my_class, weekday)
        await bot.send_message(message.chat.id, lessons[0])
    lessons = []

@dp.message_handler(commands=['my_week_lessons'])
async def my_week_lessons(message: types.Message):
    global lessons
    rows_id = sql.execute('''SELECT id FROM users_data''').fetchall()
    rows_idnew = []
    for i in rows_id:
        rows_idnew.append(i[0])

    rows_class = sql.execute('''SELECT class FROM users_data''').fetchall()
    rows_classnew = []
    for i in rows_class:
        rows_classnew.append(i[0])

    for i in range(len(rows_idnew)):
        if rows_idnew[i] == message.chat.id:
            my_class = rows_classnew[i]
    open_schedule(my_class)
    for i in lessons:
        await bot.send_message(message.chat.id, i)
    lessons = []

#-------------------MY_DAY_LESSONS
@dp.message_handler(commands=['my_day_lessons'])
async def my_day_lessons(message: types.Message):
    global full_class
    rows_id = sql.execute('''SELECT id FROM users_data''').fetchall()
    rows_idnew = []
    for i in rows_id:
        rows_idnew.append(i[0])

    rows_class = sql.execute('''SELECT class FROM users_data''').fetchall()
    rows_classnew = []
    for i in rows_class:
        rows_classnew.append(i[0])

    for i in range(len(rows_idnew)):
        if rows_idnew[i] == message.chat.id:
            full_class = rows_classnew[i]
    create_days_button()
    await bot.send_message(message.chat.id, 'Выбери день недели', reply_markup=days_buttons)

#----------------INFO---------
@dp.message_handler(commands=['info'])
async def send_info(message: types.Message):
    await bot.send_message(message.chat.id, 'Что умеет наш бот?\n/today_lessons - твоё расписание на сегодня\n/my_week_lessons - твоё расписание на неделю\n/my_day_lessons - твоё расписание на какай-нибудь день недели\n/all_week_lessons - расписание на неделю любого класса\n/one_day_lessons - расписание на какой-нибудь любого класса\n/reset_grade - если ты перешёл в новый класс, воспользуйся этой командой')

@dp.message_handler()
async def echo(message: types.Message):
    #print(message)
    global letter_buttons, grade, letter, group, full_class, lessons, command, days_buttons
    if message.text == '8':
        create_letter_button(8)
        grade = 8
        await bot.send_message(message.chat.id, 'Выбери букву класса', reply_markup=letter_buttons)
    if message.text == '9':
        create_letter_button(9)
        grade = 9
        await bot.send_message(message.chat.id, 'Выбери букву класса', reply_markup=letter_buttons)
    if message.text == '10' :
        create_letter_button(10)
        grade = 10
        await bot.send_message(message.chat.id, 'Выбери букву класса', reply_markup=letter_buttons)
    if message.text == '11':
        create_letter_button(11)
        grade = 11
        await bot.send_message(message.chat.id, 'Выбери букву класса', reply_markup=letter_buttons)

    if message.text == 'А':
        letter = 'А'
        create_group_buttons()
        await bot.send_message(message.chat.id, 'Выбери группу', reply_markup=group_buttons)
    if message.text == 'Б':
        letter = 'Б'
        create_group_buttons()
        await bot.send_message(message.chat.id, 'Выбери группу', reply_markup=group_buttons)
    if message.text == 'В':
        letter = 'В'
        create_group_buttons()
        await bot.send_message(message.chat.id, 'Выбери группу', reply_markup=group_buttons)
    if message.text == 'Г':
        letter = 'Г'
        create_group_buttons()
        await bot.send_message(message.chat.id, 'Выбери группу', reply_markup=group_buttons)
    if message.text == 'И':
        letter = 'И'
        create_group_buttons()
        await bot.send_message(message.chat.id, 'Выбери группу', reply_markup=group_buttons)

    if message.text == '1':
        group = 1
        full_class = f'{grade}{letter}{group}'
        if command == 'all_week_lessons':
            open_schedule(full_class)
            for i in lessons:
                await bot.send_message(message.chat.id, i)

        elif command == 'one_day_lessons':
            create_days_button()
            await bot.send_message(message.chat.id, 'Выбери день недели', reply_markup=days_buttons)
        elif command == 'start':
            insert_id(message.chat.id, full_class)
            await bot.send_message(message.chat.id, f'Ты учишься в {full_class} классе')
        elif command == 'reset_grade':
            reset_class(message.chat.id, full_class)
            await bot.send_message(message.chat.id, f'Теперь ты учишься в {full_class} классе')

    if message.text == '2':
        group = 2
        full_class = f'{grade}{letter}{group}'
        if command == 'all_week_lessons':
            open_schedule(full_class)
            await bot.send_message(message.chat.id, f'Ты видишь расписани {full_class} класса')
            for i in lessons:
                await bot.send_message(message.chat.id, i)
        elif command == 'one_day_lessons':
            create_days_button()
            await bot.send_message(message.chat.id, 'Выбери день недели', reply_markup=days_buttons)
        elif command == 'start':
            insert_id(message.chat.id, full_class)
            await bot.send_message(message.chat.id, f'Ты учишься в {full_class} классе')
        elif command == 'reset_grade':
            reset_class(message.chat.id, full_class)
            await bot.send_message(message.chat.id, f'Теперь ты учишься в {full_class} классе')

    if message.text == 'Monday':
        open_schedule(full_class, 'Понедельник')
        await bot.send_message(message.chat.id, f'Ты видишь расписани {full_class} класса на понедельник')
        await bot.send_message(message.chat.id, lessons[0])
    if message.text == 'Tuesday':
        open_schedule(full_class, 'Вторник')
        await bot.send_message(message.chat.id, f'Ты видишь расписани {full_class} класса на вторник')
        await bot.send_message(message.chat.id, lessons[0])
    if message.text == 'Wednesday':
        open_schedule(full_class, 'Среда')
        await bot.send_message(message.chat.id, f'Ты видишь расписани {full_class} класса на среду')
        await bot.send_message(message.chat.id, lessons[0])
    if message.text == 'Thursday':
        open_schedule(full_class, 'Четверг')
        await bot.send_message(message.chat.id, f'Ты видишь расписани {full_class} класса на четверг')
        await bot.send_message(message.chat.id, lessons[0])
    if message.text == 'Friday':
        open_schedule(full_class, 'Пятница')
        await bot.send_message(message.chat.id, f'Ты видишь расписани {full_class} класса на пятницу')
        await bot.send_message(message.chat.id, lessons[0])
    if message.text == 'Saturday':
        open_schedule(full_class, 'Суббота')
        await bot.send_message(message.chat.id, f'Ты видишь расписани {full_class} класса на субботу')
        await bot.send_message(message.chat.id, lessons[0])
    lessons = []

#кнопки с выбором класса
def create_grade_buttons():
    global grade_buttons
    grade_buttons = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button8 = KeyboardButton(text='8')
    button9 = KeyboardButton(text='9')
    button10 = KeyboardButton(text='10')
    button11 = KeyboardButton(text='11')
    grade_buttons.row(button8, button9)
    grade_buttons.row(button10, button11)


#нопки с буквами
def create_letter_button(grade):
    global letter_buttons
    letter_buttons = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    but1 = KeyboardButton(text="А")
    but2 = KeyboardButton(text='Б')
    but3 = KeyboardButton(text='В')
    but4 = KeyboardButton(text='Г')
    but5 = KeyboardButton(text='И')
    if grade == 8:
        letter_buttons.add(but1, but2, but3)
    elif grade == 9:
        letter_buttons.row(but1, but2)
        letter_buttons.row(but3, but4)
    elif grade == 10 or grade == 11:
        letter_buttons.add(but1, but2, but3, but4, but5)
    return letter_buttons

def create_group_buttons():
    global group_buttons
    group_buttons = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    first_gr = KeyboardButton(text='1')
    second_gr = KeyboardButton(text='2')
    group_buttons.add(first_gr, second_gr)
    return group_buttons

def create_days_button():
    global days_buttons
    days_buttons = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    Monday = KeyboardButton(text='Monday')
    Tuesday = KeyboardButton(text='Tuesday')
    Wednesday = KeyboardButton(text='Wednesday')
    Thursday = KeyboardButton(text='Thursday')
    Friday = KeyboardButton(text='Friday')
    Saturday = KeyboardButton(text='Saturday')
    days_buttons.add(Monday, Tuesday, Wednesday, Thursday, Friday, Saturday)
    return days_buttons

#вытаскивание информации
def open_schedule(key, day=None):
    with open('data/json/schedule2.json' ,'r') as f:
        a = json.load(f)

    rows_id = sql.execute('''SELECT * FROM users_data''').fetchall()
    print(rows_id)
    if day == None:
        day_ = 0
        for i in a[key]:
            lessons.append(i)
            lessons[day_] += '\n'

            for j in a[key][i]:
                if type(a[key][i][j]["Предмет"]) != float or type(a[key][i][j]["Кабинет"]) != float:
                    if (len(a[key][i][j]["Кабинет"]) > 5):
                        str = f'{a[key][i][j]["Время"]}  {a[key][i][j]["Предмет"]}  {a[key][i][j]["Кабинет"][:3]}/{a[key][i][j]["Кабинет"][-3:]}'
                    else:
                        str = f'{a[key][i][j]["Время"]}  {a[key][i][j]["Предмет"]}  {a[key][i][j]["Кабинет"]}'
                    lessons[day_] += str
                    lessons[day_] += '\n'
            day_ += 1
    else:
        lessons.append(day)
        lessons[0] += '\n'
        print(a[key][day])
        for i in a[key][day]:
            if type(a[key][day][i]["Предмет"]) != float or type(a[key][day][i]["Кабинет"]) != float:
                if (len(a[key][day][i]["Кабинет"]) > 5):
                    str = f'{a[key][day][i]["Время"]}  {a[key][day][i]["Предмет"]}  {a[key][day][i]["Кабинет"][:3]}/{a[key][day][i]["Кабинет"][-3:]}'
                else:
                    str = f'{a[key][day][i]["Время"]}  {a[key][day][i]["Предмет"]}  {a[key][day][i]["Кабинет"]}'
                lessons[0] += str
                lessons[0] += '\n'
    print(lessons)
    return lessons


#add id in database
def insert_id(id, grade):
    rows_id = sql.execute('''SELECT id FROM users_data''').fetchall()
    rows_idnew = []
    for i in rows_id:
        rows_idnew.append(i[0])
    if id not in rows_idnew:
        sql.execute(f"""INSERT INTO users_data(id, class) VALUES (?, ?)""", (id, grade))
    db.commit()

#reset class in db
def reset_class(id, grade):
    sql.execute(f'''UPDATE users_data SET class = ? WHERE id = ?''', (grade, id))
    db.commit()


#------------------webhook------------------------------------------------------------------------

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dp):
    logging.warning('Shutting down..')

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')

if __name__ == '__main__':
    executor.start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBHOOK_HOST,
        port=WEBAPP_PORT,
    )