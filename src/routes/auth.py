from app import app
from src.utils.templates import send_template


@app.route("/auth/login/", methods=["GET"])
def get_login_page():
    return send_template("login.liquid", theme=1, isUserAdmin=True)

@app.route("/auth/password_reset/", methods=['POST'])
def reset_password():
    raise NotImplementedError