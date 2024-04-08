from src.utils.templates import send_template
from app import app
from flask import request, redirect, session
from src.utils.email_utils import send_bug_report
from src.utils.GH_api import create_feature_request
import html

@app.route("/about/", methods=["GET"])
def get_about_page():
    return send_template("about/about.liquid")


@app.route("/about/bug_report", methods=['GET'])
def send_report_form():
    return send_template("about/bug_report.liquid")

@app.route("/about/bug_report", methods=["POST"])
def send_report():
    send_bug_report(request.form, session["user"])
    return redirect("/about/bug_report")

@app.route("/about/feature", methods=['GET'])
def send_feature_form():
    return send_template("about/features.liquid")

@app.route("/about/feature", methods=['POST'])
def send_feature_request():
    title = html.escape(request.form.get('title'))
    description = html.escape(request.form.get('description'))
    user = html.escape(session.get('user'))
    create_feature_request(title, description, user)
    return redirect('/about/feature')

