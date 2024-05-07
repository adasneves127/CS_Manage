from json import load


def load_app_info() -> dict:
    try:
        return load(open("app_info.json", "r"))
    except FileNotFoundError:
        return {
            "public": {
                "email_domain": "example.com"
            }
        }
