from src.utils.db_utils import db_connection
from flask import session
from src.utils.templates import send_template
from app import app
from src.utils import exceptions


@app.route("/finances/", methods=["GET"])
def finance():
    with db_connection() as connection:
        if "user" not in session:
            raise exceptions.UserNotSignedInException()

        if connection.can_user_view_finances(session["user"].seq):
            statuses = connection.get_all_finance_status_names()
            return send_template(
                "finances/index.liquid", statuses=statuses,
                types=connection.get_all_types()
            )
        else:
            raise exceptions.InvalidPermissionException()


@app.route("/finances/pending/", methods=["GET"])
def pending():
    with db_connection() as connection:
        if "user" not in session:
            raise exceptions.UserNotSignedInException()

        if connection.can_user_view_finances(session["user"].seq):
            return send_template("finances/pending.liquid")
        else:
            raise exceptions.InvalidPermissionException()
