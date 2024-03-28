from flask_liquid import render_template
from app import app
from flask import session
from src.utils.app_utils import load_app_info
from src.utils.db_utils import connect


def send_template(template: str, **kwargs):
    with app.app_context():
        app_info = load_app_info()["public"]
        user_data = {"theme": 1}

        if "loggedin" not in session:
            session["loggedin"] = False

        if "user" in session:
            session["user"] = connect().get_user_by_seq(session["user"].seq)
            session.permanent = True
            user_data = session["user"].__dict__

        return render_template(
            template,
            **app_info,
            **kwargs,
            isLoggedIn=session["loggedin"],
            **user_data
        )
