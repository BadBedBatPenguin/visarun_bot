import os
import sqlite3
from datetime import datetime
from typing import List, Tuple

# import requests

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
# from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from telegram.ext import CommandHandler, Updater, CallbackQueryHandler
# from telegram.update import Update
# from decorators import query

from dotenv import load_dotenv

load_dotenv()

secret_token = os.getenv('TOKEN')
DB_NAME = 'database.db'


connection = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = connection.cursor()


# @query
def create_tables_if_not_exist():
    '''Creates db if it doesn't exist already.'''
    create_users = """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(200),
        first_name VARCHAR(200),
        last_name VARCHAR(200),
        date INTEGER);"""
    create_visaruns = """CREATE TABLE IF NOT EXISTS visaruns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date INTEGER,
        city VARCHAR(200),
        type VARCHAR(100),
        available_places INTEGER,
        comment TEXT);"""
    create_registration = """CREATE TABLE IF NOT EXISTS registration (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        users INTEGER REFERENCES users(id),
        visaruns INTEGER REFERENCES visaruns(id));"""
    cursor.execute(create_users)
    cursor.execute(create_visaruns)
    cursor.execute(create_registration)
    connection.commit()


# @query
def save_new_user(username: str, first_name: str, last_name: str) -> None:
    '''Saves user username to database'''
    sql_command = '''
    INSERT INTO users
    VALUES (NULL, ?, ?, ?, strftime("%s", "now"));
    '''
    cursor.execute(sql_command, (username, first_name, last_name))
    connection.commit()
    if cursor.rowcount < 1:
        print(f'Что-то пошло не так, пользователь {username} '
              'не сохранен в базе')
    else:
        print(f'Пользователь {username} успешно сохранен в базе')


def get_user_id(username: str) -> str:
    '''Gets user data from database'''
    sql_command = f'SELECT id FROM users WHERE username = "{username}"'
    cursor.execute(sql_command)
    user = cursor.fetchall()
    if not user:
        print('Пользователь не найден.')
        return None
    return user[0][0]


# print(get_user_id('macass'))


def save_new_visarun(
    date: datetime,
    city: str,
    type: str,
    available_places: int,
    comment: str = None,
) -> None:
    '''Saves new visarun to database'''
    if date < datetime.now():
        print('Нельзя создавать визараны в прошлом')
        return
    sql_command = 'INSERT INTO visaruns VALUES (NULL, ?, ?, ?, ?, ?);'
    cursor.execute(sql_command, (
        int(datetime.timestamp(date)),
        city,
        type,
        available_places,
        comment
    ))
    connection.commit()
    if cursor.rowcount < 1:
        print(f'Что-то пошло не так, визаран в {city} '
              'не сохранен в базе')
    else:
        print(f'Визаран в {city} успешно сохранен в базе')


# save_new_visarun(datetime(2012, 12, 17), 'Test', 'test', 666)


# @query
def get_nearest_visaruns() -> List:
    '''Returns id of nearest visarun in future'''
    cursor.execute(
        '''SELECT city, date, type
        FROM visaruns
        WHERE date > strftime("%s", "now")
        ORDER BY date;'''
    )
    return cursor.fetchall()


# print(get_nearest_visaruns())


def get_visarun_id(city: str, date: int) -> int:
    '''Returns id of specified visarun.'''
    sql_command = f'''
        SELECT id
        FROM visaruns
        WHERE city = "{city}" AND date = {date}
    '''
    cursor.execute(sql_command)
    visarun = cursor.fetchall()
    if not visarun:
        print('Визаран не найден.')
        return None
    return visarun[0][0]


# print(get_visarun_id('Belgrade', 1672354800))


# @query
def register(user_id: int, visarun_id: int) -> None:
    '''Creates registration for nearest visarun'''
    sql_command = 'INSERT INTO registration VALUES (NULL, ?, ?);'
    cursor.execute(sql_command, (user_id, visarun_id))
    connection.commit()
    if cursor.rowcount < 1:
        print('Что-то пошло не так, регистрация не произведена.')
    else:
        print('Регистрация прошла успешно.')


# register(1, 2)


# @query
def cancel(user_id: int, visarun_id: int) -> None:
    '''Cancels registration for nearest visarun'''
    sql_command = f'''
        DELETE FROM registration
        WHERE users = {user_id} AND visaruns = {visarun_id};
    '''
    cursor.execute(sql_command)
    connection.commit()
    if cursor.rowcount < 1:
        print('Что-то пошло не так, отмена регистрации не произведена.')
    else:
        print('Отмена регистрации прошла успешно.')


# cancel(2, 2)


def register_user(update, context):
    '''Sends message with inline buttons attached.'''
    visaruns = get_nearest_visaruns()
    # print(visaruns)
    keyboard = [[InlineKeyboardButton(
        f'Визаран в {visarun[0]} {datetime.fromtimestamp(visarun[1])},\nтип: {visarun[2]}',
        callback_data=f'{visarun[0]} {visarun[1]} {visarun[2]}'
    )] for visarun in visaruns]
    # keyboard = [
    #     [
    #         InlineKeyboardButton('Option1', callback_data='1'),
    #         InlineKeyboardButton('Option2', callback_data='2'),
    #     ],
    #     [
    #         InlineKeyboardButton('Option3', callback_data='3'),
    #         InlineKeyboardButton('Option4', callback_data='4'),
    #     ],
    # ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def button(update, context):
    '''Parses the CallbackQuery and updates the message text.'''
    query = update.callback_query
    user_id = get_user_id(update.effective_chat.username)
    visarun_city = query.data.split()[0]
    visarun_date = int(query.data.split()[1])
    visarun_id = get_visarun_id(visarun_city, visarun_date)
    register(user_id, visarun_id)
    query.answer(text='Регистрация успешна')
    query.edit_message_text(
        text=f"Вы зарегистрированы на визаран в {visarun_city} на {datetime.fromtimestamp(visarun_date)}")

    # chat = update.effectivechat
    # nearest_visaruns = get_nearest_visaruns()
    # button = ReplyKeyboardMarkup(
    #   [[f'', '/cancel', '/call_for_help']],
    #   resize_keyboard=True
    # )


def wake_up(update, context):
    '''Saves new user to database and welcomes him'''
    chat = update.effective_chat
    first_name = chat.first_name
    save_new_user(
        username=chat.username,
        first_name=first_name,
        last_name=chat.last_name,
    )
    # button = ReplyKeyboardMarkup(
    #   [['/register', '/cancel', '/call_for_help']],
    #   resize_keyboard=True
    # )

    context.bot.send_message(
        chat_id=chat.id,
        text=f'Приветcтвуем тебя, {first_name}.',
        # reply_markup=button,
    )


def main():
    '''Implementing main logic'''
    updater = Updater(token=secret_token, use_context=True)
    commands = [
        ['start', wake_up],
        ['register', register_user],
        # ['newdog', new_dog],
    ]
    for command, func in commands:
        updater.dispatcher.add_handler(CommandHandler(command, func))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    # updater.dispatcher.add_handler(MessageHandler(Filters.text, answer))

    print("Bot Started")
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    try:
        create_tables_if_not_exist()
        main()
        connection.close()
    except Exception as error:
        print(f'Cause: {error}')
