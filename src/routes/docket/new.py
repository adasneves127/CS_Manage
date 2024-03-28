from app import app
from src.utils.templates import send_template
from src.utils.db_utils import connect
from flask import session, request, redirect
from src.utils import exceptions


@app.route("/docket/officer/new/", methods=["GET"])
def new_officer_docket():
    conn = connect()
    if "user" not in session:
        raise exceptions.UserNotSignedInException()
    user = session["user"]
    if not conn.can_user_view_officer_docket(user):
        return exceptions.InvalidPermissionException()

    return send_template("docket/new.liquid")


@app.route("/docket/officer/new/", methods=["POST"])
def create_officer_docket():
    conn = connect()
    if "user" not in session:
        raise exceptions.UserNotSignedInException()
    user = session["user"]
    if not conn.can_user_view_officer_docket(user):
        return exceptions.InvalidPermissionException()

    docket = request.form
    conn.create_officer_docket(docket, user)
    return redirect("/docket/officer/view/")
