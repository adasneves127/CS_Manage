from json import load


def load_app_info() -> dict:
    return load(open("app_info.json", "r"))
