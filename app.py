from flask import Flask, send_from_directory, send_file, render_template
from flask_session import Session
from src.utils.app_utils import load_app_info
from flask_liquid import Liquid


app = Flask(__name__, template_folder='./interface/templates/', static_folder='./interface/static/')
liquid = Liquid(app)
app.config.update(
    SESSION_PERMANENT=False,
    SESSION_TYPE = "filesystem"
)

Session(app)

import src.routes.base_routes
import src.routes.auth


if __name__ == '__main__':
    app.run(debug=True)