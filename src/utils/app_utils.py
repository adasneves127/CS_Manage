from json import load
from contextlib import contextmanager


def load_app_info() -> dict:
    return load(open("app_info.json", "r"))
