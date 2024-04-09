from app import app
from src.utils.templates import send_template
from flask import session, request, redirect
from src.utils import exceptions
from src.utils import email_utils
from src.utils.app_utils import load_app_info
from src.utils.db_utils import db_connection


@app.route("/auth/login/", methods=["GET"])
def get_login_page():
    return send_template("login.liquid")


@app.route("/auth/login/", methods=["POST"])
def login():
    with db_connection() as connection:
        
        # Get the username and password from the form
        username = request.form["username"]
        password = request.form["password"]

        # Check if the user exists
        (valid, user_seq, _) = connection.check_user_valid(username, password)
        if valid:
            user = connection.get_user_by_seq(user_seq)
            if user.system_user:
                raise exceptions.UserNotFoundException()
            session["loggedin"] = True
            session["user"] = user
            # return redirect(redir, code=302)
            return redirect(session.get("ref", "/"), code=302)
        else:
            login_error = "Invalid username or password"
            return login_error, 400


@app.route("/auth/logout/")
def logout():
    session.clear()
    return redirect("/", code=302)


@app.route("/reset_password/<token>", methods=["GET"])
def reset_password_page(token):
    with db_connection() as conn:
        user = conn.get_user_by_reset_token(token)
        if user:
            # deepcode ignore XSS: <please specify a reason of ignoring this>
            return send_template("user/reset_password.liquid", token=token)
        else:
            raise exceptions.MalformedRequestException()


@app.route("/reset_password/<token>", methods=["POST"])
def reset_password_form(token):
    with db_connection() as conn:
        user = conn.get_user_by_reset_token(token)
        if user:
            password = request.form["password"]
            conn.reset_password(user[0], password)
            session.clear()
            return redirect("/")
        else:
            return "Invalid token", 400


@app.route("/auth/password_reset/", methods=["POST"])
def reset_password():
    with db_connection() as conn:
        user_name = request.json["username"]
        user = conn.get_user_by_user_name(user_name)
        app_domain = load_app_info()["public"]["application_url"]
        if user:
            # Get the user's IP address
            ip = request.remote_addr
            user_seq = user.seq
            key = conn.request_reset_password(user_seq, ip)
            email_utils.send_password_reset_email(
                user, f"http://{app_domain}/reset_password/{key}"
            )
            return_msg = "Password reset email sent to your email."
            return_msg += "Please check for a link."
            return (
                return_msg, 201
            )
        return "Invalid username", 400


@app.route("/auth/request/", methods=["GET"])
def request_access():
    return send_template("user/request.liquid")


@app.route("/auth/request/", methods=["POST"])
def request_access_form_submit():
    form_data = request.form
    with db_connection() as conn:
        conn.save_user_request(form_data)
        return redirect("/")
