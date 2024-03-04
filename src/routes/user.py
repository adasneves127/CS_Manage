from app import app

from src.utils.templates import render_template
from flask import session, redirect
from src.utils.db_utils import connect

@app.route("/user/reload/", methods=["GET"])
def reload_user():
    connection = connect()
    session['user'] = connection.get_user_by_seq(session['user'].seq)
    return "", 200