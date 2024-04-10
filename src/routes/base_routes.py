from app import app
from flask import request, session, redirect, send_file
from src.utils.templates import send_template
from src.utils.email_utils import send_bug_report
import time


@app.route("/", methods=["GET"])
def get_root_index():
    return send_template("index.liquid")


@app.route("/robots.txt", methods=['GET'])
def send_robots():
    return send_file("interface/private/robots.txt")


@app.route('/favicon.ico', methods=['GET'])
def send_favicon():
    return send_file('interface/private/favicon.ico')


@app.before_request
def prevent_rapid_requests():
    if request.method == "POST":
        last_post = session.get('last_post', 0)
        if last_post >= time.time() - 10:
            raise TimeoutError


@app.route('/register/', methods=['GET'])
def get_current_event_link():
    with open('events.csv') as f:
        for line in f:
            link, start, end = line.split(',')
            if float(start) - 1800 < time.time() < float(end) + 1800:
                return redirect(link)
    return "No Event is Occurring... Please try again later."
