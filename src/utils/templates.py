from flask_liquid import render_template
from app import app
from flask import session, request
from src.utils.app_utils import load_app_info
from src.utils.db_utils import db_connection
import time


def send_template(template: str, should_rl=True, **kwargs):
    with app.app_context():
        app_info = load_app_info()["public"]
        user_data = {"theme": 1}

        if "loggedin" not in session:
            session["loggedin"] = False

        if "user" in session:
            with db_connection() as conn:
                session["user"] = conn.get_user_by_seq(session["user"].seq)
                session.permanent = True
                user_data = session["user"].__dict__

            if request.method == 'POST' and should_rl:
                session['last_post'] = time.time()
            print(session)

        return render_template(
            template,
            **app_info,
            **kwargs,
            isLoggedIn=session["loggedin"],
            **user_data
        )
