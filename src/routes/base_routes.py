from app import app
from flask import request, session, redirect
from src.utils.app_utils import load_app_info
from src.utils.templates import send_template
from src.utils.email_utils import send_bug_report

@app.route("/", methods=["GET"])
def get_root_index():
    return send_template("navbar.liquid")


@app.route("/about/", methods=['GET'])
def get_about_page():
    return send_template("about.liquid")

@app.route("/about/bug_report", methods=['POST'])
def send_report():
    send_bug_report(request.form, session['user'])
    return redirect("/about/")