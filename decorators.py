import sqlite3
from visarun_bot import DB_NAME


def query(func):
    def connect(*args, **kwargs):
        connection = sqlite3.connect(DB_NAME, check_same_thread=False)
        cursor = connection.cursor()
        result = func(*args, **kwargs)
        cursor.execute(result)
        connection.commit()
        connection.close()
        return result
    return connect
