from app import app
from src.utils.templates import send_template
import bcrypt
from flask import session, request, redirect
from src.utils.db_utils import connect

@app.route("/auth/login/", methods=["GET"])
def get_login_page():
    return send_template("login.liquid")

@app.route("/auth/login/", methods=["POST"])
def login():
    connection = connect()
    # Get the username and password from the form
    username = request.form['username']
    password = request.form['password']
    
    # Check if the user exists
    (valid, user_seq, user_id) = connection.check_user_valid(username, password)
    if valid:
        user = connection.get_user_by_seq(user_seq)
        if user.system_user:
            return "Invalid username or password", 400
        session["loggedin"] = True
        session['user'] = user
        # return redirect(redir, code=302)
        return redirect("/", code=302)
    else:
        login_error = "Invalid username or password"
        return login_error, 400

@app.route("/auth/logout/")
def logout():
    keys = list(session.keys())
    for key in keys:
        session.pop(key)
    return redirect("/" )
    

@app.route("/auth/password_reset/", methods=['POST'])
def reset_password():
    raise NotImplementedError