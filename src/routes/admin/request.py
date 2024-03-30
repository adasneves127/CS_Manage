from app import app
from flask import session
from src.utils.db_utils import connect
from src.utils.templates import send_template
from src.utils.exceptions import UserNotSignedInException


@app.route("/admin/user/requests/", methods=["GET"])
def get_user_requests():
    conn = connect()
    if "user" not in session:
        raise UserNotSignedInException()
    return send_template()
