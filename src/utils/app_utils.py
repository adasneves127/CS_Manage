from json import load, dump


def load_app_info() -> dict:
    return load(open("app_info.json", "r"))