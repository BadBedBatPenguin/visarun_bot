import os
import sqlite3
from datetime import datetime

# import requests

# from telegram import ReplyKeyboardMarkup
# from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from telegram.ext import CommandHandler, Updater
# from telegram.update import Update

from dotenv import load_dotenv

load_dotenv()

secret_token = os.getenv('TOKEN')

def save_new_user(username, first_name, last_name):
    '''Saves user username to database'''
    date = str(datetime.now())
    sql_command = 'INSERT INTO users VALUES (NULL, ?, ?, ?, ?);'
    cursor.execute(sql_command, (username, first_name, last_name, date))
    connection.commit()
    if cursor.rowcount < 1:
        print(f'Что-то пошло не так, пользователь {username} '
              'не сохранен в базе')
    else:
        print(f'Пользователь {username} успешно сохранен в базе')


def wake_up(update, context):
    '''Saves new user to database and welcomes him'''
    chat = update.effective_chat
    first_name = chat.first_name
    save_new_user(
        username=chat.username,
        first_name=first_name,
        last_name=chat.last_name,
    )
    # button = ReplyKeyboardMarkup([['/newcat', '/newdog']], resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat.id,
        text=f'Приветcтвуем тебя, {first_name}.',
        # reply_markup=button,
    )

    # context.bot.send_photo(chat.id, get_new_pictre('cat'))


def main():
    '''Implementing main logic'''
    # print("Initializing Database...")
    # # Connect to local database
    # db_name = 'database.db' # Insert the database name. Database is the folder
    # connection = sqlite3.connect(db_name, check_same_thread=False)
    # cursor = connection.cursor()
    # print("Connected to the database")

    # sql_command = """CREATE TABLE IF NOT EXISTS users (
    #     id INTEGER PRIMARY KEY AUTOINCREMENT, 
    #     username VARCHAR(200),
    #     first_name VARCHAR(200),
    #     last_name VARCHAR(200),
    #     date VARCHAR(100));"""
    # cursor.execute(sql_command)
    # print("All tables are ready")
    updater = Updater(token=secret_token, use_context=True)
    commands = [
        ['start', wake_up],
        # ['newcat', new_cat],
        # ['newdog', new_dog],
    ]
    for command, func in commands:
        updater.dispatcher.add_handler(CommandHandler(command, func))
    # updater.dispatcher.add_handler(MessageHandler(Filters.text, answer))

    print("Bot Started")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    try:
        print("Initializing Database...")
        # Connect to local database
        DB_NAME = 'database.db' # Insert the database name. Database is the folder
        connection = sqlite3.connect(DB_NAME, check_same_thread=False)
        cursor = connection.cursor()
        print("Connected to the database")

        SQL_COMMAND = """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            username VARCHAR(200),
            first_name VARCHAR(200),
            last_name VARCHAR(200),
            date VARCHAR(100));"""
        cursor.execute(SQL_COMMAND)
        print("All tables are ready")
        main()

    except Exception as error:
        print(f'Cause: {error}')
