from json import load
from contextlib import contextmanager
from src.utils.db_utils import connect

def load_app_info() -> dict:
    return load(open("app_info.json", "r"))

@contextmanager
def db_connection():
    connection = connect()
    try:
        yield connection
    finally:
        connection.close()