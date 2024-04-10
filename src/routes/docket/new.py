from app import app
from src.utils.templates import send_template
from src.utils.db_utils import db_connection
from flask import session, request, redirect, abort
from src.utils import exceptions


@app.route("/docket/officer/new/", methods=["GET"])
def new_officer_docket():
    with db_connection() as conn:
        if "user" not in session:
            raise exceptions.UserNotSignedInException()
        user = session["user"]
        if not conn.can_user_view_officer_docket(user):
            return exceptions.InvalidPermissionException()

        return send_template("docket/new.liquid")


@app.route("/docket/officer/new/", methods=["POST"])
def create_officer_docket():
    with db_connection() as conn:
        if "user" not in session:
            raise exceptions.UserNotSignedInException()
        user = session["user"]
        if not conn.can_user_view_officer_docket(user):
            return exceptions.InvalidPermissionException()

        docket = request.form
        conn.create_officer_docket(docket, user)
        return redirect("/docket/officer/view/")


@app.route("/docket/conversation/add/<int:seq>", methods=['POST'])
def create_docket_conversation(seq: int):
    with db_connection() as conn:
        user = session['user']
        if conn.can_user_view_officer_docket(user):
            try:
                conn.create_docket_conversation(seq, request.json, user)
            except Exception:
                abort(500)
    return ""
