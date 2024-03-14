from flask import Flask
from flask_session import Session
from src.utils.app_utils import load_app_info
from flask_liquid import Liquid
import datetime

app = Flask(__name__, template_folder='./interface/templates/',
            static_folder='./interface/static/')
liquid = Liquid(app)
app.config.update(
    SESSION_PERMANENT=False,
    SESSION_TYPE="filesystem"
)

app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=1)


Session(app)
app.secret_key = load_app_info()['private']['secret_token']

from src.routes import docket, user, auth, finances, base_routes, admin, exception_handler


if __name__ == '__main__':
    app.run(debug=True)
