from src.utils.db_utils import connect
from flask import session
from src.utils.templates import send_template
from app import app

@app.route("/finances/", methods=["GET"])
def finance():
    connection = connect()
    if connection.can_user_view_finances(session['user'].seq):
        statuses = connection.get_all_statuses()
        return send_template("finances/index.liquid", statuses=statuses,
                             types=connection.get_all_types())
    else:
        return "You do not have permission to view this page", 403
    
@app.route("/finances/pending/", methods=["GET"])
def pending():
    connection = connect()
    if connection.can_user_view_finances(session['user'].seq):
        return send_template("finances/pending.liquid")
    else:
        return "You do not have permission to view this page", 403