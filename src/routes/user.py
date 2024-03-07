from app import app
from flask import abort
from src.utils.templates import send_template
from flask import session, redirect, request
from src.utils.db_utils import connect
from src.utils import exceptions

@app.route("/user/reload/", methods=["GET"])
def reload_user():
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    connection = connect()
    session['user'] = connection.get_user_by_seq(session['user'].seq)
    return "", 200

@app.route("/user/settings/")
def user_settings():
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    return send_template("user/settings.liquid")


@app.route('/user/change_password', methods=["POST"])
def change_password():
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    target_seq = request.args.get("seq", -1)
    if target_seq == -1:
        return send_template("user/settings.liquid", error="Current Password not correct"), 400
    
    else:
        connection = connect()
        user_valid = connection.check_user_valid(session['user'].user_name, 
                                    request.form.get("old_password", ""))
        if not user_valid[0]:
            return send_template("user/settings.liquid", error="Current Password not correct"), 400
        
        user = connection.get_user_by_seq(user_valid[1])
        if user is None:
            return send_template("user/settings.liquid", error="User not found"), 404
        else:
            new_password = request.form.get("new_password", "")
            if new_password == "":
                return send_template("user/settings.liquid", error="Internal Server Error"), 500
            else:
                connection.change_password(target_seq, session['user'], new_password)
                reload_user()
                return redirect("/user/settings/")


@app.route("/user/preferences", methods=["POST"])
def change_preferences():
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    target_seq = request.args.get("seq", -1)
    if target_seq == -1:
        return send_template("user/settings.liquid", error="Internal Server Error"), 500
    else:
        connection = connect()
        user = session['user']
        if user is None:
            return send_template("user/settings.liquid", error="User not found"), 404
        else:
            print(dict(request.form))
            connection.change_preferences(target_seq, user, request.form)
            reload_user()
            return redirect("/user/settings/")

@app.route("/user/change_approver_pin", methods=["POST"])
def change_approver_pin():
    if 'user' not in session:
        raise exceptions.UserNotSignedInException()
    seq = request.args.get("seq", -1)
    if seq == -1:
        return send_template("user/settings.liquid", error="Internal Server Error"), 500
    else:
        connection = connect()
        user = connection.get_user_by_seq(seq)
        if user is None:
            return send_template("user/settings.liquid", error="User not found"), 404
        else:
            connection.change_approver_pin(user, seq, request.form.get("new_pin", ""))
            reload_user()
            return redirect("/user/settings/")