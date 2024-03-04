from app import app
from flask import send_file
from src.utils.app_utils import load_app_info
from src.utils.templates import send_template

@app.route("/", methods=["GET"])
def get_root_index():
    return send_template("navbar.liquid")


@app.route("/about/", methods=['GET'])
def get_about_page():
    return send_template("about.liquid")